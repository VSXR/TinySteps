from django.core.management.base import BaseCommand
from django.utils.text import slugify
from tinySteps.models import Guides_Model, Category_Model
from django.contrib.auth.models import User
import random
import uuid

class Command(BaseCommand):
    help = 'Generates sample parent guides'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of parent guides to create')
        parser.add_argument('--clear', action='store_true', help='Clear existing guides before creating new ones')
        parser.add_argument('--approved', action='store_true', help='Create guides as already approved')

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        approved = options['approved']
        
        # Get a staff user for the guides
        staff_users = User.objects.filter(is_staff=True)
        if not staff_users.exists():
            self.stdout.write(self.style.ERROR('No staff users found. Please create a staff user first.'))
            return
        
        # Check if we have categories
        # Note: We're getting all categories since there's no 'type' field
        categories = list(Category_Model.objects.all())
        if not categories:
            self.stdout.write(self.style.WARNING('No categories defined. Creating default category.'))
            category = Category_Model.objects.create(
                name='General Parenting',
                description='General parenting topics'
            )
            categories = [category]
        
        if clear:
            Guides_Model.objects.filter(guide_type='parent').delete()
            self.stdout.write(self.style.SUCCESS('All parent guides have been deleted'))
        
        created_count = 0
        topics = [
            'positive discipline',
            'effective communication with children',
            'managing child anxiety',
            'child socialization',
            'language development'
        ]
        
        # Various prefixes to create diverse titles
        prefixes = [
            'How to handle',
            'Understanding',
            'Keys to',
            'All about',
            'Solutions for',
            'Strategies for',
            'Complete guide to',
            'Introduction to'
        ]
        
        for _ in range(count):
            try:
                author = random.choice(staff_users)
                category = random.choice(categories)
                
                # Create a unique title and slug
                topic = random.choice(topics)
                prefix = random.choice(prefixes)
                title = f"{prefix} {topic}"
                
                # Create a unique slug to avoid UNIQUE constraint errors
                unique_id = uuid.uuid4().hex[:6]
                slug = f"{slugify(title)}-{unique_id}"
                
                # Generate content
                content = f"""
# {title}

## Introduction
This is a guide about {topic}. Here you'll find valuable information and practical advice.

## Main points
1. Understanding the basics of {topic}
2. How to apply the principles of {topic} in everyday situations
3. Common challenges and solutions related to {topic}

## Practical advice
When dealing with {topic}, remember these key points:
- Consistency is essential
- Communication is the foundation
- Every child is unique
- Patience leads to progress
                """
                
                guide = Guides_Model.objects.create(
                    title=title,
                    slug=slug,
                    desc=content,
                    author=author,
                    category=category,
                    status='approved' if approved else 'pending',
                    guide_type='parent' 
                )
                
                status = "(approved)" if approved else "(pending approval)"
                self.stdout.write(self.style.SUCCESS(f'Created parent guide: {guide.title} {status}'))
                created_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating parent guide: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} parent guides have been created'))