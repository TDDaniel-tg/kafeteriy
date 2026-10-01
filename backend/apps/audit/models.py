import hashlib
import json
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('accrual', 'Начисление баллов'),
        ('deduction', 'Списание баллов'),
        ('refund', 'Возврат баллов'),
        ('transfer', 'Перевод баллов'),
        ('donation', 'Благотворительность'),
        ('budget_change', 'Изменение бюджета'),
        ('role_change', 'Смена роли пользователя'),
        ('permission_change', 'Изменение матрицы прав'),
        ('setting_change', 'Изменение настройки платформы'),
        ('account_freeze', 'Заморозка счета'),
        ('account_unfreeze', 'Разморозка счета'),
        ('anomaly_action', 'Действие по аномалии'),
        ('order_action', 'Действие с заказом'),
        ('login_2fa', 'Подтверждение 2FA'),
    ]

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_actions')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField()
    payload = models.JSONField(default=dict, blank=True)
    ip_address = models.CharField(max_length=50, blank=True, default='')
    integrity_hash = models.CharField(max_length=64, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Запись аудита'
        verbose_name_plural = 'Журнал аудита'
        ordering = ['-created_at']

    def clean(self):
        if self.pk:
            raise ValidationError("Записи журнала аудита неизменяемы (append-only).")

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Записи журнала аудита неизменяемы (append-only).")
        # Calculate integrity hash chaining to previous log
        last_log = AuditLog.objects.order_by('-id').first()
        prev_hash = last_log.integrity_hash if last_log else "GENESIS_AUDIT_BLOCK"
        content_str = f"{prev_hash}:{self.actor_id}:{self.action}:{self.entity_type}:{self.entity_id}:{json.dumps(self.payload, sort_keys=True, ensure_ascii=False)}"
        self.integrity_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Записи журнала аудита не могут быть удалены.")

class AnomalyRule(models.Model):
    name = models.CharField(max_length=150)
    rule_type = models.CharField(max_length=50, choices=[
        ('daily_spend_limit', 'Превышение суточного списания'),
        ('frequent_transfers', 'Частые переводы между сотрудниками'),
        ('abnormal_accrual', 'Аномально крупное начисление'),
        ('multiple_failed_totp', 'Множественные ошибки 2FA'),
    ])
    threshold = models.FloatField(default=10000.0)
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return f"{self.name} (порог: {self.threshold})"

class AnomalyTicket(models.Model):
    STATUS_CHOICES = [
        ('detected', 'Обнаружено'),
        ('legitimate', 'Легитимно'),
        ('blocked', 'Аккаунт заблокирован'),
    ]

    ticket_number = models.CharField(max_length=50, unique=True)
    rule = models.ForeignKey(AnomalyRule, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='anomaly_tickets')
    severity = models.CharField(max_length=20, default='medium', choices=[('low', 'Низкая'), ('medium', 'Средняя'), ('high', 'Высокая'), ('critical', 'Критическая')])
    description = models.TextField()
    status = models.CharField(max_length=20, default='detected', choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_anomalies')
    resolution_comment = models.TextField(blank=True, default='')
    detected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-detected_at']
