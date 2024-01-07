import random

from django.contrib.auth.models import AbstractUser
from django.db import models


def random_token():
    return random.random()


class EpicPongUser(AbstractUser):
    token = models.CharField(max_length=128, default=random_token)
