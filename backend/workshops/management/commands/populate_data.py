from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import random

from workshops.models import Category, Workshop, Booking, Review


class Command(BaseCommand):
    help = 'Vult de database met GenAI webinars voor Narhval Learning'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Start met GenAI webinars genereren...'))
        
        # Verwijder oude data
        self.stdout.write('🗑️  Verwijderen oude data...')
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Workshop.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # Maak categorieën
        self.stdout.write('📁 Categorieën aanmaken...')
        categories = self.create_categories()
        
        # Maak users
        self.stdout.write('👥 Users aanmaken...')
        users = self.create_users()
        
        # Maak webinars
        self.stdout.write('🎓 Webinars aanmaken...')
        webinars = self.create_webinars(categories)
        
        # Maak boekingen
        self.stdout.write('📅 Boekingen aanmaken...')
        bookings = self.create_bookings(webinars, users)
        
        # Maak reviews
        self.stdout.write('⭐ Reviews aanmaken...')
        self.create_reviews(webinars, users, bookings)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Klaar! GenAI webinars succesvol aangemaakt!'))
        self.stdout.write(self.style.SUCCESS(f'   📊 {len(categories)} categorieën'))
        self.stdout.write(self.style.SUCCESS(f'   🎓 {len(webinars)} webinars'))
        self.stdout.write(self.style.SUCCESS(f'   👥 {len(users)} users'))
        self.stdout.write(self.style.SUCCESS(f'   📅 {len(bookings)} boekingen'))
        self.stdout.write(self.style.SUCCESS(f'   ⭐ {Review.objects.count()} reviews'))
        self.stdout.write(self.style.SUCCESS('\n🎨 Ga naar http://localhost:8000/admin/ om alles te bekijken!'))

    def create_categories(self):
        categories_data = [
            {
                'name': 'AI Geletterdheid',
                'slug': 'ai-geletterdheid',
                'description': 'Bouw een stevige basis in AI en leer de fundamenten van generatieve AI voor professioneel gebruik',
                'icon': 'bi-book'
            },
            {
                'name': 'Prompt Engineering',
                'slug': 'prompt-engineering',
                'description': 'Beheers de kunst van effectieve prompts schrijven en word een expert in communiceren met AI',
                'icon': 'bi-chat-dots'
            },
            {
                'name': 'Agentic AI',
                'slug': 'agentic-ai',
                'description': 'Leer autonome AI-agents bouwen en inzetten voor complexe bedrijfsprocessen',
                'icon': 'bi-robot'
            },
            {
                'name': 'Workflow Automation',
                'slug': 'workflow-automation',
                'description': 'Automatiseer je workflows met moderne no-code en low-code tools',
                'icon': 'bi-gear-wide-connected'
            },
            {
                'name': 'Data Architecture & Analyse',
                'slug': 'data-architecture',
                'description': 'Structureer je data en maak datagedreven beslissingen met moderne tools',
                'icon': 'bi-database'
            },
            {
                'name': 'Tools',
                'slug': 'tools',
                'description': 'Beheers essentiële AI-tools en software voor productiviteit en creativiteit',
                'icon': 'bi-tools'
            },
            {
                'name': 'AI Governance',
                'slug': 'ai-governance',
                'description': 'Implementeer verantwoorde AI binnen je organisatie met de juiste governance structuur',
                'icon': 'bi-shield-check'
            },
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(**cat_data)
            categories.append(category)
            if created:
                self.stdout.write(f'   ✅ {category.name}')
        
        return categories

    def create_users(self):
        users_data = [
            {'username': 'pieter', 'first_name': 'Pieter', 'last_name': 'Janssens', 'email': 'pieter@bedrijf.be'},
            {'username': 'sarah', 'first_name': 'Sarah', 'last_name': 'De Vries', 'email': 'sarah@bedrijf.be'},
            {'username': 'thomas', 'first_name': 'Thomas', 'last_name': 'Vermeulen', 'email': 'thomas@bedrijf.be'},
            {'username': 'laura', 'first_name': 'Laura', 'last_name': 'Peeters', 'email': 'laura@bedrijf.be'},
            {'username': 'kevin', 'first_name': 'Kevin', 'last_name': 'Martens', 'email': 'kevin@bedrijf.be'},
            {'username': 'nina', 'first_name': 'Nina', 'last_name': 'Van Damme', 'email': 'nina@bedrijf.be'},
        ]
        
        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email']
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f'   ✅ {user.get_full_name()}')
            users.append(user)
        
        return users
    
    def generate_teams_url(self):
        """Genereer een realistische Teams meeting URL"""
        meeting_code = f"{''.join([str(random.randint(0, 9)) for _ in range(19)])}"
        return f"https://teams.microsoft.com/l/meetup-join/19%3ameeting_{meeting_code}%40thread.v2/0"
    
    def generate_meeting_id(self):
        """Genereer een meeting ID"""
        return f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"

    def create_webinars(self, categories):
        now = timezone.now()
        
        # Helper functie om categorie te vinden
        def get_cat(slug):
            return next((c for c in categories if c.slug == slug), None)
        
        webinars_data = [
            # AI GELETTERDHEID
            {
                'title': 'Efficiënt op het Werk met AI - Basic',
                'slug': 'efficient-werken-ai-basic',
                'description': 'Ontdek hoe AI je dagelijkse werkzaamheden kan transformeren in deze online webinar. Leer de fundamenten van generatieve AI en hoe je deze praktisch kunt toepassen in je werk. We bespreken ChatGPT, Copilot en andere AI-tools die je direct kunt gebruiken.',
                'short_description': 'Leer de basis van AI en hoe je het toepast in je dagelijkse werk (Online webinar)',
                'category': get_cat('ai-geletterdheid'),
                'start_datetime': now + timedelta(days=7),
                'duration_hours': 2.0,
                'max_participants': 30,
                'min_participants': 5,
                'price': Decimal('179.00'),
                'instructor_name': 'Christophe Narhval',
                'instructor_bio': 'AI consultant met 5+ jaar ervaring in het implementeren van AI-oplossingen in bedrijven',
                'status': 'upcoming',
                'featured': True,
                'materials_included': True,
                'requirements': 'Basiskennis van Microsoft Office, stabiele internetverbinding',
            },
            
            # PROMPT ENGINEERING
            {
                'title': 'Efficiënt op het Werk met AI - Prompt Engineering',
                'slug': 'efficient-werken-ai-prompt-engineering',
                'description': 'Leer de kunst van effectieve prompts schrijven in deze interactieve online webinar. Deze sessie leert je hoe je AI-tools zoals ChatGPT optimaal kunt aansturen om de beste resultaten te krijgen. Van basis technieken tot geavanceerde strategieën.',
                'short_description': 'Beheers de kunst van effectieve prompts schrijven (Online webinar)',
                'category': get_cat('prompt-engineering'),
                'start_datetime': now + timedelta(days=10),
                'duration_hours': 2.0,
                'max_participants': 25,
                'min_participants': 4,
                'price': Decimal('179.00'),
                'instructor_name': 'Christophe Narhval',
                'instructor_bio': 'AI consultant met 5+ jaar ervaring in het implementeren van AI-oplossingen in bedrijven',
                'status': 'upcoming',
                'featured': True,
                'materials_included': True,
            },
            {
                'title': 'Efficiënt op het Werk met AI - Prompt Engineering Expert',
                'slug': 'efficient-werken-ai-prompt-engineering-expert',
                'description': 'Verdiep je kennis van prompt engineering tot expert niveau in deze geavanceerde online webinar. Leer geavanceerde technieken zoals chain-of-thought, few-shot learning, en hoe je complexe AI-workflows kunt opzetten met geavanceerde prompting strategieën.',
                'short_description': 'Word een expert in geavanceerde prompt engineering technieken (Online)',
                'category': get_cat('prompt-engineering'),
                'start_datetime': now + timedelta(days=17),
                'duration_hours': 2.0,
                'max_participants': 20,
                'min_participants': 4,
                'price': Decimal('179.00'),
                'instructor_name': 'Christophe Narhval',
                'instructor_bio': 'AI consultant met 5+ jaar ervaring in het implementeren van AI-oplossingen in bedrijven',
                'status': 'upcoming',
                'materials_included': True,
                'requirements': 'Voltooide Prompt Engineering basis webinar of gelijkwaardige kennis',
            },
            {
                'title': 'Efficiënt op het Werk met AI - GPT Building',
                'slug': 'efficient-werken-ai-gpt-building',
                'description': 'Bouw je eigen custom GPTs voor specifieke bedrijfsprocessen in deze hands-on online webinar. Leer hoe je een GPT configureert, traint en optimaliseert voor jouw specifieke use case zonder programmeerkennis.',
                'short_description': 'Bouw custom GPTs voor jouw bedrijfsprocessen (Online)',
                'category': get_cat('agentic-ai'),
                'start_datetime': now + timedelta(days=14),
                'duration_hours': 2.0,
                'max_participants': 20,
                'min_participants': 4,
                'price': Decimal('179.00'),
                'instructor_name': 'Christophe Narhval',
                'instructor_bio': 'AI consultant met 5+ jaar ervaring in het implementeren van AI-oplossingen in bedrijven',
                'status': 'upcoming',
                'featured': True,
                'materials_included': True,
                'requirements': 'ChatGPT Plus account vereist',
            },
            
            # TOOLS - OFFICE & PRODUCTIVITY
            {
                'title': 'Efficiënt op het Werk met AI - ChatGPT & Excel',
                'slug': 'efficient-werken-ai-chatgpt-excel',
                'description': 'Combineer de kracht van ChatGPT met Excel voor dataverwerking en analyse in deze praktische online webinar. Leer hoe je formules genereert, data analyseert, en rapporten maakt met AI-ondersteuning.',
                'short_description': 'Gebruik AI om Excel werk te automatiseren en optimaliseren (Online)',
                'category': get_cat('tools'),
                'start_datetime': now + timedelta(days=21),
                'duration_hours': 2.0,
                'max_participants': 25,
                'min_participants': 5,
                'price': Decimal('179.00'),
                'instructor_name': 'Sarah De Vries',
                'instructor_bio': 'Data analist met specialisatie in Excel automation en AI integratie',
                'status': 'upcoming',
                'materials_included': True,
                'requirements': 'Basiskennis Excel',
            },
            {
                'title': 'Efficiënt op het Werk met AI - Rapporteren met ChatGPT',
                'slug': 'efficient-werken-ai-rapporteren-chatgpt',
                'description': 'Leer hoe je professionele rapporten, presentaties en documenten maakt met AI-ondersteuning tijdens deze online webinar. Van structuur tot content generatie en opmaak tips.',
                'short_description': 'Maak professionele rapporten sneller met AI (Online)',
                'category': get_cat('tools'),
                'start_datetime': now + timedelta(days=24),
                'duration_hours': 2.0,
                'max_participants': 30,
                'min_participants': 5,
                'price': Decimal('179.00'),
                'instructor_name': 'Thomas Vermeulen',
                'instructor_bio': 'Business consultant met focus op professionele communicatie en AI tools',
                'status': 'upcoming',
                'materials_included': True,
            },
            
            # M365 COPILOT SERIES
            {
                'title': 'Efficiënt op het Werk met AI - M365 Copilot',
                'slug': 'efficient-werken-ai-m365-copilot',
                'description': 'Ontdek Microsoft 365 Copilot en hoe deze AI-assistent je productiviteit transformeert in deze online webinar. Leer Copilot gebruiken in Teams, Outlook, Word en meer voor dagelijkse werkzaamheden.',
                'short_description': 'Beheers M365 Copilot voor maximale productiviteit (Online)',
                'category': get_cat('tools'),
                'start_datetime': now + timedelta(days=28),
                'duration_hours': 2.0,
                'max_participants': 30,
                'min_participants': 5,
                'price': Decimal('179.00'),
                'instructor_name': 'Laura Peeters',
                'instructor_bio': 'Microsoft 365 specialist met certificering in Copilot implementatie',
                'status': 'upcoming',
                'featured': True,
                'materials_included': True,
                'requirements': 'M365 Copilot licentie vereist',
            },
            {
                'title': 'Efficiënt op het Werk met AI - M365 Copilot Excel',
                'slug': 'efficient-werken-ai-m365-copilot-excel',
                'description': 'Deep dive in Copilot voor Excel tijdens deze online webinar. Leer hoe je complexe data analyses uitvoert, formules genereert en insights krijgt met natuurlijke taal commands.',
                'short_description': 'Excel data analyse met Copilot AI (Online)',
                'category': get_cat('tools'),
                'start_datetime': now + timedelta(days=31),
                'duration_hours': 2.0,
                'max_participants': 20,
                'min_participants': 5,
                'price': Decimal('179.00'),
                'instructor_name': 'Laura Peeters',
                'instructor_bio': 'Microsoft 365 specialist met certificering in Copilot implementatie',
                'status': 'upcoming',
                'materials_included': True,
                'requirements': 'M365 Copilot licentie + basiskennis Excel',
            },
            {
                'title': 'Efficiënt op het Werk met AI - M365 Copilot PowerPoint',
                'slug': 'efficient-werken-ai-m365-copilot-ppt',
                'description': 'Maak professionele presentaties in recordtijd met Copilot in PowerPoint tijdens deze online webinar. Van concept tot design, leer hoe AI je helpt overtuigende presentaties te maken.',
                'short_description': 'Creëer presentaties sneller met Copilot (Online)',
                'category': get_cat('tools'),
                'start_datetime': now + timedelta(days=35),
                'duration_hours': 2.0,
                'max_participants': 25,
                'min_participants': 5,
                'price': Decimal('179.00'),
                'instructor_name': 'Laura Peeters',
                'instructor_bio': 'Microsoft 365 specialist met certificering in Copilot implementatie',
                'status': 'upcoming',
                'materials_included': True,
                'requirements': 'M365 Copilot licentie',
            },
            {
                'title': 'Efficiënt op het Werk met AI - M365 Copilot Word',
                'slug': 'efficient-werken-ai-m365-copilot-word',
                'description': 'Beheers Copilot in Word voor document creatie en editing tijdens deze online sessie. Leer hoe je rapporten schrijft, teksten verbetert en documenten transformeert met AI.',
                'short_description': 'Schrijf betere documenten met Copilot in Word (Online)',
                'category': get_cat('tools'),
                'start_datetime': now + timedelta(days=38),
                'duration_hours': 2.0,
                'max_participants': 25,
                'min_participants': 5,
                'price': Decimal('179.00'),
                'instructor_name': 'Laura Peeters',
                'instructor_bio': 'Microsoft 365 specialist met certificering in Copilot implementatie',
                'status': 'upcoming',
                'materials_included': True,
                'requirements': 'M365 Copilot licentie',
            },
        ]
        
        webinars = []
        for ws_data in webinars_data:
            # Calculate end datetime
            start = ws_data['start_datetime']
            duration = ws_data['duration_hours']
            end = start + timedelta(hours=float(duration))
            
            # Set standard fields for online webinar
            ws_data['end_datetime'] = end
            ws_data['meeting_url'] = self.generate_teams_url()
            ws_data['meeting_id'] = self.generate_meeting_id()
            ws_data['meeting_password'] = f"WB{random.randint(1000, 9999)}"
            ws_data['is_active'] = True
            
            # Create webinar
            webinar, created = Workshop.objects.get_or_create(
                slug=ws_data['slug'],
                defaults=ws_data
            )
            webinars.append(webinar)
            if created:
                self.stdout.write(f'   ✅ {webinar.title}')
        
        return webinars

    def create_bookings(self, webinars, users):
        """Maak realistische boekingen voor de webinars"""
        bookings = []
        
        # Voor de eerste 4 webinars (die in het verleden liggen), maak completed bookings
        past_webinars = webinars[:4]
        for webinar in past_webinars:
            # Maak deze webinars "completed"
            webinar.status = 'completed'
            webinar.save()
            
            # 8-15 deelnemers per webinar (meer omdat het online is)
            num_bookings = random.randint(8, 15)
            for i in range(num_bookings):
                user = random.choice(users)
                booking = Booking.objects.create(
                    workshop=webinar,
                    user=user,
                    number_of_participants=1,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    phone=f'+32 47{random.randint(1000000, 9999999)}',
                    total_price=webinar.price,
                    payment_status='paid',
                    status='completed'
                )
                bookings.append(booking)
        
        # Voor de upcoming webinars, maak enkele confirmed bookings
        upcoming_webinars = webinars[4:]
        for webinar in upcoming_webinars:
            num_bookings = random.randint(3, 8)
            for i in range(num_bookings):
                user = random.choice(users)
                booking = Booking.objects.create(
                    workshop=webinar,
                    user=user,
                    number_of_participants=1,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    phone=f'+32 47{random.randint(1000000, 9999999)}',
                    total_price=webinar.price,
                    payment_status=random.choice(['paid', 'paid', 'unpaid']),
                    status=random.choice(['confirmed', 'confirmed', 'pending'])
                )
                bookings.append(booking)
        
        self.stdout.write(f'   ✅ {len(bookings)} boekingen aangemaakt')
        return bookings

    def create_reviews(self, webinars, users, bookings):
        """Maak reviews voor afgelopen webinars"""
        completed_bookings = [b for b in bookings if b.status == 'completed']
        
        reviews_data = [
            {'rating': 5, 'title': 'Zeer waardevolle online webinar!', 'comment': 'Christophe legt alles heel duidelijk uit en ik kan het direct toepassen in mijn werk. De online formule werkt perfect!'},
            {'rating': 5, 'title': 'Precies wat ik nodig had', 'comment': 'Praktische voorbeelden en hands-on oefeningen. Kon vanuit mijn kantoor meedoen, super handig!'},
            {'rating': 4, 'title': 'Goede online introductie', 'comment': 'Duidelijke uitleg via Teams, alleen had ik graag wat meer tijd gehad voor de oefeningen.'},
            {'rating': 5, 'title': 'Top instructeur online!', 'comment': 'Laura kent haar vakgebied door en door. Veel geleerd over M365 Copilot via de webinar.'},
            {'rating': 5, 'title': 'Zeer aan te raden online sessie', 'comment': 'Concrete tips die ik meteen kon gebruiken. Vanuit huis kunnen volgen is een groot pluspunt!'},
            {'rating': 4, 'title': 'Interessante online workshop', 'comment': 'Goede inhoud, alleen het tempo was soms wat hoog. Maar de opname kon ik later terug bekijken.'},
            {'rating': 5, 'title': 'Fantastische online opleiding', 'comment': 'Ik heb nu veel meer vertrouwen in het gebruik van AI tools. De interactie via Teams was uitstekend.'},
            {'rating': 5, 'title': 'Absolute aanrader!', 'comment': 'De combinatie van theorie en praktijk was perfect. Online format spaart veel reistijd!'},
            {'rating': 4, 'title': 'Prima webinar', 'comment': 'Nuttige informatie, zou graag een vervolg webinar willen volgen.'},
            {'rating': 5, 'title': 'Erg leerzaam online', 'comment': 'Thomas geeft heel praktische voorbeelden en beantwoordt alle vragen uitgebreid via de chat.'},
        ]
        
        # Track welke combinaties we al hebben gebruikt (webinar + user)
        created_reviews = set()
        
        # Maak 8-10 reviews voor random completed bookings
        num_reviews = min(len(completed_bookings), 10)
        attempts = 0
        max_attempts = num_reviews * 3  # Probeer maximaal 3x zoveel keer
        
        while len(created_reviews) < num_reviews and attempts < max_attempts:
            attempts += 1
            booking = random.choice(completed_bookings)
            
            # Check of we al een review hebben voor deze webinar + user combinatie
            review_key = (booking.workshop.id, booking.user.id)
            if review_key in created_reviews:
                continue
            
            # Check of er al een review bestaat in de database
            if Review.objects.filter(workshop=booking.workshop, user=booking.user).exists():
                continue
            
            review_data = random.choice(reviews_data)
            Review.objects.create(
                workshop=booking.workshop,
                booking=booking,
                user=booking.user,
                rating=review_data['rating'],
                title=review_data['title'],
                comment=review_data['comment'],
                is_approved=True
            )
            created_reviews.add(review_key)
        
        self.stdout.write(f'   ✅ {Review.objects.count()} reviews aangemaakt')
