from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Category, Workshop, Booking, Review


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Houtbewerking',
            slug='houtbewerking',
            description='Workshops over houtbewerking'
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Houtbewerking')
        self.assertEqual(str(self.category), 'Houtbewerking')


class WorkshopModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.workshop = Workshop.objects.create(
            title='Test Workshop',
            slug='test-workshop',
            description='Een test workshop',
            category=self.category,
            start_datetime=timezone.now() + timedelta(days=7),
            end_datetime=timezone.now() + timedelta(days=7, hours=3),
            duration_hours=3.0,
            location='Test Locatie',
            city='Gent',
            max_participants=10,
            min_participants=3,
            price=50.00,
            instructor_name='Test Instructeur',
            status='upcoming'
        )
    
    def test_workshop_creation(self):
        self.assertEqual(self.workshop.title, 'Test Workshop')
        self.assertEqual(self.workshop.max_participants, 10)
    
    def test_available_spots(self):
        # Geen boekingen = alle plaatsen beschikbaar
        self.assertEqual(self.workshop.available_spots, 10)
    
    def test_is_full(self):
        self.assertFalse(self.workshop.is_full)


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.workshop = Workshop.objects.create(
            title='Test Workshop',
            slug='test-workshop',
            description='Een test workshop',
            category=self.category,
            start_datetime=timezone.now() + timedelta(days=7),
            end_datetime=timezone.now() + timedelta(days=7, hours=3),
            duration_hours=3.0,
            location='Test Locatie',
            max_participants=10,
            price=50.00,
            instructor_name='Test Instructeur'
        )
        self.booking = Booking.objects.create(
            workshop=self.workshop,
            user=self.user,
            number_of_participants=2,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='0123456789',
            total_price=100.00
        )
    
    def test_booking_creation(self):
        self.assertEqual(self.booking.number_of_participants, 2)
        self.assertEqual(self.booking.total_price, 100.00)
    
    def test_booking_reference_generated(self):
        self.assertTrue(self.booking.booking_reference.startswith('WS'))
        self.assertEqual(len(self.booking.booking_reference), 10)  # WS + 8 characters


# Voeg meer tests toe voor:
# - Review model
# - Workshop filtering
# - Booking validation
# - etc.
