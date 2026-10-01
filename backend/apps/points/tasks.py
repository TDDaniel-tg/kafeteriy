from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.settings_platform.models import PlatformSetting
from apps.comms.models import Notification
from apps.audit.services import log_audit_event
from .models import PointLot, PointAccount, PointTransaction
from .services import PointService

User = get_user_model()

@shared_task
def check_expiring_lots_and_notify():
    now = timezone.now()
    notification_days = PlatformSetting.get_setting('notification_expiring_days', [30, 7])

    # 1. Send warning notifications before expiration (e.g. 30 days and 7 days)
    for days in notification_days:
        target_start = now + timedelta(days=days - 1)
        target_end = now + timedelta(days=days)
        lots = PointLot.objects.filter(
            lot_type='burnable',
            current_balance__gt=0,
            is_expired=False,
            expires_at__gte=target_start,
            expires_at__lte=target_end
        )
        for lot in lots:
            Notification.objects.create(
                user=lot.user,
                title="Баллы скоро сгорят",
                message=f"У вас есть {lot.current_balance} б., которые действуют до {lot.expires_at.strftime('%d.%m.%Y')}. Успейте выбрать льготу!",
                notification_type='warning'
            )

    # 2. Process actually expired lots
    expired_lots = PointLot.objects.filter(
        lot_type='burnable',
        current_balance__gt=0,
        is_expired=False,
        expires_at__lte=now
    )
    for lot in expired_lots:
        burn_amount = lot.current_balance
        lot.current_balance = 0
        lot.is_expired = True
        lot.save(update_fields=['current_balance', 'is_expired'])

        account = PointAccount.objects.get_or_create(user=lot.user)[0]
        account.total_balance = max(0, account.total_balance - burn_amount)
        account.save(update_fields=['total_balance'])

        PointTransaction.objects.create(
            account=account,
            transaction_type='expire',
            amount=-burn_amount,
            balance_after=account.total_balance,
            idempotency_key=f"expire-lot-{lot.id}-{now.date()}",
            comment=f"Сгорание баллов по истечении срока лота #{lot.id}"
        )

        Notification.objects.create(
            user=lot.user,
            title="Баллы сгорели",
            message=f"Срок действия {burn_amount} б. истёк.",
            notification_type='info'
        )

        log_audit_event(
            action='deduction',
            entity_type='PointLot',
            entity_id=str(lot.id),
            description=f"Сгорело {burn_amount} б. у пользователя {lot.user.username}",
            payload={'lot_id': lot.id, 'burned_amount': burn_amount}
        )

@shared_task
def accrue_seniority_points_daily():
    today = timezone.now().date()
    users = User.objects.filter(hire_date__isnull=False, is_active=True).exclude(role__in=['vip', 'maternity'])
    for user in users:
        hire = user.hire_date
        if hire.month == today.month and hire.day == today.day and today.year > hire.year:
            years = today.year - hire.year
            points = 500 * years
            PointService.accrue(
                user=user,
                amount=points,
                lot_type='non_burnable',
                comment=f"Начисление за стаж: {years} года в компании",
                idempotency_key=f"seniority-{user.id}-{today.year}"
            )

@shared_task
def process_event_accruals_daily():
    today = timezone.now().date()
    users = User.objects.filter(birth_date__isnull=False, is_active=True)
    for user in users:
        bday = user.birth_date
        if bday.month == today.month and bday.day == today.day:
            PointService.accrue(
                user=user,
                amount=500,
                lot_type='burnable',
                comment="Подарок ко дню рождения от компании",
                idempotency_key=f"bday-{user.id}-{today.year}"
            )
