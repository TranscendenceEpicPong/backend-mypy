from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
import random
from django.contrib.auth.hashers import check_password as django_check_password
from django.contrib.auth.hashers import make_password as django_make_password

class CustomUser(AbstractUser):
    token = models.CharField(max_length=128)
    def check_password(self, raw_password):
        return django_check_password(raw_password, self.password)

@receiver(pre_save, sender=CustomUser)
def pre_save_user(sender, instance, **kwargs):
    # Ajoutez ici votre logique personnalisée
    # par exemple, vérifiez une condition et effectuez une action en conséquence
    instance.password = django_make_password(instance.password)
    instance.token = f"{random.random()}"
