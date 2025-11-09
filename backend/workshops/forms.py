from django import forms
from django.core.exceptions import ValidationError
from .models import Booking, Workshop, NewsletterSubscriber


class BookingForm(forms.ModelForm):
    """
    Form voor het boeken van een workshop
    """
    
    # Extra velden voor niet-ingelogde gebruikers
    name = forms.CharField(
        label='Volledige Naam',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bijv. Jan Janssens'
        })
    )
    
    email = forms.EmailField(
        label='E-mailadres',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'jan.janssens@email.com'
        })
    )
    
    phone = forms.CharField(
        label='Telefoonnummer',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+32 123 45 67 89'
        })
    )
    
    num_participants = forms.IntegerField(
        label='Aantal Deelnemers',
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1',
            'value': '1',
            'min': '1'
        })
    )
    
    notes = forms.CharField(
        label='Opmerkingen (optioneel)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Bijv. dieetwensen, vragen, speciale verzoeken...'
        })
    )
    
    # Acceptatie voorwaarden
    accept_terms = forms.BooleanField(
        label='Ik ga akkoord met de algemene voorwaarden',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = Booking
        fields = ['num_participants', 'notes']
    
    def __init__(self, *args, workshop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.workshop = workshop
        
        # Zet default waarde op 1
        if 'initial' not in kwargs:
            self.fields['num_participants'].initial = 1
        
        # Als er een workshop is, update het label met de prijs
        if self.workshop:
            self.fields['num_participants'].label = f'Aantal Deelnemers (€{self.workshop.price} per persoon)'
            
            # Zet alleen max op basis van beschikbare plaatsen
            available_spots = self.workshop.available_spots
            if available_spots:
                self.fields['num_participants'].widget.attrs['max'] = available_spots
                self.fields['num_participants'].help_text = f'Nog {available_spots} plaatsen beschikbaar'
    
    def clean_num_participants(self):
        """
        Valideer aantal deelnemers tegen beschikbare plaatsen
        GEEN minimum restrictie meer!
        """
        num_participants = self.cleaned_data.get('num_participants')
        
        if not self.workshop:
            return num_participants
        
        # Check dat het minimum 1 is (altijd)
        if num_participants < 1:
            raise ValidationError('Je moet minimaal 1 deelnemer opgeven.')
        
        # Check beschikbare plaatsen
        available_spots = self.workshop.available_spots
        if available_spots is not None and num_participants > available_spots:
            if available_spots == 0:
                raise ValidationError('Deze workshop is helaas volgeboekt.')
            else:
                raise ValidationError(
                    f'Er zijn nog maar {available_spots} plaatsen beschikbaar.'
                )
        
        # Check maximaal aantal deelnemers (van de workshop)
        if self.workshop.max_participants and num_participants > self.workshop.max_participants:
            raise ValidationError(
                f'Maximum aantal deelnemers is {self.workshop.max_participants}.'
            )
        
        return num_participants
    
    def clean_email(self):
        """
        Valideer email formaat
        """
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
        return email
    
    def clean_phone(self):
        """
        Cleanup telefoon nummer
        """
        phone = self.cleaned_data.get('phone')
        if phone:
            # Verwijder spaties en streepjes
            phone = phone.replace(' ', '').replace('-', '')
        return phone


class NewsletterSubscribeForm(forms.ModelForm):
    """
    Form voor nieuwsbrief inschrijving
    """
    
    email = forms.EmailField(
        label='Email adres',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'jouw@email.be'
        })
    )
    
    first_name = forms.CharField(
        label='Voornaam',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Voornaam (optioneel)'
        })
    )
    
    class Meta:
        model = NewsletterSubscriber
        fields = ['email', 'first_name']
    
    def clean_email(self):
        """
        Valideer of email al bestaat
        """
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            
            # Check of email al bestaat en actief is
            if NewsletterSubscriber.objects.filter(email=email, is_active=True).exists():
                raise ValidationError('Dit email adres is al ingeschreven voor de nieuwsbrief.')
        
        return email
