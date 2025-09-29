from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portfolio.models import Profile

class Command(BaseCommand):
    help = 'Create Profile rows for existing users that lack one'

    def handle(self, *args, **options):
        created = 0
        for u in User.objects.all():
            p, c = Profile.objects.get_or_create(user=u)
            if c:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created} profiles'))
