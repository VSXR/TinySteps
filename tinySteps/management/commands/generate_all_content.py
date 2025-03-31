from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Automatically generates all content (users, children, forum posts, guides)'

    def add_arguments(self, parser):
        parser.add_argument('--children', type=int, default=20, help='Number of children to generate per user')
        parser.add_argument('--posts', type=int, default=30, help='Number of posts to generate for the forum')
        parser.add_argument('--parent_guides', type=int, default=15, help='Number of parent guides to generate')
        parser.add_argument('--nutrition_guides', type=int, default=15, help='Number of nutrition guides to generate')
        parser.add_argument('--comments', type=int, default=50, help='Number of comments to generate')
        parser.add_argument('--clear_all', action='store_true', help='Delete all existing content before creating new')
        parser.add_argument('--approved', action='store_true', help='Create guides as already approved')

    def handle(self, *args, **options):
        children_count = options['children']
        posts_count = options['posts']
        parent_guides_count = options['parent_guides']
        nutrition_guides_count = options['nutrition_guides']
        comments_count = options['comments']
        clear_all = options['clear_all']
        approved = options['approved']
        
        self.stdout.write(self.style.SUCCESS('=== CONTENT GENERATION START ==='))
        
        # 1. Generate children profiles
        self.stdout.write(self.style.NOTICE('\n[1/5] Generating children profiles...'))
        call_command('generate_children', count=children_count, clear=clear_all)
        
        # 2. Generate forum posts
        self.stdout.write(self.style.NOTICE('\n[2/5] Generating forum posts...'))
        call_command('generate_forum_posts', count=posts_count, clear=clear_all)
        
        # 3. Generate nutrition guides
        self.stdout.write(self.style.NOTICE('\n[3/5] Generating nutrition guides...'))
        call_command('generate_nutrition_guides', count=nutrition_guides_count, clear=clear_all, approved=approved)
        
        # 4. Generate parent guides
        self.stdout.write(self.style.NOTICE('\n[4/5] Generating parent guides...'))
        call_command('generate_parent_guides', count=parent_guides_count, clear=clear_all, approved=approved)
        
        # 5. Generate comments
        self.stdout.write(self.style.NOTICE('\n[5/5] Generating comments...'))
        call_command('generate_comments', count=comments_count, clear=clear_all)
        
        self.stdout.write(self.style.SUCCESS('\n=== CONTENT GENERATION COMPLETED ==='))
        self.stdout.write(self.style.SUCCESS(f'- {children_count} children profiles'))
        self.stdout.write(self.style.SUCCESS(f'- {posts_count} forum posts'))
        self.stdout.write(self.style.SUCCESS(f'- {nutrition_guides_count} nutrition guides'))
        self.stdout.write(self.style.SUCCESS(f'- {parent_guides_count} parent guides'))
        self.stdout.write(self.style.SUCCESS(f'- {comments_count} comments on posts and guides'))