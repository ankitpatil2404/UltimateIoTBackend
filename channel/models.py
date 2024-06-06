"""
code written by shubham waje
github -> https://www.github.com/wajeshubham
"""
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


# Create your models here.


class Channel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    description = models.TextField(max_length=250, blank=True)
    fields = ArrayField(models.CharField(max_length=20), size=16)
    values = ArrayField(models.IntegerField(default=0), size=16)
    created_at = models.DateTimeField(auto_now_add=True)
    read_api_key = models.CharField(max_length=40)
    write_api_key = models.CharField(max_length=40)

    def __str__(self):
        return self.name
