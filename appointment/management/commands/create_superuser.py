from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
import os

class Command(BaseCommand):
    help = 'Create a superuser with the provided credentials'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not username or not email or not password:
            raise ImproperlyConfigured("Superuser credentials are not set in environment variables")

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully'))
