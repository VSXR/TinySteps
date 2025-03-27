"""
Command to generate random babies data for TinySteps
"""
import os
import json
import random
import argparse
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from management.config.settings import settings
from management.commands.utils.data_helpers import load_json_data, save_json_data, get_json_directory, setup_json_directory

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate random babies for the TinySteps app'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username', 
            type=str, 
            help='Username to assign babies to (defaults to random users)'
        )
        parser.add_argument(
            '--count', 
            type=int, 
            default=settings.get('content_generation.default_baby_count', 5),
            help='Number of babies to generate'
        )
        parser.add_argument(
            '--clear', 
            action='store_true',
            help='Clear existing babies data before generating new ones'
        )
    
    def setup_json_files(self):
        """Create and initialize JSON data files if they don't exist"""
        # Define default data for JSON files
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
        
        # Use the utility function to set up the directory and load data
        return setup_json_directory('babies', json_files)
    
    def handle(self, *args, **kwargs):
        username = kwargs.get('username')
        count = kwargs.get('count')
        clear = kwargs.get('clear')
        
        # Setup JSON data files
        data = self.setup_json_files()
        boy_names = data.get('boy_names', [])
        girl_names = data.get('girl_names', [])
        last_names = data.get('last_names', [])
        descriptions = data.get('descriptions', [])
        
        if not all([boy_names, girl_names, last_names, descriptions]):
            self.stderr.write(self.style.ERROR("Failed to load required JSON data files"))
            return
        
        # Get user if username provided, otherwise get all users
        users = []
        if username:
            try:
                user = User.objects.get(username=username)
                users = [user]
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"User '{username}' not found"))
                return
        else:
            users = list(User.objects.all())
            if not users:
                self.stderr.write(self.style.ERROR("No users found in the database. Please create some users first."))
                return
            
        # Get or create output file
        output_file = os.path.join(get_json_directory('babies'), 'generated_babies.json')
        
        # Load existing data or start with empty list
        babies = []
        if not clear and os.path.exists(output_file):
            try:
                babies = load_json_data(output_file, [])
                self.stdout.write(self.style.SUCCESS(f"Loaded {len(babies)} existing babies"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error loading existing babies: {str(e)}"))
        
        # Generate new babies
        new_babies = []
        now = timezone.now()
        
        for _ in range(count):
            gender = random.choice(['male', 'female'])
            first_name = random.choice(boy_names if gender == 'male' else girl_names)
            last_name = random.choice(last_names)
            
            # Generate random birth date within last 3 years
            days_ago = random.randint(0, 1095)  # Up to 3 years
            birth_date = (now - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            # Assign to random user if no specific username
            assigned_user = username or random.choice(users).username
            
            baby = {
                "name": first_name,
                "lastName": last_name,
                "gender": gender,
                "birthDate": birth_date,
                "description": random.choice(descriptions),
                "user": assigned_user
            }
            
            new_babies.append(baby)
        
        # Add new babies to existing list (if not clearing)
        if clear:
            babies = new_babies
        else:
            babies.extend(new_babies)
        
        # Save to JSON file
        if save_json_data(babies, output_file):
            self.stdout.write(self.style.SUCCESS(f"Successfully generated {count} new babies"))
            self.stdout.write(self.style.SUCCESS(f"Total babies: {len(babies)}"))
        else:
            self.stderr.write(self.style.ERROR("Failed to save generated babies"))

def main(args=None):
    """Run the command with the given arguments."""
    parser = argparse.ArgumentParser(description='Generate random babies for TinySteps')
    parser.add_argument(
        '--username', 
        type=str, 
        help='Username to assign babies to (defaults to random users)'
    )
    parser.add_argument(
        '--count', 
        type=int, 
        default=settings.get('content_generation.default_baby_count', 5),
        help='Number of babies to generate'
    )
    parser.add_argument(
        '--clear', 
        action='store_true',
        help='Clear existing babies data before generating new ones'
    )
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Try to import Django models and run as Django command
        from django.core.management import call_command
        call_command('generate_babies_list', 
                    username=parsed_args.username,
                    count=parsed_args.count,
                    clear=parsed_args.clear)
    except ImportError:
        logger.error("This command requires Django to be available.")
        return 1

if __name__ == '__main__':
    main()