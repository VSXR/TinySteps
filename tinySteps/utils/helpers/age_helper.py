from dateutil.relativedelta import relativedelta
from django.utils import timezone

def calculate_age_in_months(birth_date):
    """Calculate age in months based on birth date"""
    if not birth_date:
        return 0
        
    today = timezone.now().date()
    diff = relativedelta(today, birth_date)
    months = diff.years * 12 + diff.months
    
    return months

def calculate_age_range(age_months):
    """Determine the age range category for a given age in months"""
    if age_months < 0:
        return '0-6'  # Default to youngest range for invalid values
    elif age_months < 6:
        return '0-6'  # 0-6 months
    elif age_months < 12:
        return '6-12'  # 6-12 months
    elif age_months < 24:
        return '12-24'  # 1-2 years
    else:
        return '24+'  # 2+ years

def get_age_appropriate_content(age_months, content_items):
    """Filter content items based on age"""
    if not age_months or not content_items:
        return []
        
    appropriate_items = []
    for item in content_items:
        # If item has min_age and max_age attributes
        min_age = getattr(item, 'min_age', 0)
        max_age = getattr(item, 'max_age', 999)  # Large number means no upper limit
        
        if min_age <= age_months and (max_age is None or age_months <= max_age):
            appropriate_items.append(item)
            
    return appropriate_items

def get_next_milestone_age(current_age_months):
    """Getthe next developmental milestone age based on current age in months"""
    milestone_ages = [1, 2, 4, 6, 9, 12, 15, 18, 24, 36, 48, 60]
    for age in milestone_ages:
        if current_age_months < age:
            return age
            
    # If older than all milestones, return the last one
    return milestone_ages[-1]

def format_age_display(age_months):
    """Format age for display in years and months"""
    if age_months < 0:
        return "0 months"
        
    years = age_months // 12
    remaining_months = age_months % 12
    
    if years == 0:
        return f"{age_months} month{'s' if age_months != 1 else ''}"
    elif remaining_months == 0:
        return f"{years} year{'s' if years != 1 else ''}"
    else:
        return f"{years} year{'s' if years != 1 else ''}, {remaining_months} month{'s' if remaining_months != 1 else ''}"