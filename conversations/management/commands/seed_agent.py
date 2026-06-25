from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Seeds the default support agent account'

    def handle(self, *args, **options):
        email = 'admin@test.com'
        password = 'admin123'
        username = 'admin'
        
        # Check if user already exists by email
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f"Support agent with email '{email}' already exists."))
            return
            
        # Check if username exists, if so, resolve conflict
        if User.objects.filter(username=username).exists():
            username = 'admin_support'

        # Create superuser so the agent has full admin/staff access
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded support agent: {email} with password: {password}"))
