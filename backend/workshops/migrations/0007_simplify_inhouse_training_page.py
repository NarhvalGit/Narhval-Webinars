# Generated manually for inhouse training page simplification

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshops', '0006_inhousetrainingpage'),
    ]

    operations = [
        # Voeg het nieuwe content veld toe
        migrations.AddField(
            model_name='inhousetrainingpage',
            name='content',
            field=models.TextField(
                blank=True,
                default='',
                help_text='HTML content voor de inhouse trainingen pagina. Je kunt hier volledige HTML gebruiken voor opmaak.',
                verbose_name='Pagina Inhoud'
            ),
        ),

        # Update banner_description default
        migrations.AlterField(
            model_name='inhousetrainingpage',
            name='banner_description',
            field=models.TextField(
                default='Ontdek onze inhouse trainingen: volledig aangepast aan de behoeften van jouw organisatie.',
                help_text='Korte beschrijving op de homepage',
                verbose_name='Banner Beschrijving (Homepage)'
            ),
        ),

        # Update banner_title verbose_name
        migrations.AlterField(
            model_name='inhousetrainingpage',
            name='banner_title',
            field=models.CharField(
                default='Op zoek naar opleidingen op maat voor jouw team?',
                help_text='Titel die getoond wordt op de homepage',
                max_length=200,
                verbose_name='Banner Titel (Homepage)'
            ),
        ),

        # Update banner_button_text verbose_name
        migrations.AlterField(
            model_name='inhousetrainingpage',
            name='banner_button_text',
            field=models.CharField(
                default='Ontdek Inhouse Opleidingen',
                max_length=50,
                verbose_name='Banner Knop Tekst (Homepage)'
            ),
        ),

        # Verwijder oude velden die niet meer nodig zijn
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='page_title',
        ),
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='intro_text',
        ),
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='benefits_title',
        ),
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='benefits',
        ),
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='process_title',
        ),
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='process_description',
        ),
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='process_steps',
        ),
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='topics_title',
        ),
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='topics_description',
        ),
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='cta_title',
        ),
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='cta_description',
        ),
        migrations.RemoveField(
            model_name='inhousetrainingpage',
            name='cta_button_text',
        ),
    ]
