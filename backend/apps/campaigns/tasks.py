from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.comms.models import Notification
from .models import SelectionWindow

User = get_user_model()

@shared_task
def check_selection_windows():
    now = timezone.now()
    active_windows = SelectionWindow.objects.filter(is_active=True)
    for window in active_windows:
        # Check window just started
        if window.start_date <= now <= window.start_date + timedelta(hours=24):
            users = User.objects.filter(is_active=True)
            for u in users:
                Notification.objects.get_or_create(
                    user=u,
                    title=f"Старт окна выбора льгот",
                    message=f"Кампания «{window.name}» открыта! Выберите льготы до {window.end_date.strftime('%d.%m.%Y')}.",
                    notification_type='success'
                )
        # Check window ending soon (within 3 days)
        elif now <= window.end_date <= now + timedelta(days=3):
            users = User.objects.filter(is_active=True)
            for u in users:
                Notification.objects.get_or_create(
                    user=u,
                    title=f"Окно выбора скоро закроется",
                    message=f"Кампания «{window.name}» завершается {window.end_date.strftime('%d.%m.%Y')}. Проверьте корзину!",
                    notification_type='warning'
                )
