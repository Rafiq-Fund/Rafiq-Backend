from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pictures/', blank=True, null=True)
    verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    address = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.username
