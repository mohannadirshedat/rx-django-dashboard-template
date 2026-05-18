from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Create UserProfile rows for users that do not have one."

    def handle(self, *args, **options):
        created = 0
        for user in User.objects.all():
            _, was_created = UserProfile.objects.get_or_create(user=user)
            if was_created:
                created += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Ensured profiles for {User.objects.count()} user(s); "
                f"created {created} new profile(s)."
            )
        )
