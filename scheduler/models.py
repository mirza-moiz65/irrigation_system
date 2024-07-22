# scheduler/models.py
from django.db import models

class Ranch(models.Model):
    name = models.CharField(max_length=100)
    allocation = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class IrrigationSet(models.Model):
    number = models.PositiveIntegerField()
    ranch = models.ForeignKey(Ranch, on_delete=models.CASCADE, related_name='irrigation_sets')

    def __str__(self):
        return f"Set {self.number} - {self.ranch.name}"

class Well(models.Model):
    name = models.CharField(max_length=100)
    ranch = models.ForeignKey(Ranch, on_delete=models.CASCADE, related_name='wells')
    gpm = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.name} - {self.ranch.name}"

class Block(models.Model):
    name = models.CharField(max_length=100)
    set = models.ForeignKey(IrrigationSet, on_delete=models.CASCADE, related_name='blocks')
    variety = models.CharField(max_length=100)
    acreage = models.DecimalField(max_digits=10, decimal_places=2)
    gpm = models.DecimalField(max_digits=10, decimal_places=2)
    tree_spacing = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    emitter_output = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    has_crop_x = models.BooleanField(default=True)
    et_crop_coefficient = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    days_between_irrigations = models.IntegerField(null=True, blank=True)
    interval_between_irrigations = models.IntegerField(null=True, blank=True)
    water_quality = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    well = models.ForeignKey(Well, on_delete=models.CASCADE, related_name='blocks', null=True, blank=True)

    def __str__(self):
        return f"Block {self.name} - {self.variety} - Set {self.set.number}"

class IrrigationSchedule(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    minutes_needed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hours_needed = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    inches_needed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    leaching_factor = models.DecimalField(max_digits=10, decimal_places=2)
    fertilized = models.BooleanField(default=False)
    fertilization_details = models.TextField(blank=True, null=True)
    well = models.ForeignKey(Well, on_delete=models.CASCADE, related_name='irrigation_schedules', null=True, blank=True)
    reference_evapotranspiration = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    distribution_uniformity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.minutes_needed is None:
            self.minutes_needed = self.calculate_irrigation_time()
        self.hours_needed = self.minutes_needed / 60
        super().save(*args, **kwargs)

    def calculate_irrigation_time(self):
        if self.block.has_crop_x:
            return self.inches_needed * 27154 / self.block.gpm  # Adjust this calculation as needed
        else:
            return self.irrigation_calculator()

    def irrigation_calculator(self):
        try:
            ETo = float(self.reference_evapotranspiration or 0)
            Kc = float(self.block.et_crop_coefficient or 0)
            DU = float(self.distribution_uniformity or 0) / 100
            LR = float(self.leaching_factor or 0) / 100

            tpa = 43560 / (float(self.block.tree_spacing or 1) * float(self.block.tree_spacing or 1))
            cvg = 1
            EmittersPerTree = float(self.block.emitter_output or 1)
            EmitterOutput = float(self.block.gpm or 1)
            groveSize = float(self.block.acreage or 1)

            ETcrop = ETo * Kc
            ETc = ETcrop / DU
            GalPerAcreInch = 27154
            GalPerTree = ((ETc * GalPerAcreInch * cvg) / tpa) * (1.0 + LR)

            HoursPerTree = round(100 * GalPerTree / (EmittersPerTree * EmitterOutput)) / 100
            return HoursPerTree * 60  # convert hours to minutes
        except ValueError as e:
            return {'error': f'Invalid input: {str(e)}'}

    def __str__(self):
        return f"Irrigation Schedule for {self.block.name} - {self.hours_needed} hours"

class IrrigationHistory(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='irrigation_histories')
    date = models.DateField(auto_now_add=True)
    minutes_irrigated = models.DecimalField(max_digits=10, decimal_places=2)
    gallons_used = models.DecimalField(max_digits=15, decimal_places=2)
    acre_feet_used = models.DecimalField(max_digits=10, decimal_places=4)
    days_between_irrigations = models.IntegerField(null=True, blank=True)
    interval_between_irrigations = models.IntegerField(null=True, blank=True)
    well = models.ForeignKey(Well, on_delete=models.CASCADE, related_name='irrigation_histories', null=True, blank=True)

    def __str__(self):
        return f"Irrigation History for {self.block.name} on {self.date}"

class WaterMeterReading(models.Model):
    ranch = models.ForeignKey(Ranch, on_delete=models.CASCADE, related_name='water_meter_readings')
    well = models.ForeignKey(Well, on_delete=models.CASCADE, related_name='water_meter_readings', null=True, blank=True)
    date = models.DateField()
    gallons = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    acre_feet = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"Water Meter Reading for {self.ranch.name} on {self.date}"
