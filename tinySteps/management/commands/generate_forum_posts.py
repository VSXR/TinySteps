import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from tinySteps.models import ParentsForum_Model

class Command(BaseCommand):
    help = 'Generates random posts for the parents forum'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of posts to generate')
        parser.add_argument('--clear', action='store_true', help='Delete existing posts before creating new ones')

    def handle(self, *args, **options):
        count = options['count']
        clear = options.get('clear', False)
        
        # Verify that there are users in the system
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('There are no users in the database. Create some first.'))
            return
        
        # Delete existing posts if requested
        if clear:
            confirm = input("Are you sure you want to delete ALL forum posts? (y/n): ").lower()
            if confirm == 'y':
                ParentsForum_Model.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('All existing posts have been deleted'))
            else:
                self.stdout.write(self.style.WARNING('Operation canceled by user'))

        # Available categories for posts
        categories = [choice[0] for choice in ParentsForum_Model.CATEGORY_CHOICES]
        
        # Common topics for titles
        topics = [
            "Tips for", "Problems with", "Help with", "Experience with", 
            "Questions about", "How to handle?", "Information about", "My experience with",
            "Need help with", "Recommendations for"
        ]
        
        # Specific topics by category
        subjects = {
            'advice': ["new parents", "routines", "baby sleep", "early stimulation"],
            'feeding': ["breastfeeding", "introducing solids", "food allergies", "food rejection"],
            'sleep': ["sleep patterns", "sleep training", "co-sleeping", "night waking"],
            'health': ["vaccines", "fever", "teething", "common colds"],
            'development': ["developmental milestones", "language delay", "fine motor skills", "socialization"],
            'care': ["diaper changing", "baby bathing", "diaper rash", "skin care"]
        }
        
        # Generic descriptions
        descriptions = [
            "Hello everyone, I wanted to share my experience with {} and see if anyone else has gone through this.",
            "I'm having difficulties with {} and would like to know how you handled it.",
            "Does anyone have advice on {}? I really need help with this.",
            "My baby is experiencing {} and I don't know what to do. Any suggestions?",
            "Is it normal for my child to have problems with {}? How did you solve it?",
            "I'm concerned about {} and looking for advice from parents who have gone through this before.",
            "What has been your experience with {}? I'm considering options and need opinions."
        ]
        
        # Create random posts
        created_count = 0
        now = timezone.now()
        
        for i in range(count):
            try:
                # Choose a random category and topic
                category = random.choice(categories)
                
                # Choose a specific subject for the category
                subject = random.choice(subjects.get(category, ["parenting"]))
                
                # Build the title
                title = f"{random.choice(topics)} {subject}"
                if len(title) > 100:
                    title = title[:97] + "..."
                
                # Build the description
                desc = random.choice(descriptions).format(subject)
                
                # Add more details to the description to make it longer
                additional_text = " I'd like to know what other parents think about this and what solutions have worked for you. All suggestions are welcome. Thank you in advance for your help and support in this community."
                desc += additional_text
                
                # Choose a random user and publication date
                author = random.choice(users)
                days_ago = random.randint(0, 90)  # Post created between today and 90 days ago
                created_at = now - timedelta(days=days_ago, 
                                           hours=random.randint(0, 23),
                                           minutes=random.randint(0, 59))
                
                # Create the post
                post = ParentsForum_Model.objects.create(
                    title=title,
                    desc=desc,
                    category=category,
                    author=author,
                )
                # Update creation date
                post.created_at = created_at
                post.save(update_fields=['created_at'])
                
                created_count += 1
                self.stdout.write(f"Created post: {title}")
                
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error creating post: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'{created_count} new posts have been created in the forum'))