import json
from django.db import models
from django.conf import settings

class PlatformSetting(models.Model):
    TYPE_CHOICES = [
        ('int', 'Целое число'),
        ('float', 'Дробное число'),
        ('string', 'Строка'),
        ('bool', 'Логическое (Да/Нет)'),
        ('json', 'JSON структура'),
    ]

    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField()
    value_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='string')
    description = models.CharField(max_length=255, blank=True, default='')
    version = models.PositiveIntegerField(default=1)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Настройка платформы'
        verbose_name_plural = 'Настройки платформы'

    def get_typed_value(self):
        if self.value_type == 'int':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'bool':
            return self.value.lower() in ('true', '1', 'yes', 't')
        elif self.value_type == 'json':
            try:
                return json.loads(self.value)
            except Exception:
                return {}
        return self.value

    @classmethod
    def get_setting(cls, key: str, default=None):
        item = cls.objects.filter(key=key).first()
        if not item:
            return default
        return item.get_typed_value()

    @classmethod
    def set_setting(cls, key: str, value, user=None, comment: str = '') -> 'PlatformSetting':
        from apps.audit.services import log_audit_event
        item = cls.objects.filter(key=key).first()
        val_str = str(value)
        if isinstance(value, bool):
            val_str = 'true' if value else 'false'
        elif isinstance(value, (dict, list)):
            val_str = json.dumps(value, ensure_ascii=False)

        if not item:
            # Determine type
            v_type = 'string'
            if isinstance(value, bool):
                v_type = 'bool'
            elif isinstance(value, int):
                v_type = 'int'
            elif isinstance(value, float):
                v_type = 'float'
            elif isinstance(value, (dict, list)):
                v_type = 'json'

            item = cls.objects.create(
                key=key,
                value=val_str,
                value_type=v_type,
                version=1,
                updated_by=user
            )
            PlatformSettingHistory.objects.create(
                setting=item,
                version=1,
                value=val_str,
                updated_by=user,
                comment=comment or 'Создание настройки'
            )
            log_audit_event(
                action='setting_change',
                entity_type='PlatformSetting',
                entity_id=str(item.id),
                actor=user,
                description=f'Создана настройка {key}={val_str}',
                payload={'key': key, 'new_value': val_str, 'version': 1}
            )
            return item

        old_value = item.value
        item.version += 1
        item.value = val_str
        item.updated_by = user
        item.save()

        PlatformSettingHistory.objects.create(
            setting=item,
            version=item.version,
            value=val_str,
            updated_by=user,
            comment=comment or f'Обновление версии {item.version}'
        )

        log_audit_event(
            action='setting_change',
            entity_type='PlatformSetting',
            entity_id=str(item.id),
            actor=user,
            description=f'Изменена настройка {key}: {old_value} -> {val_str}',
            payload={'key': key, 'old_value': old_value, 'new_value': val_str, 'version': item.version}
        )
        return item

class PlatformSettingHistory(models.Model):
    setting = models.ForeignKey(PlatformSetting, on_delete=models.CASCADE, related_name='history')
    version = models.PositiveIntegerField()
    value = models.TextField()
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['-version']
