from django.db import models
from django.conf import settings

class CharityFund(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    logo = models.URLField(blank=True, default='')
    website = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Donation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')
    fund = models.ForeignKey(CharityFund, on_delete=models.PROTECT, related_name='donations')
    amount = models.PositiveIntegerField()
    company_match = models.PositiveIntegerField(default=0)  # ФТ-СОЦ.5: множитель компании
    certificate_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def total_impact(self):
        return self.amount + self.company_match

class TeamPot(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    target_points = models.PositiveIntegerField()
    collected_points = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.collected_points}/{self.target_points} б.)"

class TeamPotContribution(models.Model):
    pot = models.ForeignKey(TeamPot, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class SocialProject(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
