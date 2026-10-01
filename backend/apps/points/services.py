import uuid
from datetime import timedelta
from typing import Optional, Tuple
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.settings_platform.models import PlatformSetting
from apps.audit.services import log_audit_event
from .models import PointAccount, PointLot, PointTransaction

class InsufficientPointsError(Exception):
    pass

class PointService:
    @classmethod
    def get_or_create_account(cls, user) -> PointAccount:
        account, _ = PointAccount.objects.get_or_create(user=user)
        return account

    @classmethod
    @transaction.atomic
    def accrue(
        cls,
        user,
        amount: int,
        lot_type: str = 'burnable',
        expires_at: Optional[timezone.datetime] = None,
        comment: str = '',
        idempotency_key: Optional[str] = None,
        initiated_by = None
    ) -> PointTransaction:
        if amount <= 0:
            raise ValidationError("Сумма начисления должна быть строго больше нуля.")

        key = idempotency_key or f"accrue-{user.id}-{uuid.uuid4()}"
        existing = PointTransaction.objects.filter(idempotency_key=key).first()
        if existing:
            return existing

        account = PointAccount.objects.select_for_update().get_or_create(user=user)[0]

        # Calculate expiration if burnable and not provided
        if lot_type == 'burnable' and not expires_at:
            exp_months = PlatformSetting.get_setting('expiration_months', 12)
            expires_at = timezone.now() + timedelta(days=exp_months * 30)

        lot = PointLot.objects.create(
            user=user,
            lot_type=lot_type,
            initial_amount=amount,
            current_balance=amount,
            accrued_at=timezone.now(),
            expires_at=expires_at if lot_type == 'burnable' else None,
            comment=comment
        )

        account.total_balance += amount
        account.save()

        tx = PointTransaction.objects.create(
            account=account,
            transaction_type='accrual',
            amount=amount,
            balance_after=account.total_balance,
            idempotency_key=key,
            comment=comment or f"Начисление {lot_type} баллов",
            initiated_by=initiated_by
        )

        log_audit_event(
            action='accrual',
            entity_type='PointAccount',
            entity_id=str(account.id),
            actor=initiated_by,
            description=f"Начислено {amount} б. пользователю {user.username} (лот {lot.id})",
            payload={'amount': amount, 'lot_type': lot_type, 'tx_id': tx.id, 'comment': comment}
        )
        return tx

    @classmethod
    @transaction.atomic
    def spend(
        cls,
        user,
        amount: int,
        comment: str = '',
        idempotency_key: Optional[str] = None,
        initiated_by = None
    ) -> PointTransaction:
        if amount <= 0:
            raise ValidationError("Сумма списания должна быть строго больше нуля.")

        key = idempotency_key or f"spend-{user.id}-{uuid.uuid4()}"
        existing = PointTransaction.objects.filter(idempotency_key=key).first()
        if existing:
            return existing

        account = PointAccount.objects.select_for_update().get_or_create(user=user)[0]
        if user.is_frozen or account.frozen_balance >= account.total_balance:
            raise ValidationError("Счет пользователя заморожен. Списание невозможно.")

        if account.available_balance < amount:
            raise InsufficientPointsError(
                f"Недостаточно доступных баллов: требуется {amount} б., доступно {account.available_balance} б."
            )

        # Rule 4: FIFO by expiration date: first burnable with closest expires_at, then non-burnable
        needed = amount
        # 1. Burnable lots ordered by expiration date ascending
        burnable_lots = PointLot.objects.select_for_update().filter(
            user=user,
            lot_type='burnable',
            current_balance__gt=0,
            is_expired=False
        ).order_by('expires_at')

        for lot in burnable_lots:
            if needed <= 0:
                break
            deduct = min(lot.current_balance, needed)
            lot.current_balance -= deduct
            lot.save(update_fields=['current_balance'])
            needed -= deduct

        # 2. If needed > 0, deduct from non-burnable lots
        if needed > 0:
            non_burnable_lots = PointLot.objects.select_for_update().filter(
                user=user,
                lot_type='non_burnable',
                current_balance__gt=0
            ).order_by('accrued_at')

            for lot in non_burnable_lots:
                if needed <= 0:
                    break
                deduct = min(lot.current_balance, needed)
                lot.current_balance -= deduct
                lot.save(update_fields=['current_balance'])
                needed -= deduct

        account.total_balance -= amount
        account.save()

        tx = PointTransaction.objects.create(
            account=account,
            transaction_type='spend',
            amount=-amount,
            balance_after=account.total_balance,
            idempotency_key=key,
            comment=comment or "Списание баллов за заказ",
            initiated_by=initiated_by
        )

        log_audit_event(
            action='deduction',
            entity_type='PointAccount',
            entity_id=str(account.id),
            actor=initiated_by or user,
            description=f"Списано {amount} б. у пользователя {user.username}",
            payload={'amount': amount, 'tx_id': tx.id, 'comment': comment}
        )
        return tx

    @classmethod
    @transaction.atomic
    def refund(
        cls,
        user,
        amount: int,
        comment: str = '',
        idempotency_key: Optional[str] = None,
        initiated_by = None
    ) -> PointTransaction:
        if amount <= 0:
            raise ValidationError("Сумма возврата должна быть больше нуля.")

        key = idempotency_key or f"refund-{user.id}-{uuid.uuid4()}"
        existing = PointTransaction.objects.filter(idempotency_key=key).first()
        if existing:
            return existing

        account = PointAccount.objects.select_for_update().get_or_create(user=user)[0]

        # Refund creates an unexpired burnable lot with default validity
        exp_months = PlatformSetting.get_setting('expiration_months', 12)
        PointLot.objects.create(
            user=user,
            lot_type='burnable',
            initial_amount=amount,
            current_balance=amount,
            accrued_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=exp_months * 30),
            comment=f"Возврат баллов: {comment}"
        )

        account.total_balance += amount
        account.save()

        tx = PointTransaction.objects.create(
            account=account,
            transaction_type='refund',
            amount=amount,
            balance_after=account.total_balance,
            idempotency_key=key,
            comment=comment or "Возврат баллов",
            initiated_by=initiated_by
        )

        log_audit_event(
            action='refund',
            entity_type='PointAccount',
            entity_id=str(account.id),
            actor=initiated_by,
            description=f"Возвращено {amount} б. пользователю {user.username}",
            payload={'amount': amount, 'tx_id': tx.id, 'comment': comment}
        )
        return tx

    @classmethod
    @transaction.atomic
    def manual_adjust(
        cls,
        user,
        amount: int,
        is_add: bool,
        comment: str,
        totp_code: str,
        admin_user
    ) -> PointTransaction:
        if not comment or not comment.strip():
            raise ValidationError("Для ручной финансовой операции обязателен комментарий.")

        # Verify admin 2FA / TOTP (РОЛ.5, ФТ-БАЛ.8)
        if not admin_user.verify_totp(totp_code):
            raise ValidationError("Неверный код двухфакторной аутентификации (2FA/TOTP).")

        ceiling = PlatformSetting.get_setting('manual_accrual_ceiling', 10000)
        if is_add and amount > ceiling:
            raise ValidationError(f"Превышен максимальный лимит ручного начисления ({ceiling} б.).")

        key = f"manual-{admin_user.id}-{user.id}-{uuid.uuid4()}"
        if is_add:
            tx = cls.accrue(
                user=user,
                amount=amount,
                lot_type='burnable',
                comment=f"Ручное начисление: {comment}",
                idempotency_key=key,
                initiated_by=admin_user
            )
            # Update tx type to manual_add
            tx.transaction_type = 'manual_add'
            tx.save(update_fields=['transaction_type'])
        else:
            tx = cls.spend(
                user=user,
                amount=amount,
                comment=f"Ручное списание: {comment}",
                idempotency_key=key,
                initiated_by=admin_user
            )
            tx.transaction_type = 'manual_sub'
            tx.save(update_fields=['transaction_type'])

        log_audit_event(
            action='accrual' if is_add else 'deduction',
            entity_type='PointAccount',
            entity_id=str(user.point_account.id),
            actor=admin_user,
            description=f"Ручная операция ({'+' if is_add else '-'}{amount} б.) для {user.username}: {comment}",
            payload={'amount': amount, 'is_add': is_add, 'comment': comment, 'totp_verified': True}
        )
        return tx

    @classmethod
    @transaction.atomic
    def freeze_account(cls, user, is_frozen: bool, admin_user, comment: str = '') -> bool:
        account = cls.get_or_create_account(user)
        user.is_frozen = is_frozen
        user.save(update_fields=['is_frozen'])
        if is_frozen:
            account.frozen_balance = account.total_balance
        else:
            account.frozen_balance = 0
        account.save(update_fields=['frozen_balance'])

        log_audit_event(
            action='account_freeze' if is_frozen else 'account_unfreeze',
            entity_type='User',
            entity_id=str(user.id),
            actor=admin_user,
            description=f"{'Заморозка' if is_frozen else 'Разморозка'} счета сотрудника {user.username}: {comment}",
            payload={'user_id': user.id, 'is_frozen': is_frozen, 'comment': comment}
        )
        return True

    @classmethod
    @transaction.atomic
    def transfer(cls, sender, receiver, amount: int, comment: str = '') -> Tuple[PointTransaction, PointTransaction]:
        if sender.id == receiver.id:
            raise ValidationError("Нельзя переводить баллы самому себе.")

        min_amount = PlatformSetting.get_setting('transfer_min_amount', 100)
        if amount < min_amount:
            raise ValidationError(f"Минимальная сумма перевода составляет {min_amount} б.")

        commission_pct = PlatformSetting.get_setting('transfer_commission_pct', 25)
        fee = int(round(amount * (commission_pct / 100.0)))
        total_debit = amount + fee

        sender_account = cls.get_or_create_account(sender)
        if sender_account.available_balance < total_debit:
            raise InsufficientPointsError(
                f"Недостаточно баллов для перевода с комиссией {commission_pct}%: требуется {total_debit} б. (перевод {amount} б. + комиссия {fee} б.), доступно {sender_account.available_balance} б."
            )

        key_out = f"transfer-out-{sender.id}-{uuid.uuid4()}"
        key_in = f"transfer-in-{receiver.id}-{uuid.uuid4()}"

        tx_out = cls.spend(
            user=sender,
            amount=total_debit,
            comment=f"Перевод коллеге {receiver.full_name} ({amount} б. + комиссия {fee} б. [{commission_pct}%])",
            idempotency_key=key_out,
            initiated_by=sender
        )
        tx_out.transaction_type = 'transfer_out'
        tx_out.save(update_fields=['transaction_type'])

        tx_in = cls.accrue(
            user=receiver,
            amount=amount,
            lot_type='non_burnable',
            comment=f"Входящий перевод от {sender.full_name}: {comment or 'Спасибо!'}",
            idempotency_key=key_in,
            initiated_by=sender
        )
        tx_in.transaction_type = 'transfer_in'
        tx_in.save(update_fields=['transaction_type'])

        log_audit_event(
            action='transfer',
            entity_type='PointTransfer',
            entity_id=f"{sender.id}->{receiver.id}",
            actor=sender,
            description=f"Перевод {amount} б. от {sender.username} к {receiver.username} (комиссия {fee} б.)",
            payload={'amount': amount, 'fee': fee, 'sender_id': sender.id, 'receiver_id': receiver.id}
        )
        return tx_out, tx_in
