from celery import shared_task
from django.contrib.auth import get_user_model
from apps.comms.models import Notification
from .models import VoucherBatch

User = get_user_model()

@shared_task
def check_voucher_thresholds():
    batches = VoucherBatch.objects.all()
    admins = User.objects.filter(role__in=['admin', 'hr'], is_active=True)
    for b in batches:
        if b.is_below_threshold:
            for admin in admins:
                Notification.objects.get_or_create(
                    user=admin,
                    title="Заканчиваются промокоды",
                    message=f"По позиции «{b.product.name}» осталось всего {b.remaining_count} кодов (порог: {b.threshold_alert}). Загрузите новую партию!",
                    notification_type='warning'
                )
