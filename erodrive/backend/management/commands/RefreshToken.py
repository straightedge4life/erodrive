from django.core.management.base import BaseCommand
from repositories.OneDrive import OneDrive


class Command(BaseCommand):

    def handle(self, *args, **options):
        one = OneDrive()
        one.get_token()
        print('Refresh token successful.')

