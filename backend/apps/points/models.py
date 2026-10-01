from django.db import models
from django.conf import settings
from django.utils import timezone

class PointAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='point_account')
    total_balance = models.IntegerField(default=0)
    frozen_balance = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Балльный счет'
        verbose_name_plural = 'Балльные счета'

    @property
    def available_balance(self) -> int:
        return max(0, self.total_balance - self.frozen_balance)

    def __str__(self):
        return f"Счет {self.user.username}: {self.available_balance} б. (всего: {self.total_balance})"

class PointLot(models.Model):
    LOT_TYPE_CHOICES = [
        ('burnable', 'Сгораемые'),
        ('non_burnable', 'Несгораемые'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='point_lots')
    lot_type = models.CharField(max_length=20, choices=LOT_TYPE_CHOICES, default='burnable', db_index=True)
    initial_amount = models.PositiveIntegerField()
    current_balance = models.PositiveIntegerField()
    accrued_at = models.DateTimeField(default=timezone.now, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_expired = models.BooleanField(default=False)
    comment = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        verbose_name = 'Партия баллов (Lot)'
        verbose_name_plural = 'Партии баллов'
        ordering = ['expires_at', 'accrued_at']

    def __str__(self):
        return f"{self.user.username} - {self.lot_type}: {self.current_balance}/{self.initial_amount} б. (до {self.expires_at})"

class PointTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('accrual', 'Начисление'),
        ('spend', 'Списание'),
        ('expire', 'Сгорание'),
        ('refund', 'Возврат'),
        ('manual_add', 'Ручное начисление'),
        ('manual_sub', 'Ручное списание'),
        ('freeze', 'Заморозка'),
        ('unfreeze', 'Разморозка'),
        ('transfer_in', 'Входящий перевод'),
        ('transfer_out', 'Исходящий перевод'),
        ('donation', 'Благотворительность'),
    ]

    account = models.ForeignKey(PointAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, db_index=True)
    amount = models.IntegerField()  # + for credit, - for debit
    balance_after = models.IntegerField()
    idempotency_key = models.CharField(max_length=128, unique=True, db_index=True)
    comment = models.CharField(max_length=255, blank=True, default='')
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Транзакция баллов'
        verbose_name_plural = 'Журнал транзакций баллов'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type}: {self.amount:+d} б. (Остаток: {self.balance_after} б.)"
