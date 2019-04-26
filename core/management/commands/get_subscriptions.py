from django.core.management.base import BaseCommand
from twitch.utils import get_subscriptions


class Command(BaseCommand):
    help = 'Help Text'

    def handle(self, *args, **options):
        print("Fetching Subscriptions")
        data = get_subscriptions()
        print(data)
