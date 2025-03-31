from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from tinySteps.models import YourChild_Model, ParentsForum_Model, Guides_Model, Category_Model

class CommandsTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a test category
        self.category = Category_Model.objects.create(
            name="Test Category",
            description="Test category description"
        )

    def test_generate_children_command(self):
        """Test that the generate_children command creates child profiles"""
        out = StringIO()
        # Test with small count to keep tests fast
        call_command('generate_children', count=2, username='testuser', stdout=out)
        
        # Check output
        self.assertIn('Created', out.getvalue())
        
        # Check database
        children_count = YourChild_Model.objects.filter(user=self.user).count()
        self.assertEqual(children_count, 2)

    def test_generate_forum_posts_command(self):
        """Test that the generate_forum_posts command creates forum posts"""
        out = StringIO()
        # Test with small count to keep tests fast
        call_command('generate_forum_posts', count=3, stdout=out)
        
        # Check output
        self.assertIn('Created', out.getvalue())
        
        # Check database
        posts_count = ParentsForum_Model.objects.count()
        self.assertEqual(posts_count, 3)

    def test_generate_parent_guides_command(self):
        """Test that the generate_parent_guides command creates parent guides"""
        out = StringIO()
        # Test with small count to keep tests fast
        call_command('generate_parent_guides', count=2, approved=True, stdout=out)
        
        # Check output
        self.assertIn('Created', out.getvalue())
        
        # Check database
        guides_count = Guides_Model.objects.filter(guide_type='parent', status='approved').count()
        self.assertEqual(guides_count, 2)

    def test_generate_nutrition_guides_command(self):
        """Test that the generate_nutrition_guides command creates nutrition guides"""
        out = StringIO()
        # Test with small count to keep tests fast
        call_command('generate_nutrition_guides', count=2, approved=True, stdout=out)
        
        # Check output
        self.assertIn('Created', out.getvalue())
        
        # Check database
        guides_count = Guides_Model.objects.filter(guide_type='nutrition', status='approved').count()
        self.assertEqual(guides_count, 2)

    def test_generate_all_content_command(self):
        """Test that the generate_all_content command calls all generators"""
        out = StringIO()
        # Test with minimal counts to keep tests fast
        call_command('generate_all_content', 
                    children=1, 
                    posts=1, 
                    parent_guides=1, 
                    nutrition_guides=1, 
                    approved=True, 
                    stdout=out)
        
        # Check output
        self.assertIn('CONTENT GENERATION COMPLETED', out.getvalue())
        
        # Check database counts
        children_count = YourChild_Model.objects.count()
        posts_count = ParentsForum_Model.objects.count()
        parent_guides_count = Guides_Model.objects.filter(guide_type='parent').count()
        nutrition_guides_count = Guides_Model.objects.filter(guide_type='nutrition').count()
        
        self.assertGreaterEqual(children_count, 1)
        self.assertGreaterEqual(posts_count, 1)
        self.assertGreaterEqual(parent_guides_count, 1)
        self.assertGreaterEqual(nutrition_guides_count, 1)