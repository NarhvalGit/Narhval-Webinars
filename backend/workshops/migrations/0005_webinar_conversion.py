# Generated manually for webinar conversion

from django.db import migrations, models
from django.core.validators import MinValueValidator, MaxValueValidator
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workshops', '0004_newslettersubscriber'),
    ]

    operations = [
        # Verwijder oude locatie velden
        migrations.RemoveField(
            model_name='workshop',
            name='location',
        ),
        migrations.RemoveField(
            model_name='workshop',
            name='address',
        ),
        migrations.RemoveField(
            model_name='workshop',
            name='city',
        ),
        
        # Voeg nieuwe online meeting velden toe
        migrations.AddField(
            model_name='workshop',
            name='meeting_url',
            field=models.URLField(blank=True, help_text='Link naar de Microsoft Teams meeting', max_length=500, verbose_name='Teams Meeting URL'),
        ),
        migrations.AddField(
            model_name='workshop',
            name='meeting_id',
            field=models.CharField(blank=True, help_text='Optioneel meeting ID voor deelnemers', max_length=100, verbose_name='Meeting ID'),
        ),
        migrations.AddField(
            model_name='workshop',
            name='meeting_password',
            field=models.CharField(blank=True, help_text='Optioneel wachtwoord voor de meeting', max_length=100, verbose_name='Meeting Wachtwoord'),
        ),
        
        # Update max_participants voor online webinars (500 ipv 100)
        migrations.AlterField(
            model_name='workshop',
            name='max_participants',
            field=models.PositiveIntegerField(
                validators=[MinValueValidator(1), MaxValueValidator(500)], 
                verbose_name='Maximum aantal deelnemers'
            ),
        ),
        
        # Update requirements help text
        migrations.AlterField(
            model_name='workshop',
            name='requirements',
            field=models.TextField(blank=True, help_text='Bijv. ervaring, benodigde software, etc.', verbose_name='Vereisten'),
        ),
        
        # Update what_to_bring help text
        migrations.AlterField(
            model_name='workshop',
            name='what_to_bring',
            field=models.TextField(blank=True, help_text='Benodigde materialen voor thuis', verbose_name='Wat meenemen'),
        ),
        
        # Update Booking verbose name
        migrations.AlterField(
            model_name='booking',
            name='workshop',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, 
                related_name='bookings', 
                to='workshops.workshop', 
                verbose_name='Webinar'
            ),
        ),
        
        # Update Review verbose name
        migrations.AlterField(
            model_name='review',
            name='workshop',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, 
                related_name='reviews', 
                to='workshops.workshop', 
                verbose_name='Webinar'
            ),
        ),
        
        # Update Workshop Meta
        migrations.AlterModelOptions(
            name='workshop',
            options={'ordering': ['-start_datetime'], 'verbose_name': 'Webinar', 'verbose_name_plural': 'Webinars'},
        ),
    ]
