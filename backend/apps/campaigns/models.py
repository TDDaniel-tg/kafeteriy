from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class SelectionWindow(models.Model):
    RULE_MODE_CHOICES = [
        ('inform', 'Информирует (изменения разрешены, сотрудник уведомляется)'),
        ('restrict', 'Ограничивает (вне окна блокируется оформление и отмена)'),
    ]

    name = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    rule_mode = models.CharField(max_length=20, choices=RULE_MODE_CHOICES, default='inform')
    is_active = models.BooleanField(default=True)
    target_segments = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Окно выбора (Кампания)'
        verbose_name_plural = 'Окна выбора (Кампании)'
        ordering = ['-start_date']

    def clean(self):
        # ФТ-ОКН.5: Контроль корректности дат: дата окончания не может быть ранее даты начала
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'Дата окончания окна выбора не может быть ранее даты начала.'})

    def is_currently_open(self) -> bool:
        now = timezone.now()
        return bool(self.is_active and self.start_date <= now <= self.end_date)

    def __str__(self):
        status = "Открыто" if self.is_currently_open() else "Закрыто"
        return f"{self.name} ({status}, {self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')})"
