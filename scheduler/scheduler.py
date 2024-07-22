from .models import Block

def generate_irrigation_schedule(ranch):
    blocks = Block.objects.filter(set__ranch=ranch).order_by('set__number')
    schedule = []
    for block in blocks:
        schedule.append({
            'block': block,
            'irrigation_time': calculate_irrigation_time(block),
            'fertilization': get_fertilization_info(block),
        })
    return schedule

def calculate_irrigation_time(block):
    # Assume 1 inch of water per acre requires 27,154 gallons of water
    gallons_per_inch_per_acre = 27154
    
    if block.has_crop_x:
        # Calculate total gallons needed for the block
        total_gallons_needed = block.acreage * gallons_per_inch_per_acre * block.inches_needed
    else:
        # Use ET crop coefficient if crop X is not present
        et_coefficient = block.et_crop_coefficient or 1.0
        total_gallons_needed = block.acreage * gallons_per_inch_per_acre * et_coefficient

    # Calculate irrigation time in minutes
    irrigation_time = total_gallons_needed / block.gpm

    return irrigation_time

def get_fertilization_info(block):
    # Check if the block needs fertilization this week
    if block.fertilized:
        return {
            'fertilized': True,
            'details': block.fertilization_details
        }
    else:
        return {
            'fertilized': False,
            'details': None
        }
