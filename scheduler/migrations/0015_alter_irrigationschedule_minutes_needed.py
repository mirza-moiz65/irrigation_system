# Generated by Django 5.0.6 on 2024-07-21 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0014_alter_irrigationschedule_hours_needed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='irrigationschedule',
            name='minutes_needed',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
