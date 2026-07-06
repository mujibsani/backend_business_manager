from django.db import models
from core.models import TimeStampedModel


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name