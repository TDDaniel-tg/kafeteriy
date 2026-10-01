from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class CatalogSection(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, default='ShoppingBag')
    order = models.PositiveIntegerField(default=0)
    allowed_segments = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = 'Раздел витрины'
        verbose_name_plural = 'Разделы витрины'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class CatalogCategory(models.Model):
    section = models.ForeignKey(CatalogSection, on_delete=models.SET_NULL, null=True, blank=True, related_name='categories')
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('physical', 'Физический товар'),
        ('digital', 'Цифровой товар / сертификат'),
        ('virtual_card', 'Виртуальная банковская карта'),
        ('doc_benefit', 'Льгота с подтверждающими документами'),
        ('gift_service', 'Подарочный сервис (Giftery/ПВК)'),
        ('booked_service', 'Услуга по записи'),
        ('accommodation', 'Проживание / база отдыха'),
        ('education', 'Обучение и сертификация'),
        ('vacation_days', 'Дополнительный день отпуска'),
        ('flexible_schedule', 'Гибкий график (нефинансовая льгота)'),
    ]

    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, default='Обучение')
    supplier = models.CharField(max_length=150, default='Кафетерий льгот')
    price = models.PositiveIntegerField(default=1000)
    image = models.URLField(max_length=500, blank=True, default='')
    tag = models.CharField(max_length=50, blank=True, default='')
    product_type = models.CharField(max_length=30, choices=PRODUCT_TYPE_CHOICES, default='digital')
    description = models.TextField()
    terms = models.TextField(blank=True, default='')
    pdf_attachment = models.FileField(upload_to='catalog_pdfs/', null=True, blank=True)
    is_general_offer = models.BooleanField(default=False)  # For VIP role access
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)  # ФТ-КАТ.4
    requires_approval = models.BooleanField(default=False)
    approver_type = models.CharField(max_length=20, default='none', choices=[('none', 'Не требуется'), ('manager', 'Руководитель'), ('hr', 'HR'), ('both', 'Руководитель и HR')])
    available_seats = models.IntegerField(null=True, blank=True)
    min_booking_days = models.PositiveIntegerField(default=0)  # For accommodation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Позиция каталога'
        verbose_name_plural = 'Позиции каталога'
        ordering = ['-created_at']

    def clean(self):
        # ФТ-КАТ.4: удаление позиции с активными заказами запрещено
        pass

    def delete(self, *args, **kwargs):
        from apps.orders.models import OrderItem
        has_active_orders = OrderItem.objects.filter(product=self, order__status__in=['created', 'pending_approval', 'processing']).exists()
        if has_active_orders:
            raise ValidationError("Удаление позиции с активными заказами запрещено. Используйте архивацию.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.price} б.)"

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    custom_data = models.JSONField(default=dict, blank=True)

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    class Meta:
        unique_together = ('cart', 'product')
