from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.settings_platform.models import PlatformSetting
from apps.points.models import PointAccount, PointLot, PointTransaction
from apps.catalog.models import CatalogSection, CatalogCategory, Product
from apps.orders.models import Order, OrderItem, OrderApproval, OrderStatusHistory
from apps.campaigns.models import SelectionWindow
from apps.health_dms.models import DMSProgram, EmployeeDMSPolicy, FamilyMemberDMS
from apps.social import models as social_models
from apps.comms import models as comms_models
from apps.surveys_gamification import models as sg_models
from apps.support import models as support_models
from apps.integrations import models as int_models
from apps.vouchers.models import VoucherBatch, VoucherCode
from apps.audit.models import AnomalyRule, AnomalyTicket

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds database with realistic demo data for Cafeteria of Benefits'

    def handle(self, *args, **options):
        self.stdout.write("Seeding platform settings...")
        settings_defaults = [
            ('transfer_commission_pct', 25, 'int', 'Комиссия за перевод между сотрудниками, %'),
            ('transfer_min_amount', 100, 'int', 'Минимальная сумма перевода, б.'),
            ('matching_multiplier', 1.0, 'float', 'Множитель корпоративного софинансирования благотворительности'),
            ('expiration_months', 12, 'int', 'Срок сгорания сгораемых баллов, мес.'),
            ('point_ruble_rate', 1.0, 'float', 'Стоимость 1 балла в рублях для бухгалтерских выгрузок'),
            ('manual_accrual_ceiling', 10000, 'int', 'Потолок разового ручного начисления баллов администратором'),
            ('support_sla_hours', 24, 'int', 'Нормативный срок реакции поддержки (SLA), часов'),
            ('notification_expiring_days', [30, 7], 'json', 'Дни заблаговременных уведомлений о сгорании баллов'),
            ('section_lottery_enabled', True, 'bool', 'Включение раздела «Лотерея»'),
            ('section_team_pot_enabled', True, 'bool', 'Включение раздела «Командные сборы»'),
            ('section_transfer_enabled', True, 'bool', 'Включение раздела «Перевод баллов»'),
            ('section_charity_enabled', True, 'bool', 'Включение раздела «Благотворительность»'),
            ('section_social_projects_enabled', True, 'bool', 'Включение раздела «Соцпроекты»'),
            ('section_starter_pack_enabled', True, 'bool', 'Включение раздела «Стартовый пакет»'),
            ('section_balance_wheel_enabled', True, 'bool', 'Включение раздела «Колесо баланса»'),
            ('section_tour_enabled', True, 'bool', 'Включение раздела «Тур»'),
        ]
        for key, val, vtype, desc in settings_defaults:
            if not PlatformSetting.objects.filter(key=key).exists():
                PlatformSetting.set_setting(key, val, comment='Инициализация')

        self.stdout.write("Seeding users & roles...")
        users_data = [
            {
                'username': 'morozova', 'first_name': 'Анна', 'last_name': 'Морозова', 'middle_name': 'Сергеевна',
                'email': 'a.morozova@company.ru', 'role': 'employee', 'department': 'Продуктовая команда', 'grade': 'Middle',
                'balance': 6500, 'burnable': 800, 'non_burnable': 5700, 'phone': '+7 (999) 111-22-33',
                'hire_date': date(2022, 9, 20), 'birth_date': date(1994, 8, 12), 'gender': 'female', 'city': 'Москва'
            },
            {
                'username': 'sokolov', 'first_name': 'Михаил', 'last_name': 'Соколов', 'middle_name': 'Александрович',
                'email': 'm.sokolov@company.ru', 'role': 'employee', 'department': 'Разработка', 'grade': 'Senior',
                'balance': 8200, 'burnable': 1200, 'non_burnable': 7000, 'phone': '+7 (999) 222-33-44',
                'hire_date': date(2021, 3, 15), 'birth_date': date(1990, 5, 20), 'gender': 'male', 'city': 'Санкт-Петербург'
            },
            {
                'username': 'volkova', 'first_name': 'Екатерина', 'last_name': 'Волкова', 'middle_name': 'Игоревна',
                'email': 'e.volkova@company.ru', 'role': 'employee', 'department': 'Маркетинг', 'grade': 'Middle',
                'balance': 3750, 'burnable': 500, 'non_burnable': 3250, 'phone': '+7 (999) 333-44-55',
                'hire_date': date(2023, 1, 10), 'birth_date': date(1996, 11, 4), 'gender': 'female', 'city': 'Москва'
            },
            {
                'username': 'kozlov', 'first_name': 'Дмитрий', 'last_name': 'Козлов', 'middle_name': 'Валерьевич',
                'email': 'd.kozlov@company.ru', 'role': 'vip', 'department': 'Финансы', 'grade': 'Lead',
                'balance': 11000, 'burnable': 0, 'non_burnable': 11000, 'phone': '+7 (999) 444-55-66',
                'hire_date': date(2019, 6, 1), 'birth_date': date(1985, 2, 17), 'gender': 'male', 'city': 'Москва'
            },
            {
                'username': 'petrova', 'first_name': 'Мария', 'last_name': 'Петрова', 'middle_name': 'Алексеевна',
                'email': 'm.petrova@company.ru', 'role': 'hr', 'department': 'HR', 'grade': 'Middle',
                'balance': 5400, 'burnable': 400, 'non_burnable': 5000, 'phone': '+7 (999) 555-66-77',
                'hire_date': date(2022, 11, 1), 'birth_date': date(1992, 9, 30), 'gender': 'female', 'city': 'Москва'
            },
            {
                'username': 'smirnova', 'first_name': 'Ольга', 'last_name': 'Смирнова', 'middle_name': 'Николаевна',
                'email': 'o.smirnova@company.ru', 'role': 'maternity', 'department': 'Маркетинг', 'grade': 'Middle',
                'balance': 4200, 'burnable': 0, 'non_burnable': 4200, 'phone': '+7 (999) 666-77-88',
                'hire_date': date(2020, 4, 1), 'birth_date': date(1993, 7, 14), 'gender': 'female', 'city': 'Москва'
            },
            {
                'username': 'mikhailova', 'first_name': 'Елена', 'last_name': 'Михайлова', 'middle_name': 'Викторовна',
                'email': 'e.mikhailova@company.ru', 'role': 'admin', 'department': 'Администрация', 'grade': 'Head',
                'balance': 15000, 'burnable': 0, 'non_burnable': 15000, 'phone': '+7 (999) 777-88-99',
                'hire_date': date(2018, 1, 1), 'birth_date': date(1982, 10, 5), 'gender': 'female', 'city': 'Москва'
            },
            {
                'username': 'vasiliev', 'first_name': 'Иван', 'last_name': 'Васильев', 'middle_name': 'Олегович',
                'email': 'i.vasiliev@company.ru', 'role': 'exclusion', 'department': 'Склад', 'grade': 'Junior',
                'balance': 0, 'burnable': 0, 'non_burnable': 0, 'phone': '+7 (999) 888-99-00',
                'hire_date': date(2024, 2, 1), 'birth_date': date(1999, 12, 1), 'gender': 'male', 'city': 'Казань'
            },
        ]

        now = timezone.now()
        for udata in users_data:
            user, created = User.objects.get_or_create(username=udata['username'])
            user.first_name = udata['first_name']
            user.last_name = udata['last_name']
            user.middle_name = udata['middle_name']
            user.email = udata['email']
            user.role = udata['role']
            user.department = udata['department']
            user.grade = udata['grade']
            user.phone = udata['phone']
            user.hire_date = udata['hire_date']
            user.birth_date = udata['birth_date']
            user.gender = udata['gender']
            user.city = udata['city']
            user.delivery_address = f"г. {udata['city']}, ул. Ленина, д. 10, кв. 42"
            if udata['role'] == 'admin':
                user.is_staff = True
                user.is_superuser = True
            user.set_password('demo1234')
            user.save()

            # Point Account & Lots
            acc, _ = PointAccount.objects.get_or_create(user=user)
            acc.total_balance = udata['balance']
            acc.save()

            if udata['burnable'] > 0:
                PointLot.objects.get_or_create(
                    user=user,
                    lot_type='burnable',
                    initial_amount=udata['burnable'],
                    current_balance=udata['burnable'],
                    expires_at=now + timedelta(days=30),
                    comment='Сгораемые баллы 2025'
                )

            if udata['non_burnable'] > 0:
                PointLot.objects.get_or_create(
                    user=user,
                    lot_type='non_burnable',
                    initial_amount=udata['non_burnable'],
                    current_balance=udata['non_burnable'],
                    comment='Несгораемые баллы'
                )

        # Products
        self.stdout.write("Seeding catalog products...")
        prods = [
            {
                'slug': 'english', 'name': 'Английский для жизни и работы', 'category': 'Обучение',
                'supplier': 'Skyeng', 'price': 2400, 'tag': 'Популярное', 'product_type': 'digital',
                'image': 'https://images.unsplash.com/photo-1493723843671-1d655e66ac1c?w=700&q=80',
                'description': 'Индивидуальные занятия с преподавателем в удобное время. Учитесь в своём темпе и уверенно говорите на английском.',
                'terms': 'Сертификат действителен 1 год. Код придёт на вашу почту сразу после оформления заказа.',
                'is_general_offer': True
            },
            {
                'slug': 'retreat', 'name': 'Выходные на базе отдыха', 'category': 'Отдых',
                'supplier': 'Лес и озеро', 'price': 3200, 'tag': 'Новинка', 'product_type': 'accommodation',
                'image': 'https://images.unsplash.com/photo-1619688137428-851529e61a0f?w=700&q=80',
                'description': 'Два дня вдали от городской суеты: уютный домик у озера, прогулки по лесу и время для себя.',
                'terms': 'Бронирование не позднее чем за 7 дней до заезда. Возможно проживание с семьей до 4 человек.',
                'min_booking_days': 7,
                'is_general_offer': True
            },
            {
                'slug': 'gift', 'name': 'Подарочная карта Giftery', 'category': 'Подарки',
                'supplier': 'Giftery', 'price': 1500, 'tag': 'Хит', 'product_type': 'gift_service',
                'image': 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=700&q=80',
                'description': 'Один сертификат — сотни любимых магазинов. Порадуйте себя или близких подарком на выбор.',
                'terms': 'Код направляется на email. Для позиций с промокодами отмена невозможна (ФТ-ЗАК.6).',
                'is_general_offer': True
            },
            {
                'slug': 'psych', 'name': 'Консультация психолога', 'category': 'Здоровье',
                'supplier': 'Ясно', 'price': 1800, 'product_type': 'booked_service',
                'image': 'https://images.unsplash.com/photo-1607835017779-c176b83b2dd8?w=700&q=80',
                'description': 'Бережная поддержка профессионального психолога онлайн. Выберите удобное время для первой встречи.',
                'terms': 'Сессия 50 минут по видеосвязи. Запись не менее чем за 24 часа.',
                'is_general_offer': False
            },
            {
                'slug': 'dms', 'name': 'ДМС Расширенный', 'category': 'Здоровье',
                'supplier': 'Ингосстрах', 'price': 3800, 'product_type': 'digital',
                'image': 'https://images.unsplash.com/photo-1615800001716-c53dd05bf4b8?w=700&q=80',
                'description': 'Расширенная программа заботы о здоровье: консультации врачей, диагностика и стоматология.',
                'terms': 'Полис действует в течение года. Доступно прикрепление родственников.',
                'is_general_offer': False
            },
            {
                'slug': 'holiday', 'name': 'Дополнительный день отпуска', 'category': 'Отдых',
                'supplier': 'Кафетерий льгот', 'price': 1200, 'product_type': 'vacation_days',
                'image': 'https://images.unsplash.com/photo-1676948242081-17ba7600851a?w=700&q=80',
                'description': 'Подарите себе ещё один день для отдыха, путешествия или времени с близкими.',
                'terms': 'Требуется обязательное согласование руководителем и HR службой. Блокируется при неотгулянном основном отпуске.',
                'requires_approval': True, 'approver_type': 'both',
                'is_general_offer': True
            },
            {
                'slug': 'kids', 'name': 'Кружки для детей', 'category': 'Семья',
                'supplier': 'Алгоритмика', 'price': 2100, 'product_type': 'booked_service',
                'image': 'https://images.unsplash.com/photo-1509062522246-3755977927d7?w=700&q=80',
                'description': 'Творческие и образовательные занятия для детей: выбирайте то, что нравится именно вашему ребёнку.',
                'terms': 'Курс на 4 занятия онлайн или очно в филиале школы.',
                'is_general_offer': True
            },
            {
                'slug': 'conference', 'name': 'Сертификат на конференцию', 'category': 'Обучение',
                'supplier': 'Контур', 'price': 2900, 'product_type': 'doc_benefit',
                'image': 'https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=700&q=80',
                'description': 'Посетите профессиональное событие и привезите новые идеи своей команде.',
                'terms': 'Для подтверждения требуется прикрепить чек или договор об участии в конференции.',
                'requires_approval': True, 'approver_type': 'manager',
                'is_general_offer': True
            },
        ]
        for p in prods:
            Product.objects.update_or_create(slug=p['slug'], defaults=p)

        # Voucher Codes
        gift_prod = Product.objects.get(slug='gift')
        batch, _ = VoucherBatch.objects.get_or_create(product=gift_prod, batch_name='Партия Giftery Сентябрь 2025', defaults={'total_count': 10, 'threshold_alert': 3})
        for i in range(1, 11):
            VoucherCode.objects.get_or_create(product=gift_prod, code=f"GIFT-2025-{i:03d}", defaults={'batch': batch})

        # Selection Window
        self.stdout.write("Seeding selection window...")
        SelectionWindow.objects.get_or_create(
            name="Осенний выбор льгот 2025",
            defaults={
                'start_date': now - timedelta(days=10),
                'end_date': now + timedelta(days=21),
                'rule_mode': 'inform',
                'is_active': True,
                'description': 'Период выбора льгот для всех подразделений компании.'
            }
        )

        # DMS Program & Policy
        self.stdout.write("Seeding DMS programs...")
        dms_std, _ = DMSProgram.objects.get_or_create(
            name="ДМС Стандарт",
            defaults={
                'insurer': 'Ингосстрах',
                'description': 'Базовая программа добровольного медицинского страхования.',
                'price_points': 3000,
                'is_default': True,
                'includes': [
                    "Приём терапевта и профильных специалистов",
                    "Диагностика и лабораторные исследования",
                    "Телемедицина 24/7",
                    "Экстренная медицинская помощь"
                ],
                'excludes': [
                    "Косметологические процедуры",
                    "Плановая госпитализация",
                    "Стоматология (можно подключить отдельно)"
                ],
                'clinics': [
                    "Клиника «Медси» · ул. Красная, 14",
                    "Клиника «Семейная» · пр. Мира, 28",
                    "Диагностический центр «Здоровье»"
                ]
            }
        )
        anna = User.objects.get(username='morozova')
        EmployeeDMSPolicy.objects.get_or_create(
            user=anna,
            defaults={
                'program': dms_std,
                'policy_number': 'ИНГ-2025-98124',
                'status': 'active',
                'valid_until': date(2025, 12, 31)
            }
        )

        # Initial orders
        self.stdout.write("Seeding orders...")
        eng_prod = Product.objects.get(slug='english')
        psych_prod = Product.objects.get(slug='psych')

        order_samples = [
            {'num': 'КЛ-24051', 'prod': eng_prod, 'sum': 2400, 'status': 'processing'},
            {'num': 'КЛ-24012', 'prod': gift_prod, 'sum': 1500, 'status': 'completed'},
            {'num': 'КЛ-23984', 'prod': psych_prod, 'sum': 1800, 'status': 'pending_approval'},
            {'num': 'КЛ-23810', 'prod': eng_prod, 'sum': 3000, 'status': 'completed'},
        ]
        for o in order_samples:
            ord_obj, _ = Order.objects.get_or_create(
                order_number=o['num'],
                defaults={
                    'user': anna,
                    'status': o['status'],
                    'total_points': o['sum'],
                    'recipient_name': anna.full_name,
                    'recipient_email': anna.email
                }
            )
            OrderItem.objects.get_or_create(order=ord_obj, product=o['prod'], defaults={'price': o['prod'].price, 'quantity': 1})
            OrderStatusHistory.objects.get_or_create(order=ord_obj, status=o['status'], defaults={'comment': 'Инициализация демо-данных'})

        # Social & Charity
        self.stdout.write("Seeding charity funds...")
        funds = [
            {'name': 'Фонд «Подари жизнь»', 'description': 'Помощь детям с онкологическими и гематологическими заболеваниями.'},
            {'name': 'Фонд «Нужна помощь»', 'description': 'Развитие благотворительности и системная поддержка социальных инициатив.'},
        ]
        for f in funds:
            social_models.CharityFund.objects.get_or_create(name=f['name'], defaults=f)

        # Comms: News & Banners
        self.stdout.write("Seeding news and banners...")
        comms_models.NewsArticle.objects.get_or_create(
            title="Осень — время для маленьких путешествий",
            defaults={
                'kicker': 'НОВОЕ В КАФЕТЕРИИ',
                'summary': 'В каталоге появились уютные выходные на базе отдыха «Лес и озеро».',
                'content': 'Проведите незабываемые выходные среди осеннего леса на берегу живописного озера. Бронируйте проживание за баллы!',
                'image': 'https://images.unsplash.com/photo-1619688137428-851529e61a0f?w=1100&q=80',
                'is_published': True
            }
        )
        comms_models.Notification.objects.get_or_create(
            user=anna,
            title="Окно выбора открыто до 15 октября",
            defaults={'message': 'Успейте выбрать важные для вас льготы на новый период!', 'notification_type': 'info'}
        )
        comms_models.Notification.objects.get_or_create(
            user=anna,
            title="800 баллов сгорят через 30 дней",
            defaults={'message': 'Обратите внимание: сгораемые баллы действуют до 24 октября.', 'notification_type': 'warning'}
        )

        # Surveys & Lottery
        self.stdout.write("Seeding surveys & lottery...")
        sg_models.Survey.objects.get_or_create(
            title="Что для вас важно в льготах?",
            defaults={
                'description': 'Помогите сделать кафетерий ещё полезнее для каждого.',
                'questions': [
                    {'id': 1, 'text': 'Какие категории льгот вам наиболее интересны?', 'type': 'multi_choice', 'options': ['Здоровье', 'Обучение', 'Отдых', 'Подарки']},
                    {'id': 2, 'text': 'Оцените удобство использования кафетерия льгот от 1 до 5', 'type': 'rating', 'options': ['1', '2', '3', '4', '5']}
                ]
            }
        )
        sg_models.Lottery.objects.get_or_create(
            title="Осенняя лотерея 2025",
            defaults={
                'prize_pool_points': 30000,
                'draw_date': date(2025, 10, 15),
                'is_drawn': False
            }
        )

        # Support Tickets
        self.stdout.write("Seeding support tickets...")
        support_models.SupportTicket.objects.get_or_create(
            ticket_number="КЛ-1842",
            defaults={
                'user': anna,
                'subject': 'Вопрос по сертификату Giftery',
                'description': 'Здравствуйте! Заказ оформлен, подскажите, когда поступит код на email?',
                'status': 'in_progress',
                'sla_deadline': now + timedelta(hours=2)
            }
        )
        support_models.SupportTicket.objects.get_or_create(
            ticket_number="КЛ-1720",
            defaults={
                'user': anna,
                'subject': 'Изменение персональных данных',
                'description': 'Прошу обновить адрес доставки для физических заказов.',
                'status': 'resolved',
                'resolved_at': now - timedelta(days=5)
            }
        )

        # Integrations
        self.stdout.write("Seeding integration channels...")
        channels = [
            {'name': '1С:ЗУП', 'channel_type': '1c_zup', 'status': 'available', 'is_mock': True, 'response_time_ms': 45},
            {'name': 'Корпоративный SSO', 'channel_type': 'sso', 'status': 'available', 'is_mock': True, 'response_time_ms': 28},
            {'name': 'Почтовый шлюз SMTP', 'channel_type': 'smtp', 'status': 'available', 'is_mock': True, 'response_time_ms': 120},
            {'name': 'Giftery API', 'channel_type': 'giftery', 'status': 'unavailable', 'is_mock': True, 'response_time_ms': 0},
            {'name': 'ПВК / Prostodar', 'channel_type': 'prostodar', 'status': 'available', 'is_mock': True, 'response_time_ms': 65},
            {'name': 'Бухгалтерия (1C/Excel)', 'channel_type': 'accounting', 'status': 'available', 'is_mock': True, 'response_time_ms': 15},
        ]
        for c in channels:
            int_models.IntegrationChannel.objects.get_or_create(name=c['name'], defaults=c)

        # Anomaly Rules & Tickets
        rule, _ = AnomalyRule.objects.get_or_create(
            name="Превышение лимита списаний",
            defaults={'rule_type': 'daily_spend_limit', 'threshold': 10000.0}
        )
        AnomalyTicket.objects.get_or_create(
            ticket_number="АН-101",
            defaults={
                'rule': rule,
                'user': anna,
                'severity': 'low',
                'description': 'Пользователь оформил заказ на сумму свыше 5 000 б.',
                'status': 'detected'
            }
        )

        self.stdout.write(self.style.SUCCESS("All demo data seeded successfully!"))
