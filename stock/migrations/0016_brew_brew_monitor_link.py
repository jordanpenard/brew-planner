# Generated by Django 4.1.7 on 2023-03-23 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0015_brew_bottling_volume_l'),
    ]

    operations = [
        migrations.AddField(
            model_name='brew',
            name='brew_monitor_link',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]
