from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Sum


class Category(models.Model):
    """Webinar categorie (bijv. Houtbewerking, Metaalbewerking, Kunst)"""
    name = models.CharField('Naam', max_length=100, unique=True)
    slug = models.SlugField('Slug', max_length=100, unique=True)
    description = models.TextField('Beschrijving', blank=True)
    icon = models.CharField(
        'Bootstrap Icon', 
        max_length=50, 
        default='bi-lightbulb',
        help_text='Bootstrap icon class (bijv. bi-cpu, bi-gear, bi-rocket). Zie https://icons.getbootstrap.com/'
    )
    created_at = models.DateTimeField('Aangemaakt op', auto_now_add=True)

    class Meta:
        verbose_name = 'Categorie'
        verbose_name_plural = 'Categorieën'
        ordering = ['name']

    def __str__(self):
        return self.name


class Workshop(models.Model):
    """Webinar model voor alle online webinar informatie"""
    
    STATUS_CHOICES = [
        ('upcoming', 'Binnenkort'),
        ('active', 'Actief'),
        ('full', 'Volzet'),
        ('cancelled', 'Geannuleerd'),
        ('completed', 'Afgelopen'),
    ]

    # Basis informatie
    title = models.CharField('Titel', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True)
    description = models.TextField('Beschrijving')
    short_description = models.CharField('Korte beschrijving', max_length=300, blank=True)
    
    # Categorie
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Categorie',
        related_name='workshops'
    )
    
    # Datum en tijd
    start_datetime = models.DateTimeField('Start datum & tijd')
    end_datetime = models.DateTimeField('Eind datum & tijd')
    duration_hours = models.DecimalField(
        'Duur (uren)', 
        max_digits=4, 
        decimal_places=1,
        validators=[MinValueValidator(0.5)]
    )
    
    # Online meeting details
    meeting_url = models.URLField(
        'Teams Meeting URL',
        max_length=500,
        blank=True,
        help_text='Link naar de Microsoft Teams meeting'
    )
    meeting_id = models.CharField(
        'Meeting ID',
        max_length=100,
        blank=True,
        help_text='Optioneel meeting ID voor deelnemers'
    )
    meeting_password = models.CharField(
        'Meeting Wachtwoord',
        max_length=100,
        blank=True,
        help_text='Optioneel wachtwoord voor de meeting'
    )
    
    # Capaciteit
    max_participants = models.PositiveIntegerField(
        'Maximum aantal deelnemers',
        validators=[MinValueValidator(1), MaxValueValidator(500)]
    )
    min_participants = models.PositiveIntegerField(
        'Minimum aantal deelnemers',
        default=1,
        validators=[MinValueValidator(1)]
    )
    
    # Prijzen
    price = models.DecimalField(
        'Prijs per persoon (€)', 
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Extra informatie
    materials_included = models.BooleanField('Materialen inbegrepen', default=True)
    requirements = models.TextField('Vereisten', blank=True, help_text='Bijv. ervaring, benodigde software, etc.')
    what_to_bring = models.TextField('Wat meenemen', blank=True, help_text='Benodigde materialen voor thuis')
    
    # Media
    image = models.ImageField('Afbeelding', upload_to='workshops/', blank=True, null=True)
    
    # Status en zichtbaarheid
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='upcoming')
    is_active = models.BooleanField('Actief', default=True)
    featured = models.BooleanField('Uitgelicht', default=False)
    
    # Instructor
    instructor_name = models.CharField('Instructeur naam', max_length=200)
    instructor_bio = models.TextField('Instructeur bio', blank=True)
    
    # Metadata
    created_at = models.DateTimeField('Aangemaakt op', auto_now_add=True)
    updated_at = models.DateTimeField('Geüpdatet op', auto_now=True)

    class Meta:
        verbose_name = 'Webinar'
        verbose_name_plural = 'Webinars'
        ordering = ['-start_datetime']
        indexes = [
            models.Index(fields=['start_datetime']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        """String representatie met fallback voor title en start_datetime"""
        title = self.title or "Webinar"
        if getattr(self, "start_datetime", None):
            return f"{title} - {self.start_datetime.strftime('%d/%m/%Y')}"
        return title

    @property
    def available_spots(self):
        """
        Aantal beschikbare plaatsen.
        Werkt ook wanneer de instance nog niet is opgeslagen (pk is None).
        """
        total = self.max_participants or 0
        
        # Als de webinar nog geen PK heeft, kunnen we geen relaties opvragen
        if not self.pk:
            return total
        
        confirmed = (
            self.bookings
            .filter(status="confirmed")
            .aggregate(total=Sum("number_of_participants"))
            .get("total") or 0
        )
        
        remaining = total - confirmed
        return max(remaining, 0)

    @property
    def is_full(self):
        """Check of webinar vol is"""
        return self.available_spots <= 0

    @property
    def is_upcoming(self):
        """Check of webinar in de toekomst is"""
        return self.start_datetime > timezone.now()

    def save(self, *args, **kwargs):
        # Auto-update status als vol
        if self.is_full and self.status != 'full':
            self.status = 'full'
        super().save(*args, **kwargs)


class Booking(models.Model):
    """Boeking/Reservering voor een webinar"""
    
    STATUS_CHOICES = [
        ('pending', 'In afwachting'),
        ('confirmed', 'Bevestigd'),
        ('cancelled', 'Geannuleerd'),
        ('completed', 'Voltooid'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Onbetaald'),
        ('paid', 'Betaald'),
        ('refunded', 'Terugbetaald'),
    ]

    # Webinar en deelnemer
    workshop = models.ForeignKey(
        Workshop, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name='Webinar'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name='Gebruiker',
        null=True,
        blank=True
    )
    
    # Aantal deelnemers
    number_of_participants = models.PositiveIntegerField(
        'Aantal deelnemers',
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Contact informatie (voor niet-ingelogde gebruikers)
    first_name = models.CharField('Voornaam', max_length=100)
    last_name = models.CharField('Achternaam', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Telefoonnummer', max_length=20)
    
    # Deelnemers details (optioneel)
    participants_details = models.JSONField(
        'Deelnemers details',
        blank=True,
        null=True,
        help_text='Extra informatie over deelnemers'
    )
    
    # Betaling
    total_price = models.DecimalField(
        'Totaalprijs (€)', 
        max_digits=10, 
        decimal_places=2
    )
    payment_status = models.CharField(
        'Betalingsstatus',
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid'
    )
    
    # Status
    status = models.CharField(
        'Boekingsstatus',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Extra informatie
    notes = models.TextField('Opmerkingen', blank=True)
    dietary_requirements = models.TextField('Dieetwensen', blank=True)
    
    # Metadata
    booking_reference = models.CharField(
        'Boekingsreferentie',
        max_length=20,
        unique=True,
        editable=False
    )
    created_at = models.DateTimeField('Geboekt op', auto_now_add=True)
    updated_at = models.DateTimeField('Geüpdatet op', auto_now=True)
    confirmed_at = models.DateTimeField('Bevestigd op', null=True, blank=True)
    cancelled_at = models.DateTimeField('Geannuleerd op', null=True, blank=True)

    class Meta:
        verbose_name = 'Boeking'
        verbose_name_plural = 'Boekingen'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_reference']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Boeking {self.booking_reference} - {self.workshop.title}"

    def save(self, *args, **kwargs):
        # Generate booking reference als nieuw (WB voor Webinar Booking)
        if not self.booking_reference:
            import uuid
            self.booking_reference = f"WB{uuid.uuid4().hex[:8].upper()}"
        
        # Auto-calculate total price
        if not self.total_price:
            self.total_price = self.workshop.price * self.number_of_participants
        
        # Set confirmed_at timestamp
        if self.status == 'confirmed' and not self.confirmed_at:
            self.confirmed_at = timezone.now()
        
        # Set cancelled_at timestamp
        if self.status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        
        super().save(*args, **kwargs)


class Review(models.Model):
    """Review voor een webinar"""
    
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Webinar'
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Boeking',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Gebruiker'
    )
    
    # Review content
    rating = models.PositiveIntegerField(
        'Beoordeling',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField('Titel', max_length=200)
    comment = models.TextField('Commentaar')
    
    # Metadata
    created_at = models.DateTimeField('Aangemaakt op', auto_now_add=True)
    updated_at = models.DateTimeField('Geüpdatet op', auto_now=True)
    is_approved = models.BooleanField('Goedgekeurd', default=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['workshop', 'user']

    def __str__(self):
        return f"{self.rating}★ - {self.workshop.title} door {self.user.get_full_name()}"


class NewsletterSubscriber(models.Model):
    """Nieuwsbrief inschrijvingen"""
    
    email = models.EmailField('Email adres', unique=True)
    first_name = models.CharField('Voornaam', max_length=100, blank=True)
    last_name = models.CharField('Achternaam', max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField('Actief', default=True)
    confirmed = models.BooleanField('Bevestigd', default=False)
    
    # Metadata
    subscribed_at = models.DateTimeField('Ingeschreven op', auto_now_add=True)
    unsubscribed_at = models.DateTimeField('Uitgeschreven op', null=True, blank=True)
    
    # Preferences (optioneel voor later)
    interests = models.JSONField(
        'Interesses',
        blank=True,
        null=True,
        help_text='Categorieën waar de subscriber in geïnteresseerd is'
    )

    class Meta:
        verbose_name = 'Nieuwsbrief Inschrijving'
        verbose_name_plural = 'Nieuwsbrief Inschrijvingen'
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        name = f"{self.first_name} {self.last_name}" if self.first_name else self.email
        return f"{name} - {'Actief' if self.is_active else 'Inactief'}"


class InhouseTrainingPage(models.Model):
    """Singleton model voor Inhouse Training pagina content"""

    # HTML content veld voor de hele pagina
    content = models.TextField(
        'Pagina Inhoud',
        default='',
        blank=True,
        help_text='HTML content voor de inhouse trainingen pagina. Je kunt hier volledige HTML gebruiken voor opmaak.'
    )

    # Banner sectie (homepage) - behouden voor homepage weergave
    banner_title = models.CharField(
        'Banner Titel (Homepage)',
        max_length=200,
        default='Op zoek naar opleidingen op maat voor jouw team?',
        help_text='Titel die getoond wordt op de homepage'
    )
    banner_description = models.TextField(
        'Banner Beschrijving (Homepage)',
        default='Ontdek onze inhouse trainingen: volledig aangepast aan de behoeften van jouw organisatie.',
        help_text='Korte beschrijving op de homepage'
    )
    banner_button_text = models.CharField(
        'Banner Knop Tekst (Homepage)',
        max_length=50,
        default='Ontdek Inhouse Opleidingen'
    )

    # Metadata
    is_active = models.BooleanField('Actief', default=True)
    updated_at = models.DateTimeField('Laatst gewijzigd', auto_now=True)

    class Meta:
        verbose_name = 'Inhouse Training Pagina'
        verbose_name_plural = 'Inhouse Training Pagina'

    def __str__(self):
        return 'Inhouse Training Pagina Content'

    def save(self, *args, **kwargs):
        # Singleton pattern - er mag maar 1 instance zijn
        self.pk = 1

        # Vul default content in als leeg
        if not self.content:
            self.content = '''
<div class="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-20 mb-12">
    <div class="container mx-auto px-4">
        <div class="max-w-4xl mx-auto text-center">
            <h1 class="text-4xl md:text-5xl font-bold mb-6">Inhouse Trainingen op Maat</h1>
            <p class="text-xl text-blue-100">
                Maatwerk opleidingen speciaal afgestemd op jouw organisatie
            </p>
        </div>
    </div>
</div>

<div class="container mx-auto px-4 py-8 mb-12">
    <div class="max-w-4xl mx-auto">

        <!-- Introductie -->
        <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
            <div class="prose prose-lg max-w-none">
                <p>Bij Narhval Learning begrijpen we dat elke organisatie uniek is. Daarom bieden wij volledig op maat gemaakte AI-opleidingen aan die perfect aansluiten bij jouw bedrijfsdoelen en uitdagingen.</p>
            </div>
        </div>

        <!-- Benefits Section -->
        <div class="mb-12">
            <h2 class="text-3xl font-bold mb-8 text-center">Waarom kiezen voor inhouse training?</h2>
            <div class="grid md:grid-cols-2 gap-6">
                <div class="bg-blue-50 rounded-lg p-6 border-l-4 border-blue-600">
                    <div class="flex items-start">
                        <i class="bi bi-building text-4xl text-blue-600 mr-4 flex-shrink-0"></i>
                        <div>
                            <h3 class="font-bold text-lg mb-2">Op locatie of online</h3>
                            <p class="text-gray-700">Wij komen naar jullie toe, of verzorgen de training volledig online via Teams.</p>
                        </div>
                    </div>
                </div>
                <div class="bg-blue-50 rounded-lg p-6 border-l-4 border-blue-600">
                    <div class="flex items-start">
                        <i class="bi bi-people-fill text-4xl text-blue-600 mr-4 flex-shrink-0"></i>
                        <div>
                            <h3 class="font-bold text-lg mb-2">Voor het hele team</h3>
                            <p class="text-gray-700">Train meerdere medewerkers tegelijk tegen een vast tarief.</p>
                        </div>
                    </div>
                </div>
                <div class="bg-blue-50 rounded-lg p-6 border-l-4 border-blue-600">
                    <div class="flex items-start">
                        <i class="bi bi-sliders text-4xl text-blue-600 mr-4 flex-shrink-0"></i>
                        <div>
                            <h3 class="font-bold text-lg mb-2">Volledig op maat</h3>
                            <p class="text-gray-700">Content en voorbeelden specifiek afgestemd op jullie sector en uitdagingen.</p>
                        </div>
                    </div>
                </div>
                <div class="bg-blue-50 rounded-lg p-6 border-l-4 border-blue-600">
                    <div class="flex items-start">
                        <i class="bi bi-calendar-check text-4xl text-blue-600 mr-4 flex-shrink-0"></i>
                        <div>
                            <h3 class="font-bold text-lg mb-2">Flexibele planning</h3>
                            <p class="text-gray-700">Kies zelf de data en tijdstippen die het beste passen bij jullie team.</p>
                        </div>
                    </div>
                </div>
                <div class="bg-blue-50 rounded-lg p-6 border-l-4 border-blue-600">
                    <div class="flex items-start">
                        <i class="bi bi-award text-4xl text-blue-600 mr-4 flex-shrink-0"></i>
                        <div>
                            <h3 class="font-bold text-lg mb-2">Certificaat</h3>
                            <p class="text-gray-700">Deelnemers ontvangen een certificaat na afloop van de training.</p>
                        </div>
                    </div>
                </div>
                <div class="bg-blue-50 rounded-lg p-6 border-l-4 border-blue-600">
                    <div class="flex items-start">
                        <i class="bi bi-headset text-4xl text-blue-600 mr-4 flex-shrink-0"></i>
                        <div>
                            <h3 class="font-bold text-lg mb-2">Nazorg & support</h3>
                            <p class="text-gray-700">Ook na de training staan we klaar voor vragen en ondersteuning.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Process Steps -->
        <div class="bg-gray-50 rounded-lg p-8 mb-12">
            <h2 class="text-3xl font-bold mb-4 text-center">Hoe werken we samen?</h2>
            <p class="text-center text-gray-600 mb-8">We volgen een gestructureerde aanpak om ervoor te zorgen dat de training perfect aansluit bij jullie behoeften:</p>
            <div class="space-y-6">
                <div class="flex items-start">
                    <div class="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">
                        01
                    </div>
                    <div class="flex-1">
                        <h3 class="font-bold text-lg mb-2">Intake gesprek</h3>
                        <p class="text-gray-700">We bespreken jullie doelen, uitdagingen en gewenste outcomes.</p>
                    </div>
                </div>
                <div class="flex items-start">
                    <div class="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">
                        02
                    </div>
                    <div class="flex-1">
                        <h3 class="font-bold text-lg mb-2">Programma op maat</h3>
                        <p class="text-gray-700">We stellen een trainingsplan samen dat perfect aansluit bij jullie behoeften.</p>
                    </div>
                </div>
                <div class="flex items-start">
                    <div class="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">
                        03
                    </div>
                    <div class="flex-1">
                        <h3 class="font-bold text-lg mb-2">Training verzorgen</h3>
                        <p class="text-gray-700">Onze ervaren trainers verzorgen de sessies met praktische voorbeelden uit jullie sector.</p>
                    </div>
                </div>
                <div class="flex items-start">
                    <div class="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold mr-4 flex-shrink-0 text-lg">
                        04
                    </div>
                    <div class="flex-1">
                        <h3 class="font-bold text-lg mb-2">Follow-up & evaluatie</h3>
                        <p class="text-gray-700">We evalueren de resultaten en bieden nazorg waar nodig.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- CTA Section -->
        <div class="bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-lg p-8 text-center">
            <h2 class="text-3xl font-bold mb-4">Klaar om te starten?</h2>
            <p class="text-xl text-blue-100 mb-8">
                Neem contact met ons op voor een vrijblijvend gesprek over de mogelijkheden voor jouw organisatie.
            </p>
            <a href="/contact/" class="inline-block bg-white text-blue-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-blue-50 transition-colors shadow-lg">
                <svg class="w-6 h-6 inline-block mr-2 -mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
                Neem Contact Op
            </a>
        </div>
    </div>
</div>
'''

        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Haal de singleton instance op, of maak deze aan"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
