from django.db import models

from base.models import BaseModel


class Product(BaseModel):
    name = models.CharField(
        max_length=200, unique=True
    )  # можно сделать джин, но по хорошему поиск будет через эластик
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
