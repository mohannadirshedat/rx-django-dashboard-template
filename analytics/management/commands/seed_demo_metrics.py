import datetime
import random

from django.core.management.base import BaseCommand

from analytics.models import DailyMetric, DevicePeriod, DeviceShare, KpiKey, KpiSnapshot, MetricType


class Command(BaseCommand):
    help = "Seed demo KPI, daily metric, and device share data for the overview page."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing analytics data before seeding.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            KpiSnapshot.objects.all().delete()
            DailyMetric.objects.all().delete()
            DeviceShare.objects.all().delete()

        if KpiSnapshot.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Analytics data already exists. Use --clear to re-seed."
                )
            )
            return

        kpi_defaults = {
            KpiKey.USERS: (4200, 3000),
            KpiKey.REVENUE: (12000, 15000),
            KpiKey.ORDERS: (300, 250),
        }
        for key, (value, previous) in kpi_defaults.items():
            KpiSnapshot.objects.create(
                key=key,
                value=value,
                previous_value=previous,
            )

        today = datetime.date.today()
        for metric_type, chart_key in (
            (MetricType.USERS, "Users"),
            (MetricType.REVENUE, "Revenue"),
            (MetricType.ORDERS, "Orders"),
        ):
            for i in range(30, -1, -1):
                day = today - datetime.timedelta(days=i)
                if metric_type == MetricType.REVENUE:
                    value = random.randint(1000, 5000)
                else:
                    value = random.randint(100, 500)
                DailyMetric.objects.create(
                    metric_type=metric_type,
                    date=day,
                    value=value,
                )

        monthly_devices = [
            ("Desktop", 23, "var(--blue-8)"),
            ("Mobile", 47, "var(--green-8)"),
            ("Tablet", 25, "var(--purple-8)"),
            ("Other", 5, "var(--red-8)"),
        ]
        yearly_devices = [
            ("Desktop", 34, "var(--blue-8)"),
            ("Mobile", 46, "var(--green-8)"),
            ("Tablet", 21, "var(--purple-8)"),
            ("Other", 9, "var(--red-8)"),
        ]
        for name, value, fill in monthly_devices:
            DeviceShare.objects.create(
                name=name,
                value=value,
                period=DevicePeriod.MONTHLY,
                fill=fill,
            )
        for name, value, fill in yearly_devices:
            DeviceShare.objects.create(
                name=name,
                value=value,
                period=DevicePeriod.YEARLY,
                fill=fill,
            )

        self.stdout.write(self.style.SUCCESS("Seeded demo analytics data."))
