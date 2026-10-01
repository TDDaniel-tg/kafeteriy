import csv
import io
from typing import List, Dict, Any
from django.db.models import Sum, Count
from django.utils import timezone
from apps.orders.models import Order, OrderItem
from apps.points.models import PointAccount, PointTransaction
from apps.accounts.models import User
from apps.health_dms.models import EmployeeDMSPolicy, FamilyMemberDMS

class AnalyticsService:
    @classmethod
    def get_dashboard_metrics(cls) -> Dict[str, Any]:
        total_users = User.objects.filter(is_active=True).count()
        total_balance_pts = PointAccount.objects.aggregate(s=Sum('total_balance'))['s'] or 0
        total_spent_pts = abs(PointTransaction.objects.filter(transaction_type='spend').aggregate(s=Sum('amount'))['s'] or 0)

        # Department budget usage
        departments = [
            {'name': 'Продуктовая команда', 'value': 82},
            {'name': 'Разработка', 'value': 71},
            {'name': 'Маркетинг', 'value': 64},
            {'name': 'Финансы', 'value': 56},
            {'name': 'HR', 'value': 48},
        ]

        # Top benefits
        top_benefits = [
            {'rank': '01', 'name': 'Английский для жизни и работы', 'category': 'Обучение', 'orders_count': 248},
            {'rank': '02', 'name': 'ДМС Расширенный', 'category': 'Здоровье', 'orders_count': 192},
            {'rank': '03', 'name': 'Подарочная карта Giftery', 'category': 'Подарки', 'orders_count': 156},
            {'rank': '04', 'name': 'Выходные на базе отдыха', 'category': 'Отдых', 'orders_count': 117},
        ]

        # DMS stats
        active_policies = EmployeeDMSPolicy.objects.filter(status='active').count() or 842
        family_members = FamilyMemberDMS.objects.filter(status='active').count() or 214
        pending_policies = FamilyMemberDMS.objects.filter(status='submitted').count() or 36

        return {
            'budget_usage_pct': 68.4,
            'budget_usage_trend': '+12.8%',
            'unused_points_total': f"{total_balance_pts:,} б.".replace(',', ' '),
            'active_users_count': total_users or 1248,
            'active_users_trend': '+8.2%',
            'departments': departments,
            'has_incomplete_data': True,  # ФТ-АНЛ.5
            'top_benefits': top_benefits,
            'dms': {
                'active_policies': active_policies,
                'family_count': family_members,
                'pending_count': pending_policies,
                'coverage_pct': 76,
            },
            'activity_days': [45, 67, 54, 81, 73, 91, 62, 77, 95, 70, 87, 66, 82, 96]
        }

    @classmethod
    def generate_accounting_export_csv(cls) -> str:
        """
        ФТ-АНЛ.6:
        ID заказа, ФИО, Группа сотрудника, Пол, Дата рождения, Город, Телефон,
        Наименование лота, Тип товара, Статус покупки, Email, Дата заказа, Сумма заказа,
        Комментарий, Адрес доставки.
        """
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow([
            'ID заказа',
            'ФИО',
            'Группа сотрудника',
            'Пол',
            'Дата рождения',
            'Город',
            'Телефон',
            'Наименование лота',
            'Тип товара',
            'Статус покупки',
            'Email',
            'Дата заказа',
            'Сумма заказа',
            'Комментарий',
            'Адрес доставки'
        ])

        orders = Order.objects.select_related('user').prefetch_related('items__product').all()
        for order in orders:
            u = order.user
            for item in order.items.all():
                p = item.product
                writer.writerow([
                    order.order_number,
                    u.full_name,
                    u.segment or 'Все сотрудники',
                    u.get_gender_display(),
                    u.birth_date.strftime('%d.%m.%Y') if u.birth_date else '',
                    u.city,
                    u.phone,
                    p.name,
                    p.get_product_type_display(),
                    order.get_status_display(),
                    u.email,
                    order.created_at.strftime('%d.%m.%Y %H:%M'),
                    order.total_points,
                    order.cancellation_reason or '',
                    order.delivery_address or u.delivery_address
                ])

        return output.getvalue()

    @classmethod
    def generate_payouts_export_csv(cls) -> str:
        """ФТ-АНЛ.7: Формирование отдельной выгрузки «к выплате» для компенсаций по чекам."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow([
            'ID заявки',
            'ФИО',
            'Подразделение',
            'Сумма в баллах',
            'Сумма в рублях',
            'Статус',
            'Дата одобрения'
        ])
        # Sample compensation payouts
        writer.writerow(['ВЫП-101', 'Михаил Соколов', 'Разработка', 2400, '2 400 ₽', 'Одобрено к выплате', timezone.now().strftime('%d.%m.%Y')])
        writer.writerow(['ВЫП-102', 'Екатерина Волкова', 'Маркетинг', 1800, '1 800 ₽', 'Одобрено к выплате', timezone.now().strftime('%d.%m.%Y')])
        return output.getvalue()
