#!/usr/bin/env python
"""
Command runner for TinySteps management commands
"""
import os
import sys
import argparse
import importlib
import logging
from unittest import mock, TestCase
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'management.log'))
    ]
)
logger = logging.getLogger("command_runner")

class CommandRunnerTest(TestCase):
    """Tests for the main run_command functionality"""
    
    def test_list_available_commands(self):
        """Test listing available commands"""
        from management.run_command import list_available_commands

        # We mock the Path.glob method to return a list of files
        with mock.patch('pathlib.Path.exists', return_value=True), \
             mock.patch('pathlib.Path.glob', return_value=[
                 mock.MagicMock(name='generate_babies_list.py'),
                 mock.MagicMock(name='generate_forum_discussions.py')
             ]):
            
            commands = list_available_commands()
            self.assertIn('content.generate_babies_list', commands)
            self.assertIn('content.generate_forum_discussions', commands)
    
    def test_command_not_found(self):
        """Test handling non-existent command"""
        from management.run_command import get_command_module
        result = get_command_module('non_existent_command')
        self.assertIsNone(result)

def setup_django_env():
    """Setup Django environment"""
    # Add the parent directory to sys.path
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent
    
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    # Also add the management directory to sys.path
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    try:
        import django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tinySteps.settings")
        django.setup()
        logger.info("Django environment set up successfully")
        return True
    except ImportError:
        logger.warning("Django not found. Commands requiring Django may not work.")
        return False
    except Exception as e:
        logger.error(f"Error setting up Django environment: {e}")
        return False

def list_available_commands():
    """List all available commands"""
    commands = []
    
    # Path to command directories
    base_dir = Path(__file__).resolve().parent
    command_dirs = [
        base_dir / "commands",
        base_dir / "commands" / "content",
        base_dir / "commands" / "notifications",
        base_dir / "commands" / "translations"
    ]
    
    # Collect commands from all directories
    for dir_path in command_dirs:
        if not dir_path.exists():
            continue
            
        for file_path in dir_path.glob("*.py"):
            if file_path.name.startswith("__") or file_path.name in ["settings.py", "data_helpers.py"]:
                continue
                
            # Determine command name
            rel_path = file_path.relative_to(base_dir / "commands")
            parts = list(rel_path.parts)
            parts[-1] = parts[-1].replace(".py", "")  # Remove .py extension
            
            if len(parts) == 1:
                commands.append(parts[0])
            else:
                commands.append(f"{parts[0]}.{parts[1]}")
    
    return sorted(commands)

def get_command_module(command_name):
    """Get the module for a command"""
    if "." in command_name:
        category, name = command_name.split(".", 1)
        module_path = f"management.commands.{category}.{name}"
    else:
        module_path = f"management.commands.{command_name}"
    
    try:
        return importlib.import_module(module_path)
    except ImportError as e:
        logger.error(f"Command not found: {command_name}")
        logger.debug(str(e))
        return None

def main():
    """Main function for the command runner"""
    # Setup Django environment
    django_available = setup_django_env()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="TinySteps Management Command Runner")
    parser.add_argument("command", nargs="?", help="Command to run, format: [category.]command")
    parser.add_argument("--list", action="store_true", help="List available commands")
    parser.add_argument("--version", action="store_true", help="Show version information")
    
    args, unknown = parser.parse_known_args()
    
    if args.version:
        try:
            from management import __version__
            print(f"TinySteps Management System v{__version__}")
        except ImportError:
            print("TinySteps Management System")
        return
    
    if args.list:
        print("Available commands:")
        for cmd in list_available_commands():
            print(f"  - {cmd}")
        return
    
    # Show help if no command specified
    if not args.command:
        parser.print_help()
        return
    
    # Get and run the command module
    module = get_command_module(args.command)
    if module:
        try:
            # For Django management commands
            if hasattr(module, "Command"):
                if not django_available:
                    logger.error("This command requires Django to be available.")
                    return
                
                from django.core.management import call_command
                call_command(args.command.split(".")[-1], *unknown)
            
            # For standalone command modules
            elif hasattr(module, "main"):
                module.main(unknown)
            
            else:
                logger.error(f"Command module does not have required entry point: {args.command}")
        
        except Exception as e:
            logger.error(f"Error running command: {e}")
            import traceback
            logger.debug(traceback.format_exc())

if __name__ == "__main__":
    main()