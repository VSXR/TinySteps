"""
Command to initialize translation files for TinySteps
"""
import os
import logging
import argparse
import subprocess
from pathlib import Path
from django.conf import settings as django_settings
from django.core.management.base import BaseCommand
from management.config.settings import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize translation files for TinySteps project'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--locales', '-l',
            nargs='+',
            help='Locales to create (e.g., es en). '
        )
        parser.add_argument(
            '--domain', '-d',
            default='django',
            help='Translation domain (default: django)'
        )
        parser.add_argument(
            '--extensions', '-e',
            default='html,txt,py',
            help='File extensions to examine (comma separated, default: html,txt,py)'
        )
        parser.add_argument(
            '--ignore', '-i',
            default='venv,env,.git,__pycache__,static,media,migrations',
            help='Directories to ignore (comma separated)'
        )
        
    def handle(self, *args, **options):
        # Get options
        locales = options.get('locales')
        domain = options.get('domain')
        extensions = options.get('extensions')
        ignore_patterns = options.get('ignore').split(',')
        
        # If no locales specified, use supported languages from settings
        if not locales:
            locales = settings.get('translations.supported_languages', ['en', 'es'])
            # Remove default source language if present, no need to translate to it
            default_lang = settings.get('translations.default_language', 'en')
            if default_lang in locales:
                locales.remove(default_lang)
        
        # Project directory
        base_dir = Path(django_settings.BASE_DIR)
        locale_dir = base_dir / 'locale'
        
        # Create locale directory if it doesn't exist
        if not locale_dir.exists():
            os.makedirs(locale_dir, exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f'Created locale directory: {locale_dir}'))
        
        # Check if makemessages management command is available
        try:
            # Create .po files for each locale
            for locale in locales:
                self.stdout.write(self.style.NOTICE(f'Creating translation files for locale: {locale}'))
                
                # Build makemessages command
                cmd = [
                    'django-admin', 'makemessages',
                    f'--locale={locale}',
                    f'--domain={domain}',
                    f'--extension={extensions}'
                ]
                
                # Add ignore patterns
                for pattern in ignore_patterns:
                    if pattern:
                        cmd.append(f'--ignore={pattern}')
                
                # Run makemessages command
                try:
                    process = subprocess.run(
                        cmd,
                        cwd=str(base_dir),
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    self.stdout.write(self.style.SUCCESS(f'Successfully created translation files for {locale}'))
                    if process.stdout:
                        self.stdout.write(process.stdout)
                except subprocess.CalledProcessError as e:
                    self.stderr.write(self.style.ERROR(f'Error creating translation files for {locale}:'))
                    self.stderr.write(e.stderr)
            
            # Compile message files
            self.stdout.write(self.style.NOTICE('Compiling translation files...'))
            try:
                process = subprocess.run(
                    ['django-admin', 'compilemessages'],
                    cwd=str(base_dir),
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.stdout.write(self.style.SUCCESS('Successfully compiled translation files'))
                if process.stdout:
                    self.stdout.write(process.stdout)
            except subprocess.CalledProcessError as e:
                self.stderr.write(self.style.ERROR('Error compiling translation files:'))
                self.stderr.write(e.stderr)
                
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error initializing translations: {str(e)}'))
            
        self.stdout.write(self.style.SUCCESS('\nTranslation initialization completed'))
        self.stdout.write('You can now edit the .po files in the locale directory or use Rosetta at /rosetta/')

def main(args=None):
    """Run the command with the given arguments."""
    parser = argparse.ArgumentParser(description='Initialize translation files for TinySteps project')
    parser.add_argument(
        '--locales', '-l',
        nargs='+',
        help='Locales to create (e.g., es en). '
    )
    parser.add_argument(
        '--domain', '-d',
        default='django',
        help='Translation domain (default: django)'
    )
    parser.add_argument(
        '--extensions', '-e',
        default='html,txt,py',
        help='File extensions to examine (comma separated, default: html,txt,py)'
    )
    parser.add_argument(
        '--ignore', '-i',
        default='venv,env,.git,__pycache__,static,media,migrations',
        help='Directories to ignore (comma separated)'
    )
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Create command and run
    cmd = Command()
    cmd.handle(
        locales=parsed_args.locales,
        domain=parsed_args.domain,
        extensions=parsed_args.extensions,
        ignore=parsed_args.ignore if parsed_args.ignore else 'venv,env,.git,__pycache__,static,media,migrations'
    )

if __name__ == '__main__':
    main()