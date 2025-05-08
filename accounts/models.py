from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db import models
import pycountry


class User(AbstractUser):
    email = models.EmailField(unique=True)
    COUNTRY_CHOICES = [(country.name, country.name) for country in pycountry.countries]
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, blank=True, null=True)
    age=models.IntegerField(blank=True, null=True)
    theme=models.BooleanField(default=0)
    REQUIRED_FIElDS=['country']
    def __str__(self):
        return self.username



class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"