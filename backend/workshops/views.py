from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from .models import Workshop, Category, Review, Booking, NewsletterSubscriber, InhouseTrainingPage
from .forms import BookingForm, NewsletterSubscribeForm


class WorkshopListView(ListView):
    """
    Lijst view voor alle workshops met filtering en zoeken
    """
    model = Workshop
    template_name = 'workshops/workshop_list.html'
    context_object_name = 'workshops'
    paginate_by = 12

    def get_queryset(self):
        queryset = Workshop.objects.select_related('category').filter(
            is_active=True
        ).exclude(
            status__in=['cancelled', 'completed']  # Verberg geannuleerde en afgelopen workshops
        ).order_by('start_datetime')

        # Search functionaliteit
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        # Filter op categorie
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filter op status
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Sorteer optie
        sort = self.request.GET.get('sort', 'date')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        else:  # date
            queryset = queryset.order_by('start_datetime')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Voeg categorieën toe met aantal workshops (alleen actieve, niet-afgelopen)
        categories = Category.objects.annotate(
            workshop_count=Count(
                'workshops',
                filter=Q(
                    workshops__is_active=True
                ) & ~Q(
                    workshops__status__in=['cancelled', 'completed']
                )
            )
        ).order_by('name')
        
        # Voeg custom property toe voor correcte count in template
        for category in categories:
            category.active_workshop_count = category.workshop_count
        
        context['categories'] = categories
        
        # Statistics voor hero section (alleen actieve, niet-afgelopen)
        context['total_workshops'] = Workshop.objects.filter(
            is_active=True
        ).exclude(
            status__in=['cancelled', 'completed']
        ).count()
        context['total_categories'] = Category.objects.count()
        context['total_instructors'] = Workshop.objects.filter(
            is_active=True
        ).exclude(
            status__in=['cancelled', 'completed']
        ).values('instructor_name').distinct().count()
        
        # Check of er filters actief zijn
        context['filter_active'] = any([
            self.request.GET.get('search'),
            self.request.GET.get('category'),
            self.request.GET.get('status'),
        ])
        
        # Voeg inhouse training page content toe
        context['inhouse_page'] = InhouseTrainingPage.get_instance()
        
        return context


class WorkshopDetailView(DetailView):
    """
    Detail view voor een specifieke workshop
    """
    model = Workshop
    template_name = 'workshops/workshop_detail.html'
    context_object_name = 'workshop'
    slug_field = 'slug'

    def get_queryset(self):
        return Workshop.objects.select_related('category').prefetch_related(
            'reviews__user',
            'bookings'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workshop = self.object

        # Haal goedgekeurde reviews op
        reviews = workshop.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')

        # Gemiddelde rating berekenen
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            context['average_rating'] = round(avg_rating, 1)
            context['rating_count'] = len(reviews)
        else:
            context['average_rating'] = 0
            context['rating_count'] = 0

        # Gerelateerde workshops (zelfde categorie, andere workshops, niet afgelopen/geannuleerd)
        if workshop.category:
            context['related_workshops'] = Workshop.objects.filter(
                category=workshop.category,
                is_active=True
            ).exclude(
                id=workshop.id
            ).exclude(
                status__in=['cancelled', 'completed']
            ).select_related('category')[:3]
        else:
            context['related_workshops'] = []

        return context


# Function-based views voor simpele pagina's
def homepage(request):
    """
    Homepage met featured workshops en categorieën
    """
    # Featured workshops (upcoming en active, gesorteerd op datum, niet afgelopen/geannuleerd)
    featured_workshops = Workshop.objects.filter(
        is_active=True
    ).exclude(
        status__in=['cancelled', 'completed']
    ).select_related('category').order_by('start_datetime')[:6]
    
    # Alle categorieën met workshop count (alleen actieve, niet-afgelopen)
    categories = Category.objects.annotate(
        workshop_count=Count(
            'workshops',
            filter=Q(
                workshops__is_active=True
            ) & ~Q(
                workshops__status__in=['cancelled', 'completed']
            )
        )
    ).order_by('name')
    
    # Statistics (alleen actieve, niet-afgelopen)
    stats = {
        'total_workshops': Workshop.objects.filter(
            is_active=True
        ).exclude(
            status__in=['cancelled', 'completed']
        ).count(),
        'total_categories': categories.count(),
        'total_reviews': Review.objects.filter(is_approved=True).count(),
    }
    
    context = {
        'featured_workshops': featured_workshops,
        'categories': categories,
        'stats': stats,
    }
    
    return render(request, 'workshops/homepage.html', context)


def workshop_booking(request, slug):
    """
    Booking view voor een workshop (optie A - zonder login vereist)
    """
    workshop = get_object_or_404(Workshop, slug=slug, is_active=True)
    
    # Check of workshop nog boekbaar is
    if workshop.status == 'full':
        messages.error(request, 'Deze workshop is helaas volgeboekt.')
        return redirect('workshop_detail', slug=slug)
    
    if workshop.status == 'cancelled':
        messages.error(request, 'Deze workshop is geannuleerd.')
        return redirect('workshop_detail', slug=slug)
    
    if workshop.status == 'completed':
        messages.error(request, 'Deze workshop is al afgelopen.')
        return redirect('workshop_detail', slug=slug)
    
    # Check of workshop in het verleden is
    if workshop.start_datetime < timezone.now():
        messages.error(request, 'Deze workshop is al gestart of afgelopen.')
        return redirect('workshop_detail', slug=slug)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, workshop=workshop)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Maak booking object maar sla nog niet op
                    booking = Booking()
                    booking.workshop = workshop
                    
                    # Als user ingelogd is, koppel aan user
                    if request.user.is_authenticated:
                        booking.user = request.user
                    
                    # Split naam in voor- en achternaam
                    full_name = form.cleaned_data['name'].strip()
                    name_parts = full_name.split(' ', 1)  # Split op eerste spatie
                    
                    if len(name_parts) == 2:
                        booking.first_name = name_parts[0]
                        booking.last_name = name_parts[1]
                    else:
                        # Als er geen achternaam is, gebruik voornaam voor beide
                        booking.first_name = name_parts[0]
                        booking.last_name = name_parts[0]
                    
                    # Vul contact velden in (gebruik de JUISTE model velden)
                    booking.email = form.cleaned_data['email']
                    booking.phone = form.cleaned_data['phone']
                    booking.number_of_participants = form.cleaned_data['num_participants']
                    booking.notes = form.cleaned_data.get('notes', '')
                    
                    # Bereken totaalprijs
                    booking.total_price = workshop.price * booking.number_of_participants
                    
                    # Standaard status is 'pending'
                    booking.status = 'pending'
                    booking.payment_status = 'unpaid'
                    
                    # Sla booking op (dit genereert automatisch booking_reference)
                    booking.save()
                    
                    # Success message
                    messages.success(
                        request, 
                        f'Je boeking is succesvol aangemaakt! Referentie: {booking.booking_reference}'
                    )
                    
                    # Redirect naar confirmation pagina
                    return redirect('booking_confirmation', reference=booking.booking_reference)
                    
            except Exception as e:
                messages.error(
                    request, 
                    f'Er ging iets mis bij het aanmaken van je boeking. Probeer het opnieuw. Fout: {str(e)}'
                )
                print(f"Booking error: {str(e)}")  # Debug print
                import traceback
                traceback.print_exc()  # Print volledige stacktrace
        else:
            # Toon form errors
            messages.error(request, 'Controleer de ingevoerde gegevens en probeer opnieuw.')
            print(f"Form errors: {form.errors}")  # Debug print
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    else:
        # GET request - toon leeg formulier
        form = BookingForm(workshop=workshop)
    
    # Bereken totaalprijs voor in template (voor 1 persoon als voorbeeld)
    example_price = workshop.price
    
    context = {
        'workshop': workshop,
        'form': form,
        'example_price': example_price,
    }
    
    return render(request, 'workshops/booking_form.html', context)


