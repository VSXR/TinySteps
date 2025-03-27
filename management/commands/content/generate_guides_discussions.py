"""
Command to generate discussion comments for guides in TinySteps
"""
import os
import json
import random
import argparse
import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from management.config.settings import settings
from management.commands.utils.data_helpers import load_json_data, get_json_directory

logger = logging.getLogger(__name__)

try:
    from tinySteps.models import Comment_Model, Guides_Model
    MODELS_IMPORTED = True
except ImportError:
    logger.warning("Could not import TinySteps models. This script requires Django.")
    MODELS_IMPORTED = False

class Command(BaseCommand):
    help = 'Generate random comments for existing guides using data from JSON files'

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
        
        parser.add_argument(
            '--guide_type',
            choices=['parent', 'nutrition', 'all'],
            default='all',
            help='Type of guides to process: parent, nutrition, or all (default)'
        )
        
    def handle(self, *args, **kwargs):
        if not MODELS_IMPORTED:
            self.stdout.write(self.style.ERROR('Could not import required models. Check Django installation.'))
            return
            
        max_comments = kwargs['max_comments']
        add_to_all = kwargs['all']
        guide_type = kwargs['guide_type']
        
        # Check if we have users in the system
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found in the database. Please create some users first.'))
            return
        
        # Get guides from the database
        try:
            if guide_type == 'all' or guide_type == 'parent':
                parent_guides = list(Guides_Model.objects.filter(guide_type='parent'))
            else:
                parent_guides = []
                
            if guide_type == 'all' or guide_type == 'nutrition':
                nutrition_guides = list(Guides_Model.objects.filter(guide_type='nutrition'))
            else:
                nutrition_guides = []
            
            if not parent_guides and not nutrition_guides:
                self.stdout.write(self.style.ERROR('No guides found in the database. Please create some guides first.'))
                return
                
            self.stdout.write(self.style.SUCCESS(f'Found {len(parent_guides)} parent guides and {len(nutrition_guides)} nutrition guides'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting guides: {str(e)}'))
            return
        
        # Load JSON comments data
        try:
            guides_dir = get_json_directory('guides')
            comments_file = os.path.join(guides_dir, 'comments.json')
            
            comments_data = load_json_data(comments_file)
            if not comments_data:
                self.stdout.write(self.style.ERROR(
                    f"No comments data found in {comments_file}\n"
                    f"Please ensure this file exists with appropriate comment data."
                ))
                return
                
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
        if parent_guides:
            guides_updated, comments_added = self.process_guides(
                parent_guides, guide_ct, users, max_comments, 
                add_to_all, comments_data, guides_updated, comments_added
            )
        
        # Process nutrition guides
        if nutrition_guides:
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
        # Define categories and their weights
        categories = list(comments_data.keys())
        
        if not categories:
            return "Great guide, thanks for sharing this information!"
            
        # Default weights give higher probability to positive comments
        weights = {}
        for category in categories:
            if category.lower() == 'positive':
                weights[category] = 0.6
            elif category.lower() == 'neutral':
                weights[category] = 0.3
            elif category.lower() == 'negative':
                weights[category] = 0.1
            else:
                # For unknown categories, assign a default weight
                weights[category] = 0.2
                
        # Normalize weights
        total = sum(weights.values())
        for category in weights:
            weights[category] /= total
            
        # Select a category based on weights
        rand_val = random.random()
        cumulative = 0
        selected_category = categories[0]  # Default
        
        for category, weight in weights.items():
            cumulative += weight
            if rand_val <= cumulative:
                selected_category = category
                break
                
        # Select a random comment from the chosen category
        if selected_category in comments_data and comments_data[selected_category]:
            return random.choice(comments_data[selected_category])
        
        # Fallback to a default comment
        return "Thanks for sharing this useful guide!"

def main(args=None):
    """Run the command with the given arguments."""
    parser = argparse.ArgumentParser(description='Generate guide discussions for TinySteps')
    
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
    parser.add_argument(
        '--guide_type',
        choices=['parent', 'nutrition', 'all'],
        default='all',
        help='Type of guides to process: parent, nutrition, or all (default)'
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
        call_command('generate_guides_discussions', 
                    max_comments=parsed_args.max_comments,
                    all=parsed_args.all,
                    guide_type=parsed_args.guide_type)
    except ImportError:
        logger.error("This command requires Django to be available.")
        return 1

if __name__ == '__main__':
    main()