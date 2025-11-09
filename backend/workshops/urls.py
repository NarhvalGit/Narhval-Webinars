from django.urls import path
from . import views

app_name = 'workshops'

urlpatterns = [
    # Homepage
    path('', views.WorkshopListView.as_view(), name='workshop_list'),
    
    # Workshop detail
    path('workshop/<slug:slug>/', views.WorkshopDetailView.as_view(), name='workshop_detail'),
    
    # Booking URLs
    path('workshop/<slug:slug>/boek/', views.workshop_booking, name='workshop_booking'),
    path('booking/bevestiging/<str:reference>/', views.booking_confirmation, name='booking_confirmation'),
    
    # Informatie pagina's
    path('over-ons/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('algemene-voorwaarden/', views.terms_conditions, name='terms_conditions'),
    
    # Nieuwsbrief
    path('nieuwsbrief/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Inhouse Training
    path('inhouse-trainingen/', views.inhouse_training, name='inhouse_training'),
]
