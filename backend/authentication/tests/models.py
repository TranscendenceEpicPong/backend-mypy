from django.db import models


class Dummy(models.Model):
    text = models.TextField()
    objects = models.Manager()