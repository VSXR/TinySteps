import random
import json
import os
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from tinySteps.models import YourChild_Model
from django.db.utils import IntegrityError
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate random baby records for testing purposes'

    def add_arguments(self, parser):
        default_count = random.randint(3, 10)
        
        parser.add_argument(
            '--count',
            type=int,
            default=default_count,
            help=f'Number of baby records to create (random default: {default_count})'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing baby records before creating new ones'
        )

        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Username to assign babies to (REQUIRED)'
        )

    def setup_json_files(self):
        """Create and initialize JSON data files if they don't exist"""
        json_base_dir = os.path.join('tinySteps', 'management', 'commands', 'tinySteps_jsons')
        json_dir = os.path.join(json_base_dir, 'babies')
        
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
            self.stdout.write(self.style.WARNING(f"Created directory: {json_dir}"))
        
        # List of JSON files to create if they don't exist
        json_files = {
            'boy_names.json': ["Lucas", "Hugo", "Mateo", "Martín", "Leo", "Daniel", "Alejandro", "Manuel", "Pablo", "Álvaro", 
                             "Adrián", "Mario", "Diego", "David", "Oliver", "Carlos", "Gabriel", "Marcos", "Thiago", "Enzo"],
            'girl_names.json': ["Lucía", "Sofía", "Martina", "María", "Julia", "Paula", "Valeria", "Emma", "Daniela", "Carla", 
                              "Alba", "Noa", "Alma", "Sara", "Carmen", "Vega", "Olivia", "Claudia", "Jimena", "Lola"],
            'last_names.json': ["García", "Rodríguez", "González", "Fernández", "López", "Martínez", "Sánchez", "Pérez", 
                              "Gómez", "Martín", "Jiménez", "Ruiz", "Hernández", "Díaz", "Moreno", "Álvarez", "Romero", 
                              "Alonso", "Gutiérrez", "Navarro"],
            'descriptions.json': ["Very active and always smiling", "Calm and observant", "Curious about everything", 
                                "Loves to play with toys", "Very talkative", "Enjoys bath time", "Loves to be outdoors", 
                                "Giggles a lot", "Very social with other babies", "Enjoys music and dancing", 
                                "Loves looking at picture books", "Very expressive faces", "Learning new skills quickly", 
                                "Enjoys family gatherings", "Very determined", "Loves animal toys", "Sleeps very well", 
                                "Enjoys meal times", "Very affectionate", "Always on the move"]
        }
        
        result = {}
        
        # Create each file if it doesn't exist
        for filename, default_data in json_files.items():
            file_path = os.path.join(json_dir, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, indent=2, ensure_ascii=False)
                self.stdout.write(self.style.SUCCESS(f"Created default file: {filename}"))
                
            # Load the data from the file
            with open(file_path, 'r', encoding='utf-8') as f:
                result[filename.split('.')[0]] = json.load(f)
                
        return result

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        clear_existing = kwargs['clear']
        username = kwargs.get('username')
        
        if not username:
            self.stdout.write(self.style.ERROR('Username parameter is required. Use --username=USERNAME'))
            return
            
        # Find target user
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"Creating babies for user: {user.username}")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with username "{username}" not found.'))
            return
        
        # Clear existing records if requested (only for the target user)
        if clear_existing:
            if input(f"Are you sure you want to delete all existing child records for {user.username}? (y/n): ").lower() == 'y':
                count_deleted = YourChild_Model.objects.filter(user=user).delete()[0]
                self.stdout.write(self.style.SUCCESS(f'Deleted {count_deleted} existing child records for {user.username}'))
        
        try:
            data = self.setup_json_files()
            boy_names = data.get('boy_names', [])
            girl_names = data.get('girl_names', [])
            last_names = data.get('last_names', [])
            descriptions = data.get('descriptions', [])
            
            if not (boy_names and girl_names and last_names and descriptions):
                self.stdout.write(self.style.ERROR("One or more required data files are empty. Check JSON files."))
                return
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading/creating data files: {str(e)}"))
            return
        
        babies_created = 0
        retries = 0
        max_retries = count * 5  # Increased retry limit
        existing_names = set(YourChild_Model.objects.filter(user=user).values_list('name', flat=True))
        
        try:
            while babies_created < count and retries < max_retries:
                gender = random.choice(['male', 'female'])
                if gender == 'male':
                    first_name = random.choice(boy_names)
                else:
                    first_name = random.choice(girl_names)
                
                last_name = random.choice(last_names)
                
                # Create unique name (always add a timestamp or random suffix to ensure uniqueness)
                timestamp = int(datetime.now().timestamp()) % 10000  # Last 4 digits of timestamp
                unique_suffix = f" {timestamp + random.randint(1, 999)}"
                
                full_name = f"{first_name}{unique_suffix}"
                
                # Skip if name already exists
                if full_name in existing_names:
                    retries += 1
                    continue
                
                # Generate random age between 0-36 months
                age_months = random.randint(0, 36)
                birth_date = timezone.now() - timedelta(days=age_months*30)
                
                # Generate random weight and height appropriate for age
                base_weight = 3.5  # average birth weight in kg
                base_height = 50   # average birth height in cm
                
                # Simplified growth model (not medically accurate)
                weight = round(base_weight + (age_months * 0.5 * random.uniform(0.8, 1.2)), 2)  # ~0.5kg per month
                height = round(base_height + (age_months * 2 * random.uniform(0.9, 1.1)), 1)    # ~2cm per month
                
                try:
                    child = YourChild_Model.objects.create(
                        name=full_name,
                        second_name=last_name,
                        birth_date=birth_date,
                        age=age_months,
                        gender=gender,
                        user=user,  # Always use the specified user
                        weight=weight,
                        height=height,
                        desc=random.choice(descriptions),
                        # image_url is left empty
                    )
                    
                    existing_names.add(full_name)
                    babies_created += 1
                    self.stdout.write(f"Created child {babies_created}/{count}: {full_name} {last_name}")
                    
                except IntegrityError:
                    retries += 1
                    continue  # Try again with a different name
            
            if babies_created < count:
                self.stdout.write(self.style.WARNING(
                    f'Created {babies_created} of {count} requested babies. '
                    f'Could not create more due to name uniqueness constraints.'
                ))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully created {babies_created} baby records for {user.username}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))