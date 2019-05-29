from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Help Text'

    def handle(self, *args, **options):
        from core.models import User

        User.objects.create_superuser(
            'admin',
            'gd-murray@hotmail.com',
            'adminpass'
        )
