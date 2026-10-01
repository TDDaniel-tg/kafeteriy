import random
from django.db import models
from django.conf import settings
from apps.catalog.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('pending_approval', 'На согласовании'),
        ('processing', 'В обработке'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменён'),
    ]

    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', db_index=True)
    total_points = models.PositiveIntegerField()
    recipient_name = models.CharField(max_length=255, blank=True, default='')
    recipient_email = models.EmailField(blank=True, default='')
    recipient_phone = models.CharField(max_length=50, blank=True, default='')
    delivery_address = models.CharField(max_length=255, blank=True, default='')
    delivery_status = models.CharField(max_length=50, blank=True, default='Ожидает обработки')
    cancellation_reason = models.TextField(blank=True, default='')
    is_refunded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    @classmethod
    def generate_order_number(cls) -> str:
        # e.g. КЛ-24052
        num = random.randint(24000, 99999)
        while cls.objects.filter(order_number=f"КЛ-{num}").exists():
            num = random.randint(24000, 99999)
        return f"КЛ-{num}"

    def can_be_cancelled(self) -> bool:
        if self.status in ('cancelled', 'completed'):
            return False
        # ФТ-ЗАК.6: Для позиций с промокодами отмена заказа невозможна
        has_voucher_or_gift = self.items.filter(product__product_type__in=['digital', 'gift_service']).exists()
        return not has_voucher_or_gift

    def __str__(self):
        return f"Заказ {self.order_number} ({self.get_status_display()}, {self.total_points} б.)"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    meta_info = models.JSONField(default=dict, blank=True)

    @property
    def subtotal(self):
        return self.price * self.quantity

class OrderApproval(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_approvals')
    stage = models.CharField(max_length=20, choices=[('manager', 'Руководитель'), ('hr', 'HR служба'), ('custom', 'Дополнительный согласующий')])
    status = models.CharField(max_length=20, default='pending', choices=[('pending', 'Ожидает решения'), ('approved', 'Согласовано'), ('rejected', 'Отклонено')])
    comment = models.TextField(blank=True, default='')
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    comment = models.CharField(max_length=255, blank=True, default='')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
