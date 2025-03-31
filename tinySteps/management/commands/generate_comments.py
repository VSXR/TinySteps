from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tinySteps.models import Comment_Model, Guides_Model
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generates random comments for forum posts and guides'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50, help='Number of comments to create')
        parser.add_argument('--clear', action='store_true', help='Clear existing comments before creating new ones')

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        
        if clear:
            Comment_Model.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All comments have been deleted'))
        
        # Get active users for creating comments
        users = list(User.objects.filter(is_active=True))
        if not users:
            self.stdout.write(self.style.ERROR('No active users found. Please create users first.'))
            return
        
        # Get posts and guides to comment on
        posts = list(Guides_Model.objects.all())
        guides = list(Guides_Model.objects.filter(is_approved=True))
        
        if not posts and not guides:
            self.stdout.write(self.style.ERROR('No posts or guides found. Please create some first.'))
            return
        
        # Comment templates
        post_comments = [
            "Thanks for sharing this information!",
            "This is very helpful, I had the same issue with my child.",
            "I never thought about it this way, interesting perspective.",
            "I disagree with some points, but overall good advice.",
            "Has anyone else tried this approach?",
            "This worked for us, highly recommended!",
            "I'm going to try this with my child this weekend.",
            "Very thorough explanation, thank you!",
            "Could you provide more details about...?",
            "This is exactly what I was looking for."
        ]
        
        guide_comments = [
            "Excellent guide, very well written!",
            "This is a great resource for new parents.",
            "I've been using these tips for a while and they really work.",
            "Would love to see more guides like this one.",
            "Clear, concise, and practical - thank you!",
            "I've bookmarked this for future reference.",
            "Very comprehensive, covers all the important aspects.",
            "I appreciate the step-by-step approach.",
            "This should be required reading for all parents!",
            "I've shared this with my parenting group."
        ]
        
        # Create comments
        post_comment_count = 0
        guide_comment_count = 0
        
        for _ in range(count):
            try:
                # Decide whether to comment on a post or a guide
                if posts and (not guides or random.choice([True, False])):
                    # Comment on a post
                    post = random.choice(posts)
                    comment_text = random.choice(post_comments)
                    author = random.choice(users)
                    
                    # Check your Comment_Model fields and adjust accordingly
                    # If your model uses 'author' instead of 'user'
                    comment = Comment_Model(
                        author=author,  # Changed from 'user' to match your model
                        content=comment_text,
                        post=post,  # Make sure your model has a post field
                        created_at=timezone.now()
                    )
                    comment.save()
                    post_comment_count += 1
                    
                elif guides:
                    # Comment on a guide
                    guide = random.choice(guides)
                    comment_text = random.choice(guide_comments)
                    author = random.choice(users)
                    
                    comment = Comment_Model(
                        author=author, 
                        content=comment_text,
                        guide=guide, 
                        created_at=timezone.now()
                    )
                    comment.save()
                    guide_comment_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating comment: {str(e)}'))
        
        total = post_comment_count + guide_comment_count
        self.stdout.write(self.style.SUCCESS(f'{total} comments have been created:'))
        self.stdout.write(self.style.SUCCESS(f'- {post_comment_count} on forum posts'))
        self.stdout.write(self.style.SUCCESS(f'- {guide_comment_count} on guides'))