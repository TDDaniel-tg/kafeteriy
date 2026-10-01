from django.db import models

class IntegrationChannel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    channel_type = models.CharField(max_length=50, choices=[
        ('1c_zup', '1С:ЗУП'),
        ('sso', 'Корпоративный SSO'),
        ('smtp', 'Почтовый шлюз SMTP'),
        ('giftery', 'Giftery API'),
        ('prostodar', 'ПВК / Prostodar API'),
        ('accounting', 'Канал выгрузки в бухгалтерию'),
    ])
    is_enabled = models.BooleanField(default=True)
    is_mock = models.BooleanField(default=True)
    endpoint_url = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=20, default='available', choices=[
        ('available', 'Доступно'),
        ('degraded', 'Сбои'),
        ('unavailable', 'Недоступно'),
    ])
    last_check_at = models.DateTimeField(auto_now=True)
    response_time_ms = models.PositiveIntegerField(default=45)
    error_message = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.name} ({self.status}, {'Mock' if self.is_mock else 'Real'})"
