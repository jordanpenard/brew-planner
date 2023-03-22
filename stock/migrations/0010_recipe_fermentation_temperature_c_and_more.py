# Generated by Django 4.1.7 on 2023-03-22 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0009_brew_evaporation_lph_brew_mash_thickness_lpkg_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='fermentation_temperature_c',
            field=models.FloatField(default=18),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='mash_temperature_c',
            field=models.FloatField(default=65),
        ),
    ]
