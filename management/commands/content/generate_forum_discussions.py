"""
Command to generate forum discussions for TinySteps
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
from management.config.settings import settings
from management.commands.utils.data_helpers import load_json_data, get_json_directory

logger = logging.getLogger(__name__)

try:
    from tinySteps.models import ParentsForum_Model, Comment_Model
except ImportError:
    logger.warning("Could not import TinySteps models. This script requires Django.")

class Command(BaseCommand):
    help = 'Generate random discussions for the Parents Forum on baby care topics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=settings.get('content_generation.default_forum_count', 5),
            help='Number of forum discussions to generate'
        )
        
        parser.add_argument(
            '--comments',
            type=int,
            default=settings.get('content_generation.default_comment_count', 5),
            help='Maximum number of comments per discussion'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing forum discussions before generating new ones'
        )
        
    def handle(self, *args, **options):
        count = options['count']
        max_comments = options['comments']
        clear = options.get('clear', False)
        
        # Check if we have users in the system
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found in the database. Please create some users first.'))
            return
        
        # Load JSON data
        try:
            forum_dir = get_json_directory('forum')
            topics_file = os.path.join(forum_dir, 'topics.json')
            comments_file = os.path.join(forum_dir, 'comments.json')
            
            # Load topics
            topics_data = load_json_data(topics_file)
            if not topics_data:
                self.stdout.write(self.style.ERROR(f"No topics found in {topics_file}"))
                return
            
            baby_care_topics = topics_data
            
            # Load comments
            comments_data = load_json_data(comments_file)
            if not comments_data:
                self.stdout.write(self.style.ERROR(f"No comments found in {comments_file}"))
                return
                
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded {len(baby_care_topics)} topics and {sum(len(comments) for comments in comments_data.values())} comments"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading JSON data: {str(e)}"))
            return

        # Clear existing posts if requested
        if clear:
            confirm = input("Are you sure you want to delete all existing forum posts? (y/n): ").lower()
            if confirm == 'y':
                ParentsForum_Model.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('All existing forum posts cleared'))
            else:
                self.stdout.write(self.style.WARNING('Operation cancelled by user'))
                return

        # Create forum posts with different dates
        created_count = 0
        comments_count = 0
        
        try:
            # Limit to available topics
            topics_to_create = min(count, len(baby_care_topics))
            
            # Randomly select topics if count is less than total topics
            selected_topics = random.sample(baby_care_topics, topics_to_create)
            
            for topic in selected_topics:
                author = random.choice(users)
                
                # Create a post with a random date within the last 30 days
                random_days = random.randint(0, 30)
                post_date = timezone.now() - timedelta(days=random_days)
                
                post = ParentsForum_Model.objects.create(
                    title=topic['title'],
                    desc=topic['desc'],
                    author=author,
                )
                
                # Set the created_at field manually to distribute dates
                post.created_at = post_date
                post.save()
                
                # Add random number of comments
                comment_count = random.randint(0, max_comments)
                for _ in range(comment_count):
                    commenter = random.choice(users)
                    comment_days = random.randint(0, random_days)
                    comment_date = timezone.now() - timedelta(days=comment_days)
                    
                    # Generate a comment relevant to the topic
                    comment_text = self.generate_comment_for_topic(topic.get('category', 'default'), comments_data)
                    
                    comment = Comment_Model.objects.create(
                        content_object=post,
                        author=commenter,
                        text=comment_text
                    )
                    
                    # Set the created_at field for the comment
                    comment.created_at = comment_date
                    comment.save()
                    comments_count += 1
                
                created_count += 1
                
            self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} forum posts with {comments_count} comments'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
            
    def generate_comment_for_topic(self, category, comments_data):
        """Generate relevant comments based on the topic category
        If the category is not found, a default comment is returned"""
        if category in comments_data:
            comment_list = comments_data[category]
            if not comment_list and 'default' in comments_data:
                comment_list = comments_data['default']
        elif 'default' in comments_data:
            comment_list = comments_data['default']
        else:
            return "Interesting discussion, thanks for sharing!"
            
        return random.choice(comment_list)

def main(args=None):
    """Run the command with the given arguments."""
    parser = argparse.ArgumentParser(description='Generate forum discussions for TinySteps')
    parser.add_argument(
        '--count',
        type=int,
        default=settings.get('content_generation.default_forum_count', 5),
        help='Number of forum discussions to generate'
    )
    parser.add_argument(
        '--comments',
        type=int,
        default=settings.get('content_generation.default_comment_count', 5),
        help='Maximum number of comments per discussion'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing forum discussions before generating new ones'
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
        call_command('generate_forum_discussions', 
                    count=parsed_args.count,
                    comments=parsed_args.comments,
                    clear=parsed_args.clear)
    except ImportError:
        logger.error("This command requires Django to be available.")
        return 1

if __name__ == '__main__':
    main()