"""
Django Management Command om test nieuwsbrief subscribers aan te maken
"""
from django.core.management.base import BaseCommand
from workshops.models import NewsletterSubscriber


class Command(BaseCommand):
    help = 'Voegt test nieuwsbrief subscribers toe aan de database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Start met aanmaken test nieuwsbrief subscribers...'))

        # Test subscribers data
        subscribers_data = [
            {
                'email': 'jan.janssens@email.be',
                'first_name': 'Jan',
                'last_name': 'Janssens',
                'is_active': True,
                'confirmed': True,
            },
            {
                'email': 'sarah.peeters@gmail.com',
                'first_name': 'Sarah',
                'last_name': 'Peeters',
                'is_active': True,
                'confirmed': True,
            },
            {
                'email': 'thomas.dewit@hotmail.com',
                'first_name': 'Thomas',
                'last_name': 'De Wit',
                'is_active': True,
                'confirmed': True,
            },
            {
                'email': 'laura.vandenbroeck@outlook.be',
                'first_name': 'Laura',
                'last_name': 'Van den Broeck',
                'is_active': True,
                'confirmed': True,
            },
            {
                'email': 'koen.vandenbergh@telenet.be',
                'first_name': 'Koen',
                'last_name': 'Van den Bergh',
                'is_active': True,
                'confirmed': True,
            },
            {
                'email': 'anne.martens@proximus.be',
                'first_name': 'Anne',
                'last_name': 'Martens',
                'is_active': True,
                'confirmed': True,
            },
            {
                'email': 'pieter.claes@skynet.be',
                'first_name': 'Pieter',
                'last_name': 'Claes',
                'is_active': False,  # Uitgeschreven
                'confirmed': True,
            },
            {
                'email': 'jessica.willems@gmail.com',
                'first_name': 'Jessica',
                'last_name': 'Willems',
                'is_active': True,
                'confirmed': False,  # Nog niet bevestigd
            },
        ]

        created_count = 0
        existing_count = 0

        for data in subscribers_data:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data.get('last_name', ''),
                    'is_active': data.get('is_active', True),
                    'confirmed': data.get('confirmed', True),
                }
            )

            if created:
                created_count += 1
                status = "✓ Actief" if subscriber.is_active else "✗ Inactief"
                confirmed = "✓ Bevestigd" if subscriber.confirmed else "⏳ Niet bevestigd"
                self.stdout.write(
                    f'  ✅ {subscriber.email} - {status} - {confirmed}'
                )
            else:
                existing_count += 1
                self.stdout.write(
                    f'  ⚠️  {subscriber.email} - Bestaat al'
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ {created_count} nieuwsbrief subscribers aangemaakt'))
        if existing_count > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  {existing_count} subscribers bestonden al'))

        # Statistieken
        total_active = NewsletterSubscriber.objects.filter(is_active=True).count()
        total_confirmed = NewsletterSubscriber.objects.filter(confirmed=True).count()
        total = NewsletterSubscriber.objects.count()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('📊 Nieuwsbrief Statistieken:'))
        self.stdout.write(f'  Totaal subscribers: {total}')
        self.stdout.write(f'  Actieve subscribers: {total_active}')
        self.stdout.write(f'  Bevestigde subscribers: {total_confirmed}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Klaar! Check het admin panel op /admin/workshops/newslettersubscriber/'))
