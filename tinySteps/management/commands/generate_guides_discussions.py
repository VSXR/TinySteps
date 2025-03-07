import random
import json
import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

try:
    from tinySteps.models import Comment_Model, Guides_Model
    USING_INHERITANCE = False
except ImportError:
    pass

class Command(BaseCommand):
    help = 'Generate random comments for existing guides using data from JSON files only'

    def add_arguments(self, parser):
        default_comments = random.randint(3, 10)
        
        parser.add_argument(
            '--max_comments',
            type=int,
            default=default_comments,
            help=f'Maximum number of comments per guide (random default: {default_comments})'
        )
        
        parser.add_argument(
            '--all',
            action='store_true',
            help='Add comments to all guides, even those that already have comments'
        )

    def handle(self, *args, **kwargs):
        max_comments = kwargs['max_comments']
        add_to_all = kwargs['all']
        
        # Check if we have users in the system
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found in the database. Please create some users first.'))
            return
        
        # Get guides from the database
        try:
            parent_guides = list(Guides_Model.objects.filter(guide_type='parent'))
            nutrition_guides = list(Guides_Model.objects.filter(guide_type='nutrition'))
            
            if not parent_guides and not nutrition_guides:
                self.stdout.write(self.style.ERROR('No guides found in the database. Please create some guides first.'))
                return
                
            self.stdout.write(self.style.SUCCESS(f'Found {len(parent_guides)} parent guides and {len(nutrition_guides)} nutrition guides'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting guides: {str(e)}'))
            return
        
        # Load JSON comments data - ONLY FROM JSON FILE
        try:
            json_dir = os.path.join('tinySteps', 'management', 'commands', 'tinySteps_jsons', 'guides')
            comments_file = os.path.join(json_dir, 'comments.json')
            
            if not os.path.exists(comments_file):
                self.stdout.write(self.style.ERROR(
                    f"Comments file not found: {comments_file}\n"
                    f"Please ensure this file exists with appropriate comment data."
                ))
                return
            
            with open(comments_file, 'r', encoding='utf-8') as f:
                comments_data = json.load(f)
                self.stdout.write(self.style.SUCCESS(f"Successfully loaded comments from {comments_file}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading JSON data: {str(e)}"))
            return
        
        # Get content type for the Guides model
        guide_ct = ContentType.objects.get_for_model(Guides_Model)
        
        # Create comments for each guide
        guides_updated = 0
        comments_added = 0
        
        # Process parent guides
        guides_updated, comments_added = self.process_guides(
            parent_guides, guide_ct, users, max_comments, 
            add_to_all, comments_data, guides_updated, comments_added
        )
        
        # Process nutrition guides
        guides_updated, comments_added = self.process_guides(
            nutrition_guides, guide_ct, users, max_comments, 
            add_to_all, comments_data, guides_updated, comments_added
        )
            
        self.stdout.write(self.style.SUCCESS(
            f'Successfully added {comments_added} comments to {guides_updated} guides'
        ))

    def process_guides(self, guides, content_type, users, max_comments, add_to_all, 
                      comments_data, guides_updated_count, comments_added_count):
        """Process a list of guides and add comments to them"""
        for guide in guides:
            # Skip guides that already have comments unless --all flag is used
            existing_comments = Comment_Model.objects.filter(
                content_type=content_type, 
                object_id=guide.id
            ).count()
            
            if existing_comments > 0 and not add_to_all:
                continue
                
            comment_count = random.randint(1, max_comments)
            for _ in range(comment_count):
                comment_text = self.select_weighted_comment(comments_data)
                author = random.choice(users)
                guide_created = guide.created_at if hasattr(guide, 'created_at') else timezone.now() - timedelta(days=90)
                earliest_date = max(guide_created, timezone.now() - timedelta(days=60))
                random_days = random.randint(0, max(0, (timezone.now() - earliest_date).days))
                comment_date = timezone.now() - timedelta(days=random_days)
                
                # Create the comment
                try:
                    comment = Comment_Model.objects.create(
                        content_type=content_type,
                        object_id=guide.id,
                        author=author,
                        text=comment_text
                    )
                    
                    # Set the created_at field manually
                    if hasattr(comment, 'created_at'):
                        comment.created_at = comment_date
                        comment.save()
                    
                    comments_added_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating comment: {str(e)}'))
            
            guides_updated_count += 1
            
        return guides_updated_count, comments_added_count

    def select_weighted_comment(self, comments_data):
        """Select a comment with weighted probabilities for different categories"""
        weights = {
            'positive': 25,
            'grateful': 20,
            'questions': 15, 
            'sharing_experience': 15,
            'suggestions': 10,
            'general': 15
        }
        
        available_categories = list(set(comments_data.keys()) & set(weights.keys()))
        if not available_categories:
            return random.choice([item for sublist in comments_data.values() for item in sublist])
            
        total = sum(weights[cat] for cat in available_categories)
        r = random.uniform(0, total)
        upto = 0
        
        for category in available_categories:
            if upto + weights[category] >= r:
                return random.choice(comments_data[category])
            upto += weights[category]
            
        return random.choice([item for sublist in comments_data.values() for item in sublist])