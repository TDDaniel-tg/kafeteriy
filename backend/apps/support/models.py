import random
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.settings_platform.models import PlatformSetting

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новое'),
        ('in_progress', 'В обработке'),
        ('waiting_provider', 'Ожидает поставщика'),
        ('resolved', 'Решено'),
        ('closed', 'Закрыто'),
    ]

    ticket_number = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    sla_deadline = models.DateTimeField(null=True, blank=True)
    is_escalated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Обращение в поддержку'
        verbose_name_plural = 'Обращения в поддержку'
        ordering = ['-created_at']

    @classmethod
    def generate_ticket_number(cls) -> str:
        # e.g. КЛ-1842
        num = random.randint(1000, 9999)
        while cls.objects.filter(ticket_number=f"КЛ-{num}").exists():
            num = random.randint(1000, 9999)
        return f"КЛ-{num}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        if not self.sla_deadline:
            hours = PlatformSetting.get_setting('support_sla_hours', 24)
            self.sla_deadline = timezone.now() + timedelta(hours=hours)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number}: {self.subject} ({self.get_status_display()})"

class TicketAttachment(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='support_attachments/')
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class PerkSuggestion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perk_suggestions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=30, default='under_review', choices=[
        ('under_review', 'На рассмотрении HR'),
        ('accepted', 'Принято к внедрению'),
        ('declined', 'Отклонено'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
