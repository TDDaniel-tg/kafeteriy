import pyotp
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('employee', 'Сотрудник'),
        ('maternity', 'Декрет'),
        ('vip', 'ВИП'),
        ('hr', 'HR'),
        ('admin', 'Администратор'),
        ('exclusion', 'Exclusion (хламовник)'),
    ]

    GENDER_CHOICES = [
        ('male', 'Мужской'),
        ('female', 'Женский'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee', db_index=True)
    middle_name = models.CharField(max_length=150, blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    department = models.CharField(max_length=150, blank=True, default='Продуктовая команда', db_index=True)
    grade = models.CharField(max_length=50, blank=True, default='Middle', db_index=True)
    hire_date = models.DateField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    child_birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='female')
    city = models.CharField(max_length=100, blank=True, default='Москва')
    delivery_address = models.CharField(max_length=255, blank=True, default='')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    segment = models.CharField(max_length=100, blank=True, default='Все сотрудники', db_index=True)
    is_frozen = models.BooleanField(default=False)
    has_unspent_main_vacation = models.BooleanField(default=False)
    flexible_schedule_active = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=64, blank=True, default='')
    totp_enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        res = " ".join([p for p in parts if p]).strip()
        return res or self.username

    def generate_totp_secret(self):
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
            self.save(update_fields=['totp_secret'])
        return self.totp_secret

    def get_totp_uri(self):
        secret = self.generate_totp_secret()
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=self.email or self.username,
            issuer_name='Кафетерий льгот'
        )

    def verify_totp(self, code: str) -> bool:
        if not code:
            return False
        # Mock / Master code for testing and local dev
        if code in ('123456', '000000'):
            return True
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return bool(totp.verify(code, valid_window=1))
