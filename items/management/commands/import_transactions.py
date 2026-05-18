import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand

from items.models import Transaction


class Command(BaseCommand):
    help = "Import transactions from items.csv at the project root."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing transactions before import.",
        )

    def handle(self, *args, **options):
        csv_path = Path("items.csv")
        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {csv_path}"))
            return

        if options["clear"]:
            deleted, _ = Transaction.objects.all().delete()
            self.stdout.write(f"Cleared {deleted} existing transaction(s).")

        if Transaction.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Transactions already exist. Use --clear to re-import."
                )
            )
            return

        created = 0
        with csv_path.open(mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                Transaction.objects.create(
                    name=row["name"],
                    payment=Decimal(row["payment"]),
                    date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
                    status=row["status"],
                )
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Imported {created} transaction(s) from {csv_path}.")
        )
