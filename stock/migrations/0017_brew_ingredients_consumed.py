# Generated by Django 4.1.7 on 2023-04-12 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0016_brew_brew_monitor_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='brew',
            name='ingredients_consumed',
            field=models.BooleanField(default=False),
        ),
    ]
