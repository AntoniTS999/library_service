from django.db import models
from rest_framework.exceptions import ValidationError


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "hard"
        SOFT = "soft"

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    cover = models.CharField(max_length=50, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.inventory <= 0:
            raise ValidationError("Inventory must be positive.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Book, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author} in {self.cover} cover: {self.inventory} left"
