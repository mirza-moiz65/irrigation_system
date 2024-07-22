# scheduler/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.utils import timezone
from datetime import timedelta


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class RanchForm(forms.ModelForm):
    class Meta:
        model = Ranch
        fields = ['name', 'allocation']

class WellForm(forms.ModelForm):
    class Meta:
        model = Well
        fields = ['name', 'ranch', 'gpm']


class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = [
            'name', 'set', 'variety', 'acreage', 'gpm', 'water_quality', 'tree_spacing', 'emitter_output',
            'has_crop_x', 'et_crop_coefficient', 'days_between_irrigations', 'interval_between_irrigations', 'well'
        ]
        widgets = {
            'et_crop_coefficient': forms.NumberInput(attrs={'step': '0.01'}),
            'days_between_irrigations': forms.NumberInput(attrs={'step': '1'}),
            'interval_between_irrigations': forms.NumberInput(attrs={'step': '1'}),
            'tree_spacing': forms.NumberInput(attrs={'step': '0.01'}),
            'emitter_output': forms.NumberInput(attrs={'step': '0.01'}),
            'water_quality': forms.NumberInput(attrs={'step': '0.01'}),
        }

class IrrigationSetForm(forms.ModelForm):
    class Meta:
        model = IrrigationSet
        fields = ['number', 'ranch']

class IrrigationScheduleForm(forms.ModelForm):
    blocks = forms.ModelMultipleChoiceField(queryset=Block.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = IrrigationSchedule
        fields = [
            'blocks', 'minutes_needed', 'inches_needed', 'leaching_factor', 'fertilized', 
            'fertilization_details', 'well', 'reference_evapotranspiration', 
            'distribution_uniformity'
        ]
        widgets = {
            'well': forms.Select(),
            'reference_evapotranspiration': forms.NumberInput(attrs={'step': '0.01'}),
            'distribution_uniformity': forms.NumberInput(attrs={'step': '0.01'}),
        }

class WaterMeterReadingForm(forms.ModelForm):
    class Meta:
        model = WaterMeterReading
        fields = ['ranch', 'well', 'date', 'gallons', 'acre_feet']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        gallons = cleaned_data.get('gallons')
        acre_feet = cleaned_data.get('acre_feet')

        if not gallons and not acre_feet:
            raise forms.ValidationError("Either gallons or acre-feet must be provided.")

        if gallons and not acre_feet:
            cleaned_data['acre_feet'] = gallons / 27154  # Convert gallons to acre-feet
        if acre_feet and not gallons:
            cleaned_data['gallons'] = acre_feet * 27154  # Convert acre-feet to gallons

        return cleaned_data
      
class DateRangeForm(forms.Form):
    from_date = forms.DateField(initial=timezone.now().date() - timedelta(days=7), widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(initial=timezone.now().date(), widget=forms.DateInput(attrs={'type': 'date'}))
