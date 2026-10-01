from django.db import models
from django.conf import settings
from django.utils import timezone

class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    kicker = models.CharField(max_length=100, blank=True, default='')
    summary = models.TextField(blank=True, default='')
    content = models.TextField()
    image = models.URLField(max_length=500, blank=True, default='')
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

class NewsComment(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_moderated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PromoBanner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True, default='')
    image = models.URLField(max_length=500, blank=True, default='')
    link_url = models.CharField(max_length=255, blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

class PromoCampaign(models.Model):
    name = models.CharField(max_length=150)
    target_segment = models.CharField(max_length=100, default='Все сотрудники')
    cashback_pct = models.PositiveIntegerField(default=10)
    budget_limit = models.PositiveIntegerField(default=50000)
    budget_spent = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    @property
    def is_budget_exhausted(self):
        return self.budget_spent >= self.budget_limit

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, default='info', choices=[
        ('info', 'Информация'),
        ('success', 'Успех'),
        ('warning', 'Предупреждение'),
        ('danger', 'Ошибка'),
    ])
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
