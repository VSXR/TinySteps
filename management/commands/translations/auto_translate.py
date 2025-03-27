"""
Command to automatically translate missing strings using Google Translate
"""
import os
import json
import polib
import argparse
import logging
from pathlib import Path
from googletrans import Translator
from django.conf import settings as django_settings
from django.core.management.base import BaseCommand
from management.config.settings import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Automatically translate untranslated strings using Google Translate'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--locale', 
            '-l', 
            help='Target locale (e.g., es, fr). Default: all supported languages except source'
        )
        parser.add_argument(
            '--source', 
            '-s', 
            default=settings.get('translations.default_language', 'en'),
            help='Source language for translation'
        )
        parser.add_argument(
            '--min-percent', 
            '-m', 
            type=int, 
            default=0,
            help='Only process files below this percent of completion'
        )
        parser.add_argument(
            '--dry-run', 
            '-d', 
            action='store_true',
            help="Don't actually save translations, just show what would be done"
        )
        
    def handle(self, *args, **options):
        # Get options
        locale = options.get('locale')
        source_lang = options.get('source')
        min_percent = options.get('min_percent')
        dry_run = options.get('dry_run')
        
        # Initialize translator
        translator = Translator()
        
        # Get supported languages from settings
        supported_languages = settings.get('translations.supported_languages', ['en', 'es'])
        
        # Determine locales to process
        locales_to_process = []
        if locale:
            if locale in supported_languages:
                locales_to_process.append(locale)
            else:
                self.stderr.write(self.style.ERROR(f'Locale {locale} not in supported languages: {supported_languages}'))
                return
        else:
            # Process all supported languages except source language
            locales_to_process = [lang for lang in supported_languages if lang != source_lang]
        
        # Find the locale directory
        locale_dir = Path(django_settings.BASE_DIR) / 'locale'
        if not locale_dir.exists():
            self.stderr.write(self.style.ERROR(f'Locale directory not found: {locale_dir}'))
            return
        
        # Count of translations made
        translated_count = 0
        processed_files = 0
        
        # Process each locale
        for target_locale in locales_to_process:
            self.stdout.write(self.style.NOTICE(f'\nProcessing locale: {target_locale}'))
            
            # Find PO files for this locale
            po_dir = locale_dir / target_locale / 'LC_MESSAGES'
            if not po_dir.exists():
                self.stderr.write(self.style.WARNING(f'Directory not found for locale {target_locale}: {po_dir}'))
                continue
            
            po_files = list(po_dir.glob('*.po'))
            if not po_files:
                self.stderr.write(self.style.WARNING(f'No PO files found for locale {target_locale}'))
                continue
            
            # Process each PO file
            for po_file_path in po_files:
                try:
                    po_file = polib.pofile(str(po_file_path))
                    
                    # Check completion percentage
                    translated = len([e for e in po_file if e.translated()])
                    total = len(po_file)
                    
                    if total == 0:
                        percent_translated = 100
                    else:
                        percent_translated = (translated / total) * 100
                    
                    if percent_translated >= min_percent:
                        self.stdout.write(f'Skipping {po_file_path.name} ({percent_translated:.1f}% translated)')
                        continue
                    
                    self.stdout.write(self.style.SUCCESS(f'Processing {po_file_path.name} ({percent_translated:.1f}% translated)'))
                    processed_files += 1
                    
                    # Find untranslated entries
                    untranslated = [e for e in po_file if not e.translated()]
                    
                    if not untranslated:
                        self.stdout.write(f'No untranslated strings found in {po_file_path.name}')
                        continue
                    
                    self.stdout.write(f'Found {len(untranslated)} untranslated strings')
                    
                    # Translate in batches of 50 to avoid API limitations
                    batch_size = 50
                    for i in range(0, len(untranslated), batch_size):
                        batch = untranslated[i:i+batch_size]
                        
                        # Create a batch of original strings to translate
                        texts = [entry.msgid for entry in batch]
                        
                        # Call Google Translate API
                        try:
                            translations = translator.translate(
                                texts, 
                                src=source_lang,
                                dest=target_locale
                            )
                            
                            # Update each entry with its translation
                            for j, entry in enumerate(batch):
                                translation = translations[j].text if isinstance(translations, list) else translations.text
                                
                                # Print what would be translated
                                self.stdout.write(f'  "{entry.msgid}" -> "{translation}"')
                                
                                # Update the translation if not dry run
                                if not dry_run:
                                    entry.msgstr = translation
                                    translated_count += 1
                            
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f'Error translating batch: {str(e)}'))
                            continue
                    
                    # Save the file if not dry run
                    if not dry_run:
                        po_file.save()
                        self.stdout.write(self.style.SUCCESS(f'Saved translations to {po_file_path}'))
                        
                        # If mo file exists, update it too
                        mo_file_path = po_file_path.with_suffix('.mo')
                        if mo_file_path.exists():
                            po_file.save_as_mofile(str(mo_file_path))
                            self.stdout.write(f'Updated .mo file: {mo_file_path}')
                
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Error processing {po_file_path}: {str(e)}'))
        
        # Print summary
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'\nDRY RUN: Would have translated {translated_count} strings in {processed_files} files'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nTranslated {translated_count} strings in {processed_files} files'))
            
def main(args=None):
    """Run the command with the given arguments."""
    parser = argparse.ArgumentParser(description='Automatically translate strings using Google Translate')
    parser.add_argument(
        '--locale', '-l', 
        help='Target locale (e.g., es, fr). Default: all supported languages except source'
    )
    parser.add_argument(
        '--source', '-s', 
        default=settings.get('translations.default_language', 'en'),
        help='Source language for translation'
    )
    parser.add_argument(
        '--min-percent', '-m', 
        type=int, 
        default=0,
        help='Only process files below this percent of completion'
    )
    parser.add_argument(
        '--dry-run', '-d', 
        action='store_true',
        help="Don't actually save translations, just show what would be done"
    )
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Create command and run
    cmd = Command()
    cmd.handle(
        locale=parsed_args.locale,
        source=parsed_args.source,
        min_percent=parsed_args.min_percent,
        dry_run=parsed_args.dry_run
    )

if __name__ == '__main__':
    main()