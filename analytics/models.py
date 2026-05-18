from django.db import models


class MetricType(models.TextChoices):
    USERS = "users", "Users"
    REVENUE = "revenue", "Revenue"
    ORDERS = "orders", "Orders"


class KpiKey(models.TextChoices):
    USERS = "users", "Users"
    REVENUE = "revenue", "Revenue"
    ORDERS = "orders", "Orders"


class KpiSnapshot(models.Model):
    key = models.CharField(max_length=20, choices=KpiKey.choices, unique=True)
    value = models.IntegerField()
    previous_value = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "KPI snapshots"

    def __str__(self) -> str:
        return f"{self.key}: {self.value}"


class DailyMetric(models.Model):
    metric_type = models.CharField(max_length=20, choices=MetricType.choices)
    date = models.DateField()
    value = models.IntegerField()

    class Meta:
        ordering = ("date",)
        unique_together = ("metric_type", "date")

    def __str__(self) -> str:
        return f"{self.metric_type} @ {self.date}: {self.value}"


class DevicePeriod(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"


class DeviceShare(models.Model):
    name = models.CharField(max_length=50)
    value = models.IntegerField()
    period = models.CharField(max_length=20, choices=DevicePeriod.choices)
    fill = models.CharField(max_length=50, default="var(--gray-8)")

    class Meta:
        unique_together = ("name", "period")

    def __str__(self) -> str:
        return f"{self.name} ({self.period}): {self.value}%"
