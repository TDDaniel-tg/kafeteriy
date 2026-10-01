import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('cafeteria')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # ФТ-БАЛ.3, ФТ-БАЛ.4: Проверка сроков сгорания баллов и отправка уведомлений
    'check-expiring-point-lots': {
        'task': 'apps.points.tasks.check_expiring_lots_and_notify',
        'schedule': crontab(hour=8, minute=0),  # Каждый день в 8:00
    },
    # ФТ-БАЛ.6: Начисление баллов за стаж в дату трудоустройства
    'accrue-seniority-points-daily': {
        'task': 'apps.points.tasks.accrue_seniority_points_daily',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9:00
    },
    # ФТ-БАЛ.7: Событийные начисления (дни рождения, праздники)
    'process-scheduled-event-accruals': {
        'task': 'apps.points.tasks.process_event_accruals_daily',
        'schedule': crontab(hour=9, minute=30),
    },
    # ФТ-ОКН.6: Проверка статуса окон выбора и рассылка уведомлений о старте/окончании
    'check-selection-windows-status': {
        'task': 'apps.campaigns.tasks.check_selection_windows',
        'schedule': crontab(hour=10, minute=0),
    },
    # ФТ-СЕР.3: Мониторинг порогов остатка промокодов
    'monitor-voucher-thresholds': {
        'task': 'apps.vouchers.tasks.check_voucher_thresholds',
        'schedule': crontab(hour='*/4', minute=0),
    },
    # ФТ-АУД.2: Анализ аномалий в операциях
    'scan-operations-for-anomalies': {
        'task': 'apps.audit.tasks.scan_anomalies',
        'schedule': crontab(minute='*/30'),
    }
}
