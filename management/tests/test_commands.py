"""
Tests for TinySteps management commands
"""
import os
import json
import shutil
import tempfile
import unittest
import importlib
from unittest import mock
from io import StringIO
from pathlib import Path

from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

try:
    from tinySteps.models import (
        ExternalArticle_Model, 
        ParentsForum_Model, 
        Comment_Model, 
        Guides_Model
    )
    MODELS_IMPORTED = True
except ImportError:
    MODELS_IMPORTED = False

class CommandTestCase(TestCase):
    """Base test case for management commands with utility methods"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Mock settings to use test directory
        self.settings_patcher = mock.patch('management.config.settings.settings')
        self.mock_settings = self.settings_patcher.start()
        
        # Configure mock settings to return our test paths
        def mock_get(key, default=None):
            if key.startswith('paths.'):
                path_type = key.split('.')[-1]
                return os.path.join(self.test_dir, path_type)
            return default
        
        self.mock_settings.get.side_effect = mock_get
        
        # Create test data directories
        os.makedirs(os.path.join(self.test_dir, 'babies'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'forum'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'guides'), exist_ok=True)
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password'
        )
    
    def tearDown(self):
        """Clean up after tests"""
        # Stop patchers
        self.settings_patcher.stop()
        
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def call_command(self, command, *args, **kwargs):
        """Call a custom management command directly (not through Django)"""
        out = StringIO()
        err = StringIO()
        
        try:
            # We import the command module directly
            if '.' in command:
                category, name = command.split('.')
                module_path = f"management.commands.{category}.{name}"
            else:
                module_path = f"management.commands.{command}"
                
            module = importlib.import_module(module_path)
            
            # Create command instance
            cmd = module.Command()
            cmd.stdout = out
            cmd.stderr = err
            
            # Call the handle method directly
            cmd.handle(*args, **kwargs)
            
            return out.getvalue(), err.getvalue()
            
        except ImportError as e:
            err.write(f"Command not found: {command}\n")
            err.write(str(e))
            return out.getvalue(), err.getvalue()
        except Exception as e:
            err.write(f"Error executing command: {str(e)}")
            return out.getvalue(), err.getvalue()
    
    
    def create_test_json(self, path, data):
        """Create a test JSON file"""
        full_path = os.path.join(self.test_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        return full_path

class ContentCommandsTest(CommandTestCase):
    """Tests for content generation commands"""
    
    @mock.patch('management.commands.content.generate_babies_list.setup_json_directory')
    def test_generate_babies_list(self, mock_setup):
        """Test generate_babies_list command"""
        # Setup test data
        mock_data = {
            'boy_names': ['John', 'James'],
            'girl_names': ['Emma', 'Olivia'],
            'last_names': ['Smith', 'Johnson'],
            'descriptions': ['Happy baby', 'Calm baby']
        }
        mock_setup.return_value = mock_data
        
        # Create a test output file path
        output_file = os.path.join(self.test_dir, 'babies', 'generated_babies.json')
        
        # Run the command
        out, err = self.call_command(
            'generate_babies_list',
            count=2,
            username='testuser'
        )
        
        # Check the output
        self.assertIn('Successfully generated 2 new babies', out)
        
        # Verify the JSON file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Check the content
        with open(output_file, 'r', encoding='utf-8') as f:
            babies = json.load(f)
            self.assertEqual(len(babies), 2)
            for baby in babies:
                self.assertEqual(baby['user'], 'testuser')
                self.assertIn(baby['gender'], ['male', 'female'])
                if baby['gender'] == 'male':
                    self.assertIn(baby['name'], ['John', 'James'])
                else:
                    self.assertIn(baby['name'], ['Emma', 'Olivia'])
    
    @unittest.skipIf(not MODELS_IMPORTED, "Django models not available")
    @mock.patch('management.commands.content.generate_forum_discussions.load_json_data')
    def test_generate_forum_discussions(self, mock_load_json):
        """Test generate_forum_discussions command"""
        # Setup mock data
        mock_load_json.side_effect = lambda path, default=None: {
            os.path.join(self.test_dir, 'forum', 'topics.json'): [
                {"title": "Test Topic", "desc": "Test Description", "category": "test"}
            ],
            os.path.join(self.test_dir, 'forum', 'comments.json'): {
                "test": ["Test comment 1", "Test comment 2"],
                "default": ["Default comment"]
            }
        }.get(path, default or {})
        
        # Run the command
        out, err = self.call_command(
            'generate_forum_discussions',
            count=1,
            comments=2
        )
        
        # Check the output
        self.assertIn('Successfully created', out)
        
        # Verify the database records
        self.assertEqual(ParentsForum_Model.objects.count(), 1)
        forum_post = ParentsForum_Model.objects.first()
        self.assertEqual(forum_post.title, "Test Topic")
        
        # Check comments
        ct = ContentType.objects.get_for_model(ParentsForum_Model)
        comments = Comment_Model.objects.filter(
            content_type=ct,
            object_id=forum_post.id
        )
        self.assertLessEqual(len(comments), 2)
    
    @unittest.skipIf(not MODELS_IMPORTED, "Django models not available")
    @mock.patch('management.commands.content.generate_guides_discussions.load_json_data')
    def test_generate_guides_discussions(self, mock_load_json):
        """Test generate_guides_discussions command"""
        guide = Guides_Model.objects.create(
            title="Test Guide",
            desc="Test Content",
            guide_type="parent"
        )
        
        # Setup mock data
        mock_load_json.return_value = {
            "positive": ["Great guide!"],
            "neutral": ["OK guide."],
            "negative": ["Could be better."]
        }
        
        # Run the command
        out, err = self.call_command(
            'generate_guides_discussions',
            max_comments=2,
            guide_type='parent'
        )
        
        # Check the output
        self.assertIn('Successfully added', out)
        
        # Verify the comments
        ct = ContentType.objects.get_for_model(Guides_Model)
        comments = Comment_Model.objects.filter(
            content_type=ct,
            object_id=guide.id
        )
        self.assertLessEqual(len(comments), 2)
    
    @unittest.skipIf(not MODELS_IMPORTED, "Django models not available")
    @mock.patch('tinySteps.services.apis.NewsAPI_Service.get_parenting_articles')
    @mock.patch('tinySteps.services.apis.CurrentsAPI_Service')
    def test_refresh_articles(self, mock_currents, mock_news):
        """Test refresh_articles command"""
        # Setup mock data
        mock_news.return_value = {
            "articles": [
                {
                    "title": "Test Article",
                    "description": "Test Description",
                    "url": "https://example.com/article1",
                    "urlToImage": "https://example.com/image1.jpg",
                    "publishedAt": timezone.now().isoformat(),
                    "source": {"name": "Test Source"}
                }
            ]
        }
        
        mock_currents.return_value = {
            "news": [
                {
                    "title": "Test News",
                    "description": "Test News Description",
                    "url": "https://example.com/news1",
                    "image": "https://example.com/news_image1.jpg",
                    "published": timezone.now().isoformat(),
                    "source": {"name": "Test News Source"}
                }
            ]
        }
        
        # Run the command
        out, err = self.call_command(
            'refresh_articles',
            limit=5,
            force=True
        )
        
        # Check the output
        self.assertIn('Successfully updated', out)
        
        # Verify the database records
        self.assertEqual(ExternalArticle_Model.objects.count(), 2)

class NotificationCommandsTest(CommandTestCase):
    """Tests for notification commands"""
    
    @mock.patch('tinySteps.utils.create_event_reminders')
    def test_send_reminders(self, mock_create_reminders):
        """Test send_reminders command"""
        # Setup the mock
        mock_create_reminders.return_value = 5
        
        # Run the command
        out, err = self.call_command(
            'send_reminders',
            days=2
        )
        
        # Check the output
        self.assertIn('Successfully created 5 event reminders', out)
        
        # Verify the mock was called correctly
        mock_create_reminders.assert_called_once_with(
            days_in_advance=2,
            dry_run=False
        )
    
    @mock.patch('tinySteps.utils.create_event_reminders')
    def test_send_reminders_dry_run(self, mock_create_reminders):
        """Test send_reminders command with dry run"""
        # Setup the mock
        mock_create_reminders.return_value = 3
        
        # Run the command
        out, err = self.call_command(
            'send_reminders',
            days=1,
            dry_run=True
        )
        
        # Check the output
        self.assertIn('Dry run complete. 3 reminders would be created', out)
        
        # Verify the mock was called correctly
        mock_create_reminders.assert_called_once_with(
            days_in_advance=1,
            dry_run=True
        )

class TranslationCommandsTest(CommandTestCase):
    """Tests for translation commands"""
    
    @mock.patch('subprocess.run')
    def test_init_translations(self, mock_run):
        """Test init_translations command"""
        # Setup the mock
        mock_process = mock.MagicMock()
        mock_process.stdout = "Created translations"
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Run the command
        out, err = self.call_command(
            'init_translations',
            locales=['es', 'fr']
        )
        
        # Check the output
        self.assertIn('Translation initialization completed', out)
        
        # Verify the subprocess call
        self.assertEqual(mock_run.call_count, 3)  # 1 call per locale + compilemessages
    
    @mock.patch('polib.pofile')
    def test_auto_translate(self, mock_pofile):
        """Test auto_translate command"""
        # Setup mocks
        mock_po = mock.MagicMock()
        mock_po.__iter__.return_value = []
        mock_pofile.return_value = mock_po
        
        with mock.patch('googletrans.Translator.translate') as mock_translate:
            # Set up translate mock
            mock_translate.return_value = [
                mock.MagicMock(text="Translated text")
            ]
            
            # Run the command
            out, err = self.call_command(
                'auto_translate',
                locale='es',
                source='en',
                dry_run=True
            )
            
            # Check output (simply checking it runs, since we mocked empty PO files)
            self.assertIn('DRY RUN', out)
    
    @mock.patch('polib.pofile')
    def test_translation_workflow_status(self, mock_pofile):
        """Test translation_workflow status command"""
        # Setup mocks
        mock_po = mock.MagicMock()
        mock_po.__iter__.return_value = []
        mock_po.__len__.return_value = 10
        
        def mock_filtered_entries(filter_func):
            if filter_func == mock_po.translated:
                return [1, 2, 3, 4, 5]  # 5 translated entries
            return []
            
        mock_po.filter = mock_filtered_entries
        mock_pofile.return_value = mock_po
        
        # Run the command
        out, err = self.call_command(
            'translation_workflow',
            'status',
            locales=['es']
        )
        
        # Check output
        self.assertIn('Translation status', out)

class CommandRunnerTest(TestCase):
    """Tests for the main run_command functionality"""
    
    def test_list_available_commands(self):
        """Test listing available commands"""
        # Import the function directly instead of using call_command
        from management.run_command import list_available_commands
        
        # Mock the directory structure
        with mock.patch('pathlib.Path.exists', return_value=True), \
             mock.patch('pathlib.Path.glob', return_value=[
                 mock.MagicMock(stem='generate_babies_list'),
                 mock.MagicMock(stem='generate_forum_discussions')
             ]):
            
            # Call the function directly
            commands = list_available_commands()
            
            # Check output
            self.assertIn('content.generate_babies_list', commands)
            self.assertIn('content.generate_forum_discussions', commands)
    
    def test_command_not_found(self):
        """Test handling non-existent command"""
        # Import the function directly
        from management.run_command import run_command
        
        # Run the command directly
        out = StringIO()
        err = StringIO()
        
        with mock.patch('management.run_command.get_command_module', return_value=None):
            result = run_command('non_existent_command', stdout=out, stderr=err)
            
            # Check output
            self.assertIn('Command not found', err.getvalue())
            self.assertFalse(result)  # Should return False for failure

if __name__ == '__main__':
    import unittest
    unittest.main()