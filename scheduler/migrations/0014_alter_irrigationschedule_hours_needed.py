# Generated by Django 5.0.6 on 2024-07-21 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0013_remove_block_distribution_uniformity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='irrigationschedule',
            name='hours_needed',
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=10, null=True),
        ),
    ]
