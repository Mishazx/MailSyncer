import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from dotenv import load_dotenv

load_dotenv()


class Command(BaseCommand):
    help = 'Create a admin and add it to all groups'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            admin_username = os.getenv('DJANGO_ADMIN_USERNAME', 'admin')
            admin_email = os.getenv('DJANGO_ADMIN_EMAIL')
            admin_password = os.getenv('DJANGO_ADMIN_PASSWORD', 'admin')

            # Create the Admin
            User.objects.create_superuser(
                admin_username,
                admin_email,
                admin_password
            )
            self.stdout.write(self.style.SUCCESS('Admin created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin already exists'))
