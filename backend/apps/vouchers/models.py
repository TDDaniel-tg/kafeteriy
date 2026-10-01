from django.db import models
from django.conf import settings
from apps.catalog.models import Product

class VoucherBatch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='voucher_batches')
    batch_name = models.CharField(max_length=150)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_count = models.PositiveIntegerField(default=0)
    threshold_alert = models.PositiveIntegerField(default=5)  # ФТ-СЕР.3: порог остатка

    class Meta:
        verbose_name = 'Партия промокодов'
        verbose_name_plural = 'Партии промокодов'

    @property
    def remaining_count(self):
        return self.codes.filter(is_issued=False).count()

    @property
    def is_below_threshold(self):
        return self.remaining_count <= self.threshold_alert

    def __str__(self):
        return f"{self.batch_name} ({self.remaining_count}/{self.total_count} доступно)"

class VoucherCode(models.Model):
    batch = models.ForeignKey(VoucherBatch, on_delete=models.CASCADE, related_name='codes', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='voucher_codes')
    code = models.CharField(max_length=100, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_issued = models.BooleanField(default=False, db_index=True)
    issued_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_vouchers')
    issued_at = models.DateTimeField(null=True, blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='vouchers')

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        unique_together = ('product', 'code')

    def __str__(self):
        return f"{self.code} ({'Выдан' if self.is_issued else 'Доступен'})"
