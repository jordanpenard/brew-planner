# Generated by Django 4.1.7 on 2023-03-22 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0010_recipe_fermentation_temperature_c_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brew',
            name='state',
            field=models.CharField(choices=[('Prep', 'Prep'), ('Mash', 'Mash'), ('Boil', 'Boil'), ('Fermenting', 'Fermenting'), ('Completed', 'Completed')], default='Prep', max_length=20),
        ),
    ]
