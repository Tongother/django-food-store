from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    direction = models.TextField(blank=True, null=True)

class CreditCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='credit_card')
    cardholder_name = models.CharField(max_length=150)
    card_number_secure = models.CharField(max_length=255)
    card_last_four = models.CharField(max_length=4)
    expiration_date = models.CharField(max_length=5)
    card_type = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.card_type} **** {self.card_last_four} ({self.user.username})"