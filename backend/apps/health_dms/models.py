from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

class DMSProgram(models.Model):
    name = models.CharField(max_length=150)
    insurer = models.CharField(max_length=100, default='Ингосстрах')
    description = models.TextField()
    price_points = models.PositiveIntegerField(default=3000)
    is_default = models.BooleanField(default=False)
    includes = models.JSONField(default=list, blank=True)
    excludes = models.JSONField(default=list, blank=True)
    clinics = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = 'Программа ДМС'
        verbose_name_plural = 'Программы ДМС'

    def __str__(self):
        return f"{self.name} ({self.insurer})"

class EmployeeDMSPolicy(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('pending_upgrade', 'На согласовании замены'),
        ('opted_out', 'Отказ от базового ДМС'),
        ('expired', 'Истёк'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dms_policy')
    program = models.ForeignKey(DMSProgram, on_delete=models.PROTECT, related_name='policies')
    policy_number = models.CharField(max_length=50, blank=True, default='')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active')
    valid_until = models.DateField(default=timezone.now)
    is_opted_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Полис сотрудника'
        verbose_name_plural = 'Полисы сотрудников'

    def __str__(self):
        return f"Полис {self.user.username} ({self.get_status_display()})"

class FamilyMemberDMS(models.Model):
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Супруг / супруга'),
        ('child', 'Ребёнок'),
        ('parent', 'Родитель'),
    ]

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='family_dms')
    full_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=[('male', 'Мужской'), ('female', 'Женский')])
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    price_points = models.PositiveIntegerField(default=2000)
    status = models.CharField(max_length=30, default='submitted', choices=[
        ('submitted', 'Заявка отправлена'),
        ('processing', 'В оформлении'),
        ('active', 'Полис активен'),
        ('rejected', 'Отклонено'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'ДМС члена семьи'
        verbose_name_plural = 'ДМС членов семьи'

    def clean(self):
        # ФТ-ДМС.5: Валидация возраста застрахованного
        if self.birth_date:
            age = (timezone.now().date() - self.birth_date).days // 365
            if age > 70:
                raise ValidationError("Для возраста старше 70 лет требуется альтернативная программа страхования. Обратитесь в HR.")

class DMSChangeRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('upgrade', 'Расширение программы'),
        ('switch_program', 'Замена базовой программы'),
        ('opt_out', 'Отказ от базового ДМС'),
    ]

    STATUS_CHOICES = [
        ('submitted', 'Заявка отправлена'),
        ('approved', 'Одобрено'),
        ('completed', 'Исполнено'),
        ('rejected', 'Отклонено'),
    ]

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dms_requests')
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPE_CHOICES)
    target_program = models.ForeignKey(DMSProgram, on_delete=models.SET_NULL, null=True, blank=True)
    selected_options = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='submitted')
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заявка на изменение ДМС'
        verbose_name_plural = 'Заявки на изменение ДМС'
        ordering = ['-created_at']
