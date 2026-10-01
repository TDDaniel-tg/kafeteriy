from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class BudgetRule(models.Model):
    name = models.CharField(max_length=150)
    grade = models.CharField(max_length=50, blank=True, default='')
    department = models.CharField(max_length=150, blank=True, default='')
    segment = models.CharField(max_length=100, blank=True, default='')
    amount = models.PositiveIntegerField(default=5000)
    period = models.CharField(max_length=20, default='annual', choices=[('annual', 'Годовой'), ('monthly', 'Ежемесячный')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}: {self.amount} б. ({self.grade or 'все грейды'})"

class EmployeeBudget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    period_year = models.IntegerField(default=2025)
    allocated_amount = models.PositiveIntegerField(default=0)
    spent_amount = models.PositiveIntegerField(default=0)
    is_frozen = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    comment = models.TextField(blank=True, default='')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='adjusted_budgets')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'period_year')
        ordering = ['-period_year']

    def clean(self):
        # ФТ-БЮД.5: Запрет изменения бюджета за завершённый период
        if self.pk:
            original = EmployeeBudget.objects.get(pk=self.pk)
            if original.is_closed:
                raise ValidationError("Запрещено изменять бюджет за закрытый (прошлый) период.")

    @property
    def remaining_amount(self):
        return max(0, self.allocated_amount - self.spent_amount)

class PositionLimit(models.Model):
    product_identifier = models.CharField(max_length=100, unique=True, db_index=True)
    product_name = models.CharField(max_length=255, blank=True, default='')
    max_per_day = models.PositiveIntegerField(null=True, blank=True)
    max_per_week = models.PositiveIntegerField(null=True, blank=True)
    max_per_month = models.PositiveIntegerField(null=True, blank=True)
    max_lifetime = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Лимиты для {self.product_name or self.product_identifier}"

class CategoryLimit(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    max_sum_per_month = models.PositiveIntegerField(null=True, blank=True)
    max_count_per_month = models.PositiveIntegerField(null=True, blank=True)
    is_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"Лимит категории {self.category_name} (Включен: {self.is_enabled})"
