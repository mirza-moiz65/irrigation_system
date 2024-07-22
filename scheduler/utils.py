import requests
from django.utils import timezone
from datetime import timedelta
from .models import IrrigationHistory

def get_weather_data(api_key, location):
    url = f"https://api.davissystems.com/weather?location={location}&key={api_key}"
    response = requests.get(url)
    return response.json()

def get_weekly_water_usage(block):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday of this week
    end_of_week = start_of_week + timedelta(days=6)  # Sunday of this week

    histories = IrrigationHistory.objects.filter(block=block, date__range=[start_of_week, end_of_week])
    
    total_gallons = sum(h.gallons_used for h in histories)
    total_acre_feet = sum(h.acre_feet_used for h in histories)

    return total_gallons, total_acre_feet