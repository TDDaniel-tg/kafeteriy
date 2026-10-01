import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.catalog.models import Product
from apps.points.services import PointService
from apps.orders.services import OrderService
from apps.vouchers.models import VoucherBatch, VoucherCode

User = get_user_model()

@pytest.mark.django_db
class TestRoleAccessAndBusinessRules:
    def setup_method(self):
        self.client = APIClient()
        self.employee = User.objects.create(username='emp', role='employee')
        self.maternity = User.objects.create(username='mat', role='maternity')
        self.vip = User.objects.create(username='vip', role='vip')
        self.exclusion = User.objects.create(username='excl', role='exclusion')
        self.admin = User.objects.create(username='adm', role='admin', is_staff=True)

        PointService.accrue(self.employee, 10000)
        PointService.accrue(self.maternity, 10000)
        PointService.accrue(self.vip, 10000)

        # Products
        self.general_prod = Product.objects.create(
            slug='gen-prod',
            name='Общий курс',
            category='Обучение',
            price=1000,
            is_general_offer=True
        )
        self.health_prod = Product.objects.create(
            slug='health-prod',
            name='Медицинский полис',
            category='Здоровье',
            price=2000,
            is_general_offer=False
        )

    def test_maternity_cannot_access_dms(self):
        """РОЛ.1: Декрет — все разделы, кроме страховых программ."""
        self.client.force_authenticate(user=self.maternity)
        response = self.client.get('/api/health-dms/my-policy/')
        assert response.status_code == 403
        assert 'Декрет' in response.data['error']

    def test_vip_sees_only_general_offers(self):
        """РОЛ.1: ВИП — только раздел «Общие предложения»."""
        self.client.force_authenticate(user=self.vip)
        response = self.client.get('/api/catalog/')
        assert response.status_code == 200
        # Should only contain is_general_offer=True
        product_slugs = [p['slug'] for p in response.data['results'] if 'slug' in p] if 'results' in response.data else [p['slug'] for p in response.data]
        assert 'gen-prod' in product_slugs
        assert 'health-prod' not in product_slugs

    def test_peer_transfer_commission(self):
        """ФТ-СОЦ.1: Перевод баллов между сотрудниками с комиссией 25%."""
        recipient = User.objects.create(username='colleague', role='employee')
        # Employee has 10000 pts
        # Transfer 1000 pts -> commission 250 pts -> total deducted 1250 pts
        response = self.client.post('/api/points/transfer/', {
            'receiver_id': recipient.id,
            'amount': 1000,
            'comment': 'Спасибо за помощь!'
        }, HTTP_X_USER_ID=str(self.employee.id))
        assert response.status_code == 200

        self.employee.point_account.refresh_from_db()
        recipient.point_account.refresh_from_db()
        assert self.employee.point_account.total_balance == 10000 - 1250
        assert recipient.point_account.total_balance == 1000

    def test_voucher_cancellation_prohibited(self):
        """ФТ-ЗАК.6: Для позиций с промокодами отмена заказа невозможна."""
        voucher_prod = Product.objects.create(
            slug='voucher-prod',
            name='Подарочная карта',
            category='Подарки',
            price=500,
            product_type='digital',
            is_general_offer=True
        )
        batch = VoucherBatch.objects.create(product=voucher_prod, batch_name='Test batch')
        VoucherCode.objects.create(product=voucher_prod, batch=batch, code='TEST-CODE-001')

        order = OrderService.checkout(self.employee, [{'product_id': voucher_prod.id, 'quantity': 1}])
        assert order.status == 'completed'
        assert not order.can_be_cancelled()

        with pytest.raises(Exception, match='промокодами отмена заказа невозможна'):
            OrderService.cancel_order(order.id, self.employee)
