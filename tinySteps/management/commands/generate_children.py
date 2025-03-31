from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tinySteps.models import YourChild_Model
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Generates random children profiles for testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=5, help='Number of children to create per user')
        parser.add_argument('--clear', action='store_true', help='Clear existing children before creating new ones')

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        
        if clear:
            YourChild_Model.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All child profiles have been deleted'))
        
        # Get all users who are not superusers
        users = User.objects.filter(is_active=True)
        total_created = 0
        
        for user in users:
            created_count = 0
            
            for _ in range(count):
                try:
                    # Generate random child data
                    gender = random.choice(['Male', 'Female'])
                    name = self._generate_name(gender)
                    
                    # Generate birth date for a child between 0-8 years old
                    today = date.today()
                    max_days = 365 * 8  # 8 years in days
                    random_days = random.randint(0, max_days)
                    birth_date = today - timedelta(days=random_days)
                    
                    # Calculate age in months
                    age_in_months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
                    
                    # Create the child profile
                    child = YourChild_Model(
                        user=user,
                        name=name,
                        gender=gender,
                        birth_date=birth_date,
                        age=age_in_months,  # Adding the age field that was missing
                    )
                    child.save()
                    created_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating child profile: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS(f'{created_count} child profiles have been created for user {user.username}'))
            total_created += created_count
        
        self.stdout.write(self.style.SUCCESS(f'Total: {total_created} child profiles have been created'))
    
    def _generate_name(self, gender):
        male_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles']
        female_names = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen']
        
        if gender == 'Male':
            return random.choice(male_names)
        else:
            return random.choice(female_names)