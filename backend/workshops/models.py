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
    
    # Banner sectie (homepage)
    banner_title = models.CharField(
        'Banner Titel',
        max_length=200,
        default='Op zoek naar opleidingen op maat voor jouw team?',
        help_text='Titel die getoond wordt op de homepage'
    )
    banner_description = models.TextField(
        'Banner Beschrijving',
        default='Ontdek onze inhouse trainingen: volledig aangepast aan de behoeften van jouw organisatie. Van AI-geletterdheid tot geavanceerde workflow automation - wij brengen de kennis naar jullie kantoor of online omgeving.',
        help_text='Korte beschrijving op de homepage'
    )
    banner_button_text = models.CharField(
        'Banner Knop Tekst',
        max_length=50,
        default='Ontdek Inhouse Opleidingen'
    )
    
    # Detail pagina content
    page_title = models.CharField(
        'Pagina Titel',
        max_length=200,
        default='Inhouse Trainingen op Maat'
    )
    
    intro_text = models.TextField(
        'Introductie Tekst',
        default='Bij Narhval Learning begrijpen we dat elke organisatie uniek is. Daarom bieden wij volledig op maat gemaakte AI-opleidingen aan die perfect aansluiten bij jouw bedrijfsdoelen en uitdagingen.'
    )
    
    benefits_title = models.CharField(
        'Voordelen Titel',
        max_length=200,
        default='Waarom kiezen voor inhouse training?'
    )
    
    benefits = models.JSONField(
        'Voordelen Lijst',
        default=list,
        blank=True,
        help_text='Lijst van voordelen (wordt automatisch aangemaakt bij eerste save)'
    )
    
    process_title = models.CharField(
        'Proces Titel',
        max_length=200,
        default='Hoe werken we samen?'
    )
    
    process_description = models.TextField(
        'Proces Beschrijving',
        default='We volgen een gestructureerde aanpak om ervoor te zorgen dat de training perfect aansluit bij jullie behoeften:'
    )
    
    process_steps = models.JSONField(
        'Proces Stappen',
        default=list,
        blank=True,
        help_text='Lijst van processtappen (wordt automatisch aangemaakt bij eerste save)'
    )
    
    topics_title = models.CharField(
        'Onderwerpen Titel',
        max_length=200,
        default='Mogelijke trainingsonderwerpen'
    )
    
    topics_description = models.TextField(
        'Onderwerpen Beschrijving',
        default='Wij kunnen trainingen verzorgen over diverse AI-gerelateerde onderwerpen, waaronder:'
    )
    
    cta_title = models.CharField(
        'CTA Titel',
        max_length=200,
        default='Klaar om te starten?'
    )
    
    cta_description = models.TextField(
        'CTA Beschrijving',
        default='Neem contact met ons op voor een vrijblijvend gesprek over de mogelijkheden voor jouw organisatie.'
    )
    
    cta_button_text = models.CharField(
        'CTA Knop Tekst',
        max_length=50,
        default='Neem Contact Op'
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
        
        # Vul default voordelen in als leeg
        if not self.benefits:
            self.benefits = [
                {
                    'icon': 'bi-building',
                    'title': 'Op locatie of online',
                    'description': 'Wij komen naar jullie toe, of verzorgen de training volledig online via Teams.'
                },
                {
                    'icon': 'bi-people-fill',
                    'title': 'Voor het hele team',
                    'description': 'Train meerdere medewerkers tegelijk tegen een vast tarief.'
                },
                {
                    'icon': 'bi-sliders',
                    'title': 'Volledig op maat',
                    'description': 'Content en voorbeelden specifiek afgestemd op jullie sector en uitdagingen.'
                },
                {
                    'icon': 'bi-calendar-check',
                    'title': 'Flexibele planning',
                    'description': 'Kies zelf de data en tijdstippen die het beste passen bij jullie team.'
                },
                {
                    'icon': 'bi-award',
                    'title': 'Certificaat',
                    'description': 'Deelnemers ontvangen een certificaat na afloop van de training.'
                },
                {
                    'icon': 'bi-headset',
                    'title': 'Nazorg & support',
                    'description': 'Ook na de training staan we klaar voor vragen en ondersteuning.'
                }
            ]
        
        # Vul default processtappen in als leeg
        if not self.process_steps:
            self.process_steps = [
                {
                    'number': '01',
                    'title': 'Intake gesprek',
                    'description': 'We bespreken jullie doelen, uitdagingen en gewenste outcomes.'
                },
                {
                    'number': '02',
                    'title': 'Programma op maat',
                    'description': 'We stellen een trainingsplan samen dat perfect aansluit bij jullie behoeften.'
                },
                {
                    'number': '03',
                    'title': 'Training verzorgen',
                    'description': 'Onze ervaren trainers verzorgen de sessies met praktische voorbeelden uit jullie sector.'
                },
                {
                    'number': '04',
                    'title': 'Follow-up & evaluatie',
                    'description': 'We evalueren de resultaten en bieden nazorg waar nodig.'
                }
            ]
        
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Haal de singleton instance op, of maak deze aan"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
