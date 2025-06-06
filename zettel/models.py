import os
from django.db import models
from django.conf import settings


# Create your models here.

class Kandidatur(models.Model):
    GEWAEHLT_CHOICES = [
        ('noch nicht', 'Noch nicht abgestimmt'),
        ('ja', 'Gewählt'),
        ('nein', 'Nicht Gewählt'),
        ('zurueckgezogen', 'Kandidatur zurückgezogen'),
    ]

    BESTAETIGT_CHOICES = [
        ('ja', 'Ja'),
        ('nein', 'Nein'),
    ]

    gewaehlt = models.CharField(max_length=50, choices=GEWAEHLT_CHOICES, default='noch nicht')
    gremium = models.CharField(max_length=225)
    lesung = models.CharField(max_length=225, blank=True)
    first_name = models.CharField(max_length=225, blank=True)
    last_name = models.CharField(max_length=225, blank=True)
    bestaetigt = models.CharField(max_length=50, choices=BESTAETIGT_CHOICES, default='nein')
    fakultaetFachschaft = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name.upper()}, {self.gremium}"

    if not settings.DEBUG:
        class Meta:
            managed = False
            db_table = "vs_kandidatur"
