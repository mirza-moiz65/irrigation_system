from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import *
from .models import *
from .utils import *

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def home(request):
    ranches = Ranch.objects.all()
    return render(request, 'scheduler/home.html', {'ranches': ranches})

@login_required
def create_ranch(request):
    if request.method == 'POST':
        ranch_form = RanchForm(request.POST)
        if ranch_form.is_valid():
            ranch = ranch_form.save()
            return redirect('ranch_detail', ranch_id=ranch.id)
    else:
        ranch_form = RanchForm()
    return render(request, 'scheduler/create_ranch.html', {'ranch_form': ranch_form})

@login_required
def ranch_detail(request, ranch_id):
    ranch = Ranch.objects.get(id=ranch_id)
    blocks = Block.objects.filter(set__ranch=ranch)
    return render(request, 'scheduler/ranch_detail.html', {'ranch': ranch, 'blocks': blocks})

@login_required
def create_block(request, ranch_id):
    ranch = Ranch.objects.get(id=ranch_id)
    if request.method == 'POST':
        block_form = BlockForm(request.POST)
        if block_form.is_valid():
            block = block_form.save(commit=False)
            block.set = ranch.irrigation_sets.first()  # Or however you determine the set
            block.save()
            return redirect('ranch_detail', ranch_id=ranch.id)
    else:
        block_form = BlockForm()
    return render(request, 'scheduler/create_block.html', {'block_form': block_form, 'ranch': ranch})

@login_required
def create_irrigation_set(request, ranch_id):
    ranch = Ranch.objects.get(id=ranch_id)
    if request.method == 'POST':
        set_form = IrrigationSetForm(request.POST)
        if set_form.is_valid():
            set_form.save()
            return redirect('ranch_detail', ranch_id=ranch.id)
    else:
        set_form = IrrigationSetForm(initial={'ranch': ranch})
    return render(request, 'scheduler/create_irrigation_set.html', {'set_form': set_form, 'ranch': ranch})

@login_required
def create_irrigation_schedule(request, ranch_id):
    ranch = Ranch.objects.get(id=ranch_id)
    blocks = Block.objects.filter(set__ranch=ranch)

    if request.method == 'POST':
        schedule_form = IrrigationScheduleForm(request.POST)
        if schedule_form.is_valid():
            for block in schedule_form.cleaned_data['blocks']:
                schedule = schedule_form.save(commit=False)
                schedule.block = block
                if not schedule.minutes_needed:
                    schedule.minutes_needed = schedule.calculate_irrigation_time()
                schedule.hours_needed = schedule.minutes_needed / 60
                schedule.save()

                # Calculate gallons and acre-feet used
                gallons_used = float(block.gpm) * float(schedule.minutes_needed)
                acre_feet_used = gallons_used / 27154  # 1 acre-foot = 27154 gallons

                # Save historical data
                IrrigationHistory.objects.create(
                    block=block,
                    minutes_irrigated=schedule.minutes_needed,
                    gallons_used=gallons_used,
                    acre_feet_used=acre_feet_used,
                    days_between_irrigations=block.days_between_irrigations if not block.has_crop_x else None,
                    interval_between_irrigations=block.interval_between_irrigations if block.has_crop_x else None,
                    well=schedule.well
                )
            return redirect('ranch_detail', ranch_id=ranch.id)
    else:
        schedule_form = IrrigationScheduleForm()

    return render(request, 'scheduler/create_irrigation_schedule.html', {'schedule_form': schedule_form, 'ranch': ranch, 'blocks': blocks})

@login_required
def block_history(request, block_id):
    block = Block.objects.get(id=block_id)
    histories = IrrigationHistory.objects.filter(block=block).order_by('-date')
    weekly_gallons, weekly_acre_feet = get_weekly_water_usage(block)
    return render(request, 'scheduler/block_history.html', {
        'block': block,
        'histories': histories,
        'weekly_gallons': weekly_gallons,
        'weekly_acre_feet': weekly_acre_feet
    })    

@login_required
def create_water_meter_reading(request):
    if request.method == 'POST':
        form = WaterMeterReadingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = WaterMeterReadingForm()
    return render(request, 'scheduler/create_water_meter_reading.html', {'form': form})

@login_required
def ranch_allocation_status(request, ranch_id):
    ranch = Ranch.objects.get(id=ranch_id)
    readings = WaterMeterReading.objects.filter(ranch=ranch).order_by('-date')

    total_gallons = sum(r.gallons for r in readings if r.gallons is not None)
    total_acre_feet = sum(r.acre_feet for r in readings if r.acre_feet is not None)

    return render(request, 'scheduler/ranch_allocation_status.html', {
        'ranch': ranch,
        'readings': readings,
        'total_gallons': total_gallons,
        'total_acre_feet': total_acre_feet,
        'allocation_remaining': ranch.allocation - total_acre_feet
    })

@login_required
def create_well(request, ranch_id):
    if request.method == 'POST':
        form = WellForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('well_list', ranch_id=ranch_id)
    else:
        initial = {'ranch': ranch_id} if ranch_id else {}
        form = WellForm(initial=initial)
    return render(request, 'scheduler/create_well.html', {'form': form})

@login_required
def well_list(request, ranch_id):
    ranch = Ranch.objects.get(id=ranch_id)
    wells = Well.objects.filter(ranch=ranch)
    return render(request, 'scheduler/well_list.html', {'ranch': ranch, 'wells': wells})

@login_required
def ranch_report(request, ranch_id):
    ranch = Ranch.objects.get(id=ranch_id)
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
    else:
        from_date = timezone.now().date() - timedelta(days=7)
        to_date = timezone.now().date()
        form = DateRangeForm(initial={'from_date': from_date, 'to_date': to_date})

    histories = IrrigationHistory.objects.filter(block__set__ranch=ranch, date__range=[from_date, to_date]).order_by('date', 'block__set', 'block')

    report_data = []
    for date in (from_date + timedelta(days=n) for n in range((to_date - from_date).days + 1)):
        day_histories = histories.filter(date=date)
        if day_histories.exists():
            day_data = {
                'date': date,
                'day': date.strftime('%A'),
                'histories': day_histories
            }
            report_data.append(day_data)

    return render(request, 'scheduler/ranch_report.html', {'ranch': ranch, 'report_data': report_data, 'form': form})
  