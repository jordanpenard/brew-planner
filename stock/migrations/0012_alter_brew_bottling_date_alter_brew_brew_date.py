# Generated by Django 4.1.7 on 2023-03-22 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0011_alter_brew_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brew',
            name='bottling_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='brew',
            name='brew_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
