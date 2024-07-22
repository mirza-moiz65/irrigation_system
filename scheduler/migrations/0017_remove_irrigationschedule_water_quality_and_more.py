# Generated by Django 5.0.6 on 2024-07-21 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0016_remove_block_inches_needed_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='irrigationschedule',
            name='water_quality',
        ),
        migrations.AddField(
            model_name='block',
            name='water_quality',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='irrigationschedule',
            name='inches_needed',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
