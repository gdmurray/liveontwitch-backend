from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Help Text'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', type=str)

    def handle(self, *args, **options):
        print(options)