import random
import json
import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from tinySteps.models import ParentsForum_Model, Comment_Model

class Command(BaseCommand):
    help = 'Generate random discussions for the Parents Forum on baby care topics'

    def add_arguments(self, parser):
        default_count = random.randint(10, 30)
        default_comments = random.randint(3, 10)
        
        parser.add_argument(
            '--count',
            type=int,
            default=default_count,
            help=f'Number of forum posts to create (random default: {default_count})'
        )
        
        parser.add_argument(
            '--comments',
            type=int,
            default=default_comments,
            help=f'Maximum number of comments per post (random default: {default_comments})'
        )

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        max_comments = kwargs['comments']
        
        # Check if we have users in the system and then load JSON data
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found in the database. Please create some users first.'))
            return
        
        try:
            json_dir = os.path.join('tinySteps', 'management', 'commands', 'tinySteps_jsons', 'parents_forum')
            topics_file = os.path.join(json_dir, 'topics.json')
            comments_file = os.path.join(json_dir, 'comments.json')
            
            if not os.path.exists(json_dir):
                self.stdout.write(self.style.ERROR(f"Directory not found: {json_dir}"))
                return
                
            if not os.path.exists(topics_file):
                self.stdout.write(self.style.ERROR(f"File not found: {topics_file}"))
                return
                
            if not os.path.exists(comments_file):
                self.stdout.write(self.style.ERROR(f"File not found: {comments_file}"))
                return
            
            # Load the JSON data
            with open(topics_file, 'r', encoding='utf-8') as f:
                baby_care_topics = json.load(f)
                
            with open(comments_file, 'r', encoding='utf-8') as f:
                comments_data = json.load(f)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading JSON data: {str(e)}"))
            return

        # Create forum posts with different dates
        created_count = 0
        try:
            # Clear existing posts if requested count matches total topics
            if count >= len(baby_care_topics):
                if input("Do you want to clear existing forum posts first? (y/n): ").lower() == 'y':
                    ParentsForum_Model.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS('All existing forum posts cleared'))
            
            for i in range(min(count, len(baby_care_topics))):
                topic = baby_care_topics[i]
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
                
                created_count += 1
                
            self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} forum posts with comments'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
    
    def generate_comment_for_topic(self, category, comments_data):
        """Generate relevant comments based on the topic category
        If the category is not found, a default comment is returned"""
        if category in comments_data:
            comment_list = comments_data[category] + comments_data['default']
        else:
            comment_list = comments_data['default']
            
        return random.choice(comment_list)