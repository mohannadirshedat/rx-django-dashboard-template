from django.db import models


class TransactionStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    COMPLETED = "Completed", "Completed"
    CANCELED = "Canceled", "Canceled"


class Transaction(models.Model):
    name = models.CharField(max_length=200)
    payment = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )

    class Meta:
        ordering = ("-date",)

    def __str__(self) -> str:
        return self.name
