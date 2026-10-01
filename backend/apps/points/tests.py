import pytest
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from apps.points.models import PointAccount, PointLot, PointTransaction
from apps.points.services import PointService, InsufficientPointsError
from apps.campaigns.models import SelectionWindow
from apps.audit.models import AuditLog
from apps.audit.services import log_audit_event
from apps.catalog.models import Product
from apps.orders.services import OrderService

User = get_user_model()

@pytest.mark.django_db
class TestCafeteriaCore:
    def setup_method(self):
        self.user = User.objects.create(
            username='test_emp',
            first_name='Тест',
            last_name='Тестов',
            role='employee'
        )
        self.admin = User.objects.create(
            username='test_admin',
            role='admin',
            is_staff=True
        )

    def test_points_accrual_and_fifo_deduction(self):
        """ФТ-БАЛ.4: FIFO: сначала сгораемые баллы с ближайшим сроком, затем несгораемые."""
        now = timezone.now()
        # Lot 1: burnable, expires in 30 days, 300 pts
        PointLot.objects.create(
            user=self.user,
            lot_type='burnable',
            initial_amount=300,
            current_balance=300,
            expires_at=now + timedelta(days=30)
        )
        # Lot 2: burnable, expires in 10 days, 500 pts (should be consumed FIRST)
        PointLot.objects.create(
            user=self.user,
            lot_type='burnable',
            initial_amount=500,
            current_balance=500,
            expires_at=now + timedelta(days=10)
        )
        # Lot 3: non_burnable, 1000 pts (should be consumed LAST)
        PointLot.objects.create(
            user=self.user,
            lot_type='non_burnable',
            initial_amount=1000,
            current_balance=1000
        )
        acc = PointAccount.objects.get_or_create(user=self.user)[0]
        acc.total_balance = 1800
        acc.save()

        # Deduct 600 pts
        # Should fully consume Lot 2 (500 pts) and 100 pts from Lot 1 (leaving 200 pts in Lot 1), leaving Lot 3 untouched (1000 pts)
        PointService.spend(self.user, 600, comment="Test spend")

        lot2 = PointLot.objects.filter(user=self.user, initial_amount=500).first()
        lot1 = PointLot.objects.filter(user=self.user, initial_amount=300).first()
        lot3 = PointLot.objects.filter(user=self.user, initial_amount=1000).first()

        assert lot2.current_balance == 0
        assert lot1.current_balance == 200
        assert lot3.current_balance == 1000
        self.user.point_account.refresh_from_db()
        assert self.user.point_account.total_balance == 1200

    def test_idempotency_protection(self):
        """Идемпотентность финансовых операций: повторный запрос с тем же ключом не списывает баллы дважды."""
        PointService.accrue(self.user, 1000, idempotency_key='uniq-key-1')
        assert self.user.point_account.total_balance == 1000

        # Accrue again with same idempotency key
        PointService.accrue(self.user, 1000, idempotency_key='uniq-key-1')
        assert self.user.point_account.total_balance == 1000

    def test_audit_log_immutability(self):
        """ФТ-АУД.1: Записи аудита неизменяемы (append-only). Любая попытка изменить или удалить вызывает исключение."""
        log = log_audit_event(
            action='accrual',
            entity_type='Test',
            description='Test immutable log',
            actor=self.admin
        )
        assert log.pk is not None
        assert log.integrity_hash != ''

        # Attempt to modify
        log.description = 'Hacked description'
        with pytest.raises(ValidationError):
            log.save()

        # Attempt to delete
        with pytest.raises(ValidationError):
            log.delete()

    def test_campaign_window_date_validation(self):
        """ФТ-ОКН.5: Дата окончания не может быть ранее даты начала."""
        now = timezone.now()
        window = SelectionWindow(
            name='Некорректное окно',
            start_date=now,
            end_date=now - timedelta(days=1),
            rule_mode='restrict'
        )
        with pytest.raises(ValidationError):
            window.full_clean()

    def test_vacation_perk_blocked_when_unspent_main_vacation(self):
        """ФТ-ЛГТ.4: Блокировка доп. дней отпуска при неотгулянном основном отпуске."""
        self.user.has_unspent_main_vacation = True
        self.user.save()
        PointService.accrue(self.user, 5000)

        vacation_prod = Product.objects.create(
            slug='vacation-test',
            name='Доп день отпуска',
            price=1200,
            product_type='vacation_days'
        )

        with pytest.raises(ValidationError, match='неотгулянного основного отпуска'):
            OrderService.checkout(self.user, [{'product_id': vacation_prod.id, 'quantity': 1}])
