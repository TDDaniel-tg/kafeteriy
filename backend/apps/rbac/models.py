from django.db import models

class RolePermission(models.Model):
    role = models.CharField(max_length=20, db_index=True)
    permission_key = models.CharField(max_length=100, db_index=True)
    is_allowed = models.BooleanField(default=True)
    description = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        verbose_name = 'Право роли'
        verbose_name_plural = 'Матрица прав ролей'
        unique_together = ('role', 'permission_key')

    def __str__(self):
        return f"{self.role} -> {self.permission_key} ({'Да' if self.is_allowed else 'Нет'})"

class Segment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    criteria_grade = models.CharField(max_length=100, blank=True, default='')
    criteria_department = models.CharField(max_length=150, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Сегмент сотрудников'
        verbose_name_plural = 'Сегменты сотрудников'

    def __str__(self):
        return self.name

class SegmentVisibilityRule(models.Model):
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, related_name='visibility_rules')
    section_name = models.CharField(max_length=100)
    is_visible = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Правило видимости сегмента'
        verbose_name_plural = 'Правила видимости сегментов'
        unique_together = ('segment', 'section_name')