def booking_confirmation(request, reference):
    """
    Bevestigingspagina na succesvolle booking
    """
    booking = get_object_or_404(Booking, booking_reference=reference)
    
    context = {
        'booking': booking,
        'workshop': booking.workshop,
    }
    
    return render(request, 'workshops/booking_confirmation.html', context)


def about(request):
    """
    Over Ons pagina
    """
    context = {
        'total_workshops': Workshop.objects.filter(
            is_active=True
        ).exclude(
            status__in=['cancelled', 'completed']
        ).count(),
        'total_participants': Booking.objects.filter(status='confirmed').count(),
        'total_reviews': Review.objects.filter(is_approved=True).count(),
    }
    return render(request, 'workshops/about.html', context)


def contact(request):
    """
    Contact pagina
    """
    return render(request, 'workshops/contact.html')


def privacy_policy(request):
    """
    Privacy Policy pagina
    """
    return render(request, 'workshops/privacy_policy.html')


def terms_conditions(request):
    """
    Algemene Voorwaarden pagina
    """
    return render(request, 'workshops/terms_conditions.html')


def newsletter_subscribe(request):
    """
    Nieuwsbrief inschrijving view
    """
    if request.method == 'POST':
        form = NewsletterSubscribeForm(request.POST)
        
        if form.is_valid():
            subscriber = form.save(commit=False)
            subscriber.confirmed = True  # Auto-confirm (later kan dit via email)
            subscriber.save()
            
            messages.success(
                request,
                f'✓ Je bent succesvol ingeschreven voor de nieuwsbrief! Welkom {subscriber.first_name or "aan boord"}!'
            )
            
            # Redirect terug naar de pagina waar ze vandaan kwamen, of naar home
            next_url = request.POST.get('next', '/')
            return redirect(next_url)
        else:
            # Toon form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            
            # Redirect terug met errors
            next_url = request.POST.get('next', '/')
            return redirect(next_url)
    
    # GET request - toon form pagina
    form = NewsletterSubscribeForm()
    context = {
        'form': form,
    }
    return render(request, 'workshops/newsletter_subscribe.html', context)


def inhouse_training(request):
    """
    Inhouse Training pagina met bewerkbare HTML content
    """
    # Haal de singleton instance op
    page_content = InhouseTrainingPage.get_instance()

    context = {
        'page': page_content,
    }
    return render(request, 'workshops/inhouse_training.html', context)
