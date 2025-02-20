from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"
