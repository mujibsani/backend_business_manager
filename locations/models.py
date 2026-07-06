from django.db import models
from core.models import TimeStampedModel


class Division(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class District(TimeStampedModel):
    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name="districts"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.division.name})"


class Thana(TimeStampedModel):
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name="thanas"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.district.name})"