from typing import List, Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.campaigns.models import SelectionWindow
from apps.points.services import PointService
from apps.audit.services import log_audit_event
from apps.vouchers.models import VoucherCode
from apps.comms.models import Notification
from .models import Order, OrderItem, OrderApproval, OrderStatusHistory

class OrderService:
    @classmethod
    @transaction.atomic
    def checkout(
        cls,
        user,
        items_data: List[Dict[str, Any]],
        recipient_info: Optional[Dict[str, Any]] = None,
        delivery_address: str = ''
    ) -> Order:
        from apps.catalog.models import Product

        # 1. ФТ-ОКН.4: Проверка режима окна выбора
        active_window = SelectionWindow.objects.filter(is_active=True).first()
        if active_window and not active_window.is_currently_open():
            if active_window.rule_mode == 'restrict':
                raise ValidationError("Окно выбора закрыто. Оформление льгот заблокировано (требуется заявка в HR).")

        if not items_data:
            raise ValidationError("Корзина пуста. Выберите хотя бы одну позицию.")

        # 2. Validate products and calculate total points
        total_points = 0
        order_items_to_create = []
        requires_approval = False
        approver_types = set()

        for item in items_data:
            product = Product.objects.select_for_update().get(id=item['product_id'])
            if not product.is_active or product.is_archived:
                raise ValidationError(f"Позиция «{product.name}» недоступна для заказа.")

            # Check VIP role restriction
            if user.role == 'vip' and not product.is_general_offer:
                raise ValidationError(f"Для роли ВИП доступны только общие предложения.")

            # Check Maternity role restriction
            if user.role == 'maternity' and product.category == 'Здоровье':
                raise ValidationError(f"Страховые программы недоступны для вашей роли.")

            # ФТ-ЛГТ.4: Блокировка отпуска при неотгулянном основном отпуске
            if product.product_type == 'vacation_days' and user.has_unspent_main_vacation:
                raise ValidationError("Покупка дополнительных дней отпуска заблокирована при наличии неотгулянного основного отпуска.")

            qty = item.get('quantity', 1)
            subtotal = product.price * qty
            total_points += subtotal

            if product.requires_approval or product.product_type in ('vacation_days', 'doc_benefit'):
                requires_approval = True
                approver_types.add(product.approver_type if product.approver_type != 'none' else 'manager')

            order_items_to_create.append((product, qty, subtotal, item.get('meta_info', {})))

        # 3. Spend points via PointService (FIFO deduction)
        order_num = Order.generate_order_number()
        tx = PointService.spend(
            user=user,
            amount=total_points,
            comment=f"Оплата заказа #{order_num}",
            idempotency_key=f"order-spend-{order_num}"
        )

        initial_status = 'pending_approval' if requires_approval else 'processing'

        rec_info = recipient_info or {}
        order = Order.objects.create(
            order_number=order_num,
            user=user,
            status=initial_status,
            total_points=total_points,
            recipient_name=rec_info.get('name', user.full_name),
            recipient_email=rec_info.get('email', user.email),
            recipient_phone=rec_info.get('phone', user.phone),
            delivery_address=delivery_address or user.delivery_address
        )

        for prod, qty, price, meta in order_items_to_create:
            OrderItem.objects.create(
                order=order,
                product=prod,
                price=prod.price,
                quantity=qty,
                meta_info=meta
            )

        OrderStatusHistory.objects.create(
            order=order,
            status=initial_status,
            comment="Заказ успешно сформирован",
            changed_by=user
        )

        # 4. Create Approvals if needed
        if requires_approval:
            manager = user.manager or user
            if 'manager' in approver_types or 'both' in approver_types:
                OrderApproval.objects.create(
                    order=order,
                    approver=manager,
                    stage='manager',
                    status='pending'
                )
            if 'hr' in approver_types or 'both' in approver_types:
                OrderApproval.objects.create(
                    order=order,
                    stage='hr',
                    status='pending'
                )

        # 5. Issue vouchers immediately if no approval required and has digital items
        if not requires_approval:
            cls._issue_vouchers_for_order(order)
            order.status = 'completed'
            order.save(update_fields=['status'])
            OrderStatusHistory.objects.create(
                order=order,
                status='completed',
                comment="Заказ автоматически исполнен",
                changed_by=None
            )

        # Send notification to user
        Notification.objects.create(
            user=user,
            title="Заказ оформлен",
            message=f"Заказ {order.order_number} на сумму {total_points} б. принят в обработку.",
            notification_type='success'
        )

        log_audit_event(
            action='order_action',
            entity_type='Order',
            entity_id=str(order.id),
            actor=user,
            description=f"Создан заказ {order.order_number} на {total_points} б.",
            payload={'order_number': order.order_number, 'total_points': total_points, 'status': order.status}
        )
        return order

    @classmethod
    @transaction.atomic
    def approve_order(cls, approval_id: int, approver_user, decision: str, comment: str = '') -> Order:
        approval = OrderApproval.objects.select_for_update().get(id=approval_id)
        order = Order.objects.select_for_update().get(id=approval.order_id)

        if decision not in ('approved', 'rejected'):
            raise ValidationError("Решение должно быть 'approved' или 'rejected'.")

        approval.status = decision
        approval.comment = comment
        approval.approver = approver_user
        approval.decided_at = timezone.now()
        approval.save()

        if decision == 'rejected':
            order.status = 'cancelled'
            order.cancellation_reason = f"Отклонено согласующим ({approval.get_stage_display()}): {comment}"
            order.save()
            # Refund points
            PointService.refund(
                user=order.user,
                amount=order.total_points,
                comment=f"Возврат по отклоненному заказу {order.order_number}",
                initiated_by=approver_user
            )
            order.is_refunded = True
            order.save(update_fields=['is_refunded'])
            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                comment=f"Отклонено: {comment}",
                changed_by=approver_user
            )
            Notification.objects.create(
                user=order.user,
                title="Заказ отклонён",
                message=f"Заказ {order.order_number} отклонён: {comment}. Баллы возвращены на ваш счёт.",
                notification_type='danger'
            )
            return order

        # Check if all approvals are approved
        pending_exists = order.approvals.filter(status='pending').exists()
        if not pending_exists:
            order.status = 'completed'
            order.save(update_fields=['status'])
            cls._issue_vouchers_for_order(order)
            OrderStatusHistory.objects.create(
                order=order,
                status='completed',
                comment="Все этапы согласования пройдены",
                changed_by=approver_user
            )
            Notification.objects.create(
                user=order.user,
                title="Заказ согласован",
                message=f"Заказ {order.order_number} успешно согласован и выполнен!",
                notification_type='success'
            )

        log_audit_event(
            action='order_action',
            entity_type='Order',
            entity_id=str(order.id),
            actor=approver_user,
            description=f"Согласование заказа {order.order_number}: {decision} ({comment})",
            payload={'order_number': order.order_number, 'decision': decision, 'comment': comment}
        )
        return order

    @classmethod
    @transaction.atomic
    def cancel_order(cls, order_id: int, user, reason: str = '') -> Order:
        order = Order.objects.select_for_update().get(id=order_id)
        if not order.can_be_cancelled():
            raise ValidationError("Для позиций с промокодами отмена заказа невозможна (ФТ-ЗАК.6).")

        order.status = 'cancelled'
        order.cancellation_reason = reason or "Отменено пользователем"
        order.save()

        PointService.refund(
            user=order.user,
            amount=order.total_points,
            comment=f"Возврат по отмене заказа {order.order_number}",
            initiated_by=user
        )
        order.is_refunded = True
        order.save(update_fields=['is_refunded'])

        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            comment=f"Заказ отменен: {reason}",
            changed_by=user
        )

        Notification.objects.create(
            user=order.user,
            title="Заказ отменен",
            message=f"Заказ {order.order_number} отменен. {order.total_points} б. возвращены на ваш баланс.",
            notification_type='info'
        )

        log_audit_event(
            action='order_action',
            entity_type='Order',
            entity_id=str(order.id),
            actor=user,
            description=f"Отменен заказ {order.order_number}. Возвращено {order.total_points} б.",
            payload={'order_number': order.order_number, 'refunded': order.total_points, 'reason': reason}
        )
        return order

    @classmethod
    def _issue_vouchers_for_order(cls, order: Order):
        for item in order.items.all():
            if item.product.product_type in ('digital', 'gift_service'):
                # Pick available voucher code
                code_obj = VoucherCode.objects.filter(
                    product=item.product,
                    is_issued=False
                ).first()
                if code_obj:
                    code_obj.is_issued = True
                    code_obj.issued_to = order.user
                    code_obj.issued_at = timezone.now()
                    code_obj.order = order
                    code_obj.save()
                    Notification.objects.create(
                        user=order.user,
                        title="Промокод получен",
                        message=f"Ваш промокод для «{item.product.name}»: {code_obj.code}. Отправлен на {order.recipient_email}.",
                        notification_type='success'
                    )
