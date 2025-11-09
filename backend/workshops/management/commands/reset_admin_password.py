from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Reset admin password'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username of the admin user (default: admin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='New password for the admin user'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        password = options['password']

        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Wachtwoord voor gebruiker "{username}" is succesvol gereset!'
                )
            )
        except User.DoesNotExist:
            # Als de gebruiker niet bestaat, maak een nieuwe superuser aan
            self.stdout.write(
                self.style.WARNING(
                    f'Gebruiker "{username}" bestaat niet. Aanmaken van nieuwe superuser...'
                )
            )
            user = User.objects.create_superuser(
                username=username,
                password=password,
                email='admin@example.com'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser "{username}" is succesvol aangemaakt met het opgegeven wachtwoord!'
                )
            )
