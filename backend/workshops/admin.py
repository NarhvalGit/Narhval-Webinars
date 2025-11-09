from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils import timezone
from datetime import timedelta
from .models import Category, Workshop, Booking, Review, NewsletterSubscriber, InhouseTrainingPage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'webinar_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

    def webinar_count(self, obj):
        count = obj.workshops.count()
        return format_html('<strong>{}</strong> webinars', count)
    webinar_count.short_description = 'Aantal webinars'


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'category', 
        'start_datetime', 
        'meeting_status',
        'price',
        'participants_info',
        'status_badge',
        'is_active'
    ]
    list_filter = [
        'status',
        'is_active', 
        'featured',
        'category',
        'start_datetime',
    ]
    search_fields = ['title', 'description', 'instructor_name', 'meeting_url']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_datetime'
    
    fieldsets = (
        ('Basis Informatie', {
            'fields': ('title', 'slug', 'category', 'short_description', 'description')
        }),
        ('Planning', {
            'fields': ('start_datetime', 'end_datetime', 'duration_hours')
        }),
        ('Online Meeting Details', {
            'fields': ('meeting_url', 'meeting_id', 'meeting_password'),
            'description': 'Microsoft Teams meeting informatie voor deelnemers'
        }),
        ('Capaciteit & Prijzen', {
            'fields': ('max_participants', 'min_participants', 'price')
        }),
        ('Extra Informatie', {
            'fields': (
                'materials_included',
                'requirements',
                'what_to_bring'
            ),
            'classes': ('collapse',)
        }),
        ('Instructeur', {
            'fields': ('instructor_name', 'instructor_bio')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status & Zichtbaarheid', {
            'fields': ('status', 'is_active', 'featured')
        }),
    )
    
    # Alleen created_at en updated_at readonly
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['duplicate_webinars']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:workshop_id>/duplicate/',
                self.admin_site.admin_view(self.duplicate_webinar_view),
                name='workshops_workshop_duplicate',
            ),
        ]
        return custom_urls + urls
    
    def duplicate_webinar_view(self, request, workshop_id):
        """View om een webinar te dupliceren"""
        original = Workshop.objects.get(pk=workshop_id)
        
        # Maak een kopie van de webinar
        duplicate = Workshop.objects.get(pk=workshop_id)
        duplicate.pk = None  # Maak een nieuw object
        duplicate.id = None
        
        # Update de titel en slug
        duplicate.title = f"{original.title} (Kopie)"
        duplicate.slug = f"{original.slug}-kopie-{timezone.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Verschuif de datum met 1 week (als voorbeeld)
        if original.start_datetime:
            duplicate.start_datetime = original.start_datetime + timedelta(days=7)
        if original.end_datetime:
            duplicate.end_datetime = original.end_datetime + timedelta(days=7)
        
        # Reset status naar upcoming
        duplicate.status = 'upcoming'
        duplicate.featured = False
        
        # Reset meeting URL (nieuwe meeting nodig)
        duplicate.meeting_url = ''
        duplicate.meeting_id = ''
        duplicate.meeting_password = ''
        
        # Sla de kopie op
        duplicate.save()
        
        # Redirect naar de edit pagina van de nieuwe webinar
        self.message_user(request, f'Webinar gedupliceerd! Pas nu de datum, meeting details en andere info aan.')
        return redirect('admin:workshops_workshop_change', duplicate.id)
    
    def duplicate_webinars(self, request, queryset):
        """Admin action om geselecteerde webinars te dupliceren"""
        if queryset.count() == 1:
            # Als er maar 1 geselecteerd is, ga direct naar de duplicate view
            webinar = queryset.first()
            return redirect('admin:workshops_workshop_duplicate', webinar.id)
        else:
            # Als er meerdere zijn, dupliceer ze allemaal
            count = 0
            for webinar in queryset:
                duplicate = Workshop.objects.get(pk=webinar.id)
                duplicate.pk = None
                duplicate.id = None
                duplicate.title = f"{webinar.title} (Kopie)"
                duplicate.slug = f"{webinar.slug}-kopie-{timezone.now().strftime('%Y%m%d-%H%M%S')}-{count}"
                
                if webinar.start_datetime:
                    duplicate.start_datetime = webinar.start_datetime + timedelta(days=7)
                if webinar.end_datetime:
                    duplicate.end_datetime = webinar.end_datetime + timedelta(days=7)
                
                duplicate.status = 'upcoming'
                duplicate.featured = False
                
                # Reset meeting URLs
                duplicate.meeting_url = ''
                duplicate.meeting_id = ''
                duplicate.meeting_password = ''
                
                duplicate.save()
                count += 1
            
            self.message_user(request, f'{count} webinar(s) gedupliceerd met data verschoven met 1 week.')
    
    duplicate_webinars.short_description = '📋 Dupliceer geselecteerde webinars'
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Voeg een 'Dupliceer' knop toe aan de change view"""
        extra_context = extra_context or {}
        extra_context['show_duplicate_button'] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    def meeting_status(self, obj):
        """Toon of meeting URL is ingevuld"""
        if obj.meeting_url:
            return format_html(
                '<span style="color: green;">✓ Meeting link</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Geen meeting</span>'
        )
    meeting_status.short_description = 'Meeting'
    
    def participants_info(self, obj):
        available = obj.available_spots
        total = obj.max_participants
        percentage = ((total - available) / total) * 100 if total > 0 else 0
        
        color = 'green' if percentage < 50 else 'orange' if percentage < 80 else 'red'
        return format_html(
            '<span style="color: {};">{}/{} plaatsen</span>',
            color, total - available, total
        )
    participants_info.short_description = 'Deelnemers'
    
    def status_badge(self, obj):
        colors = {
            'upcoming': '#2196F3',
            'active': '#4CAF50',
            'full': '#FF9800',
            'cancelled': '#F44336',
            'completed': '#9E9E9E',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = [
        'booking_reference',
        'first_name',
        'last_name',
        'number_of_participants',
        'status',
        'payment_status'
    ]
    readonly_fields = ['booking_reference']
    can_delete = False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_reference',
        'workshop',
        'full_name',
        'email',
        'number_of_participants',
        'total_price',
        'status_badge',
        'payment_badge',
        'created_at'
    ]
    list_filter = [
        'status',
        'payment_status',
        'created_at',
        'workshop__start_datetime'
    ]
    search_fields = [
        'booking_reference',
        'first_name',
        'last_name',
        'email',
        'phone',
        'workshop__title'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = [
        'booking_reference',
        'created_at',
        'updated_at',
        'confirmed_at',
        'cancelled_at'
    ]
    
    fieldsets = (
        ('Webinar Informatie', {
            'fields': ('workshop', 'number_of_participants')
        }),
        ('Contact Informatie', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Deelnemers Details', {
            'fields': ('participants_details', 'dietary_requirements'),
            'classes': ('collapse',)
        }),
        ('Betaling', {
            'fields': ('total_price', 'payment_status')
        }),
        ('Status & Opmerkingen', {
            'fields': ('status', 'notes')
        }),
        ('Metadata', {
            'fields': (
                'booking_reference',
                'created_at',
                'updated_at',
                'confirmed_at',
                'cancelled_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['confirm_bookings', 'cancel_bookings', 'mark_as_paid']
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Naam'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FF9800',
            'confirmed': '#4CAF50',
            'cancelled': '#F44336',
            'completed': '#2196F3',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_badge(self, obj):
        colors = {
            'unpaid': '#F44336',
            'paid': '#4CAF50',
            'refunded': '#FF9800',
        }
        color = colors.get(obj.payment_status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_badge.short_description = 'Betaling'
    
    def confirm_bookings(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} boekingen bevestigd.')
    confirm_bookings.short_description = 'Bevestig geselecteerde boekingen'
    
    def cancel_bookings(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} boekingen geannuleerd.')
    cancel_bookings.short_description = 'Annuleer geselecteerde boekingen'
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(payment_status='paid')
        self.message_user(request, f'{updated} boekingen gemarkeerd als betaald.')
    mark_as_paid.short_description = 'Markeer als betaald'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'workshop',
        'user',
        'rating_stars',
        'title',
        'is_approved',
        'created_at'
    ]
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['title', 'comment', 'workshop__title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<span style="font-size: 16px;">{}</span>', stars)
    rating_stars.short_description = 'Rating'
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews goedgekeurd.')
    approve_reviews.short_description = 'Keur geselecteerde reviews goed'
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews afgekeurd.')
    disapprove_reviews.short_description = 'Keur geselecteerde reviews af'


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'full_name',
        'status_badge',
        'confirmed',
        'subscribed_at',
    ]
    list_filter = [
        'is_active',
        'confirmed',
        'subscribed_at',
    ]
    search_fields = [
        'email',
        'first_name',
        'last_name',
    ]
    date_hierarchy = 'subscribed_at'
    readonly_fields = ['subscribed_at', 'unsubscribed_at']
    
    fieldsets = (
        ('Contact Informatie', {
            'fields': ('email', 'first_name', 'last_name')
        }),
        ('Status', {
            'fields': ('is_active', 'confirmed')
        }),
        ('Interesses (optioneel)', {
            'fields': ('interests',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('subscribed_at', 'unsubscribed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_subscribers', 'deactivate_subscribers', 'export_emails']
    
    def full_name(self, obj):
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return '-'
    full_name.short_description = 'Naam'
    
    def status_badge(self, obj):
        if obj.is_active:
            color = '#4CAF50'
            text = '✓ Actief'
        else:
            color = '#F44336'
            text = '✗ Inactief'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, text
        )
    status_badge.short_description = 'Status'
    
    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(request, f'{updated} inschrijvingen geactiveerd.')
    activate_subscribers.short_description = 'Activeer geselecteerde inschrijvingen'
    
    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f'{updated} inschrijvingen gedeactiveerd.')
    deactivate_subscribers.short_description = 'Deactiveer geselecteerde inschrijvingen'
    
    def export_emails(self, request, queryset):
        """Export email adressen naar clipboard-friendly formaat"""
        emails = queryset.filter(is_active=True).values_list('email', flat=True)
        email_list = ', '.join(emails)
        
        self.message_user(
            request,
            f'Email adressen ({len(emails)}): {email_list}',
            level='success'
        )
    export_emails.short_description = '📧 Exporteer email adressen'


@admin.register(InhouseTrainingPage)
class InhouseTrainingPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Homepage Banner', {
            'fields': ('banner_title', 'banner_description', 'banner_button_text'),
            'description': 'Deze velden worden getoond op de homepage in de banner sectie.'
        }),
        ('Pagina Inhoud', {
            'fields': ('content',),
            'description': '''
                <p><strong>HTML Editor voor Inhouse Training Pagina</strong></p>
                <p>Gebruik dit veld om de volledige inhoud van de inhouse training pagina op te maken met HTML.</p>
                <p>Je kunt alle HTML tags gebruiken, inclusief:</p>
                <ul>
                    <li>Tailwind CSS classes voor styling (bijv. <code>class="text-3xl font-bold"</code>)</li>
                    <li>Bootstrap Icons (bijv. <code>&lt;i class="bi bi-building"&gt;&lt;/i&gt;</code>)</li>
                    <li>Grid layouts, containers, buttons, etc.</li>
                </ul>
                <p>De huidige styling volgt het Tailwind CSS framework dat in de rest van de site wordt gebruikt.</p>
            '''
        }),
        ('Status', {
            'fields': ('is_active', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['updated_at']

    class Media:
        css = {
            'all': ('admin/css/inhouse_training_admin.css',)
        }

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Customize the content field to use a larger textarea"""
        if db_field.name == 'content':
            kwargs['widget'] = admin.widgets.AdminTextareaWidget(attrs={
                'rows': 30,
                'cols': 120,
                'style': 'font-family: monospace; font-size: 13px;'
            })
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def has_add_permission(self, request):
        # Singleton - er kan maar 1 instance zijn
        return not InhouseTrainingPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Singleton mag niet verwijderd worden
        return False
