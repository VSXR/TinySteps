"""
Command to manage the translation workflow for TinySteps
"""
import os
import re
import csv
import json
import polib
import logging
import argparse
from datetime import datetime
from pathlib import Path
from django.conf import settings as django_settings
from django.core.management.base import BaseCommand
from management.config.settings import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Manage translation workflow for TinySteps project'
    
    def add_arguments(self, parser):
        # Command category
        subparsers = parser.add_subparsers(dest='command', help='Command to run')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show translation status')
        status_parser.add_argument(
            '--locales', '-l',
            nargs='+',
            help='Locales to check (e.g., es en). '
        )
        status_parser.add_argument(
            '--format', '-f',
            choices=['text', 'json', 'csv'],
            default='text',
            help='Output format (default: text)'
        )
        status_parser.add_argument(
            '--output', '-o',
            help='Output file (default: stdout)'
        )
        
        # Extract command
        extract_parser = subparsers.add_parser('extract', help='Extract strings for translation')
        extract_parser.add_argument(
            '--locale', '-l',
            required=True,
            help='Locale to extract (e.g., es)'
        )
        extract_parser.add_argument(
            '--output', '-o',
            required=True,
            help='Output file (CSV format)'
        )
        extract_parser.add_argument(
            '--untranslated-only', '-u',
            action='store_true',
            help='Extract only untranslated strings'
        )
        
        # Import command
        import_parser = subparsers.add_parser('import', help='Import translations from CSV')
        import_parser.add_argument(
            '--input', '-i',
            required=True,
            help='Input CSV file with translations'
        )
        import_parser.add_argument(
            '--locale', '-l',
            required=True,
            help='Target locale (e.g., es)'
        )
        import_parser.add_argument(
            '--dry-run', '-d',
            action='store_true',
            help="Don't actually save translations, just show what would be done"
        )
        
        # Update command
        update_parser = subparsers.add_parser('update', help='Update translation files from source code')
        update_parser.add_argument(
            '--locales', '-l',
            nargs='+',
            help='Locales to update (e.g., es en). '
        )
        
        # Compile command
        compile_parser = subparsers.add_parser('compile', help='Compile translation files')
        compile_parser.add_argument(
            '--locales', '-l',
            nargs='+',
            help='Locales to compile (e.g., es en). '
        )
        
    def handle(self, *args, **options):
        command = options.get('command')
        
        if not command:
            self.print_help('manage.py', 'translation_workflow')
            return
            
        if command == 'status':
            self.handle_status(options)
        elif command == 'extract':
            self.handle_extract(options)
        elif command == 'import':
            self.handle_import(options)
        elif command == 'update':
            self.handle_update(options)
        elif command == 'compile':
            self.handle_compile(options)
        else:
            self.stderr.write(self.style.ERROR(f'Unknown command: {command}'))
            
    def handle_status(self, options):
        """Show translation status for all locales"""
        locales = options.get('locales')
        output_format = options.get('format')
        output_file = options.get('output')
        
        # If no locales specified, use supported languages from settings
        if not locales:
            supported_languages = settings.get('translations.supported_languages', ['en', 'es'])
            # Include default language in status report
            locales = supported_languages
        
        # Find the locale directory
        locale_dir = Path(django_settings.BASE_DIR) / 'locale'
        if not locale_dir.exists():
            self.stderr.write(self.style.ERROR(f'Locale directory not found: {locale_dir}'))
            return
        
        # Collect status data
        status_data = []
        
        for locale in locales:
            locale_status = {'locale': locale, 'files': []}
            
            # Find PO files for this locale
            po_dir = locale_dir / locale / 'LC_MESSAGES'
            if not po_dir.exists():
                locale_status['error'] = f'Directory not found for locale {locale}'
                status_data.append(locale_status)
                continue
            
            po_files = list(po_dir.glob('*.po'))
            if not po_files:
                locale_status['error'] = f'No PO files found for locale {locale}'
                status_data.append(locale_status)
                continue
            
            # Process each PO file
            for po_file_path in po_files:
                try:
                    po_file = polib.pofile(str(po_file_path))
                    
                    # Calculate statistics
                    total = len(po_file)
                    translated = len([e for e in po_file if e.translated()])
                    fuzzy = len([e for e in po_file if 'fuzzy' in e.flags])
                    untranslated = total - translated
                    
                    if total > 0:
                        percent_translated = (translated / total) * 100
                    else:
                        percent_translated = 100
                    
                    file_status = {
                        'file': po_file_path.name,
                        'total': total,
                        'translated': translated,
                        'untranslated': untranslated,
                        'fuzzy': fuzzy,
                        'percent_translated': percent_translated
                    }
                    
                    locale_status['files'].append(file_status)
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Error processing {po_file_path}: {str(e)}'))
            
            status_data.append(locale_status)
        
        # Output according to format
        if output_format == 'json':
            self._output_json(status_data, output_file)
        elif output_format == 'csv':
            self._output_csv(status_data, output_file)
        else:  # text
            self._output_text(status_data, output_file)
    
    def handle_extract(self, options):
        """Extract strings for translation to CSV"""
        locale = options.get('locale')
        output_file = options.get('output')
        untranslated_only = options.get('untranslated_only')
        
        # Find the locale directory
        locale_dir = Path(django_settings.BASE_DIR) / 'locale' / locale / 'LC_MESSAGES'
        if not locale_dir.exists():
            self.stderr.write(self.style.ERROR(f'Directory not found for locale {locale}'))
            return
        
        po_files = list(locale_dir.glob('*.po'))
        if not po_files:
            self.stderr.write(self.style.ERROR(f'No PO files found for locale {locale}'))
            return
        
        # Collect strings to extract
        extracted_strings = []
        
        for po_file_path in po_files:
            try:
                po_file = polib.pofile(str(po_file_path))
                
                for entry in po_file:
                    if untranslated_only and entry.translated():
                        continue
                    
                    # Use current translation as default if available
                    current_translation = entry.msgstr if entry.msgstr else ''
                    
                    extracted_strings.append({
                        'file': po_file_path.name,
                        'msgid': entry.msgid,
                        'msgstr': current_translation,
                        'fuzzy': 'fuzzy' in entry.flags,
                        'obsolete': entry.obsolete
                    })
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error processing {po_file_path}: {str(e)}'))
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['file', 'msgid', 'msgstr', 'fuzzy', 'obsolete']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in extracted_strings:
                writer.writerow(row)
        
        self.stdout.write(self.style.SUCCESS(f'Extracted {len(extracted_strings)} strings to {output_file}'))
    
    def handle_import(self, options):
        """Import translations from CSV"""
        input_file = options.get('input')
        locale = options.get('locale')
        dry_run = options.get('dry_run')
        
        # Find the locale directory
        locale_dir = Path(django_settings.BASE_DIR) / 'locale' / locale / 'LC_MESSAGES'
        if not locale_dir.exists():
            self.stderr.write(self.style.ERROR(f'Directory not found for locale {locale}'))
            return
        
        # Read CSV file
        translations = {}
        try:
            with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    file_name = row.get('file', '')
                    msgid = row.get('msgid', '')
                    msgstr = row.get('msgstr', '')
                    fuzzy = row.get('fuzzy', '').lower() in ('true', 'yes', '1')
                    
                    if not file_name or not msgid:
                        continue
                    
                    if file_name not in translations:
                        translations[file_name] = []
                    
                    translations[file_name].append({
                        'msgid': msgid,
                        'msgstr': msgstr,
                        'fuzzy': fuzzy
                    })
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error reading CSV file: {str(e)}'))
            return
        
        # Apply translations to PO files
        total_updated = 0
        
        for file_name, entries in translations.items():
            po_file_path = locale_dir / file_name
            
            if not po_file_path.exists():
                self.stderr.write(self.style.WARNING(f'PO file not found: {po_file_path}'))
                continue
            
            try:
                po_file = polib.pofile(str(po_file_path))
                updated_count = 0
                
                for entry_data in entries:
                    msgid = entry_data['msgid']
                    msgstr = entry_data['msgstr']
                    fuzzy = entry_data['fuzzy']
                    
                    # Find matching entry
                    entry = next((e for e in po_file if e.msgid == msgid), None)
                    
                    if entry:
                        if not dry_run:
                            entry.msgstr = msgstr
                            
                            # Handle fuzzy flag
                            if fuzzy and 'fuzzy' not in entry.flags:
                                entry.flags.append('fuzzy')
                            elif not fuzzy and 'fuzzy' in entry.flags:
                                entry.flags.remove('fuzzy')
                        
                        updated_count += 1
                        self.stdout.write(f"  {file_name}: '{msgid}' -> '{msgstr}'")
                
                if updated_count > 0 and not dry_run:
                    po_file.save()
                    
                    # Update MO file if it exists
                    mo_file_path = po_file_path.with_suffix('.mo')
                    if mo_file_path.exists():
                        po_file.save_as_mofile(str(mo_file_path))
                
                total_updated += updated_count
                self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} strings in {file_name}'))
                
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error processing {po_file_path}: {str(e)}'))
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'DRY RUN: Would have updated {total_updated} strings'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {total_updated} strings'))
    
    def handle_update(self, options):
        """Update translation files from source code"""
        locales = options.get('locales')
        
        # If no locales specified, use supported languages from settings
        if not locales:
            supported_languages = settings.get('translations.supported_languages', ['en', 'es'])
            # Remove default source language if present, no need to translate to it
            default_lang = settings.get('translations.default_language', 'en')
            if default_lang in supported_languages:
                supported_languages.remove(default_lang)
            locales = supported_languages
        
        # Build makemessages command
        cmd = ['django-admin', 'makemessages']
        
        for locale in locales:
            cmd.extend(['--locale', locale])
        
        # Run makemessages
        import subprocess
        try:
            self.stdout.write(self.style.NOTICE('Updating translation files...'))
            
            process = subprocess.run(
                cmd,
                cwd=str(django_settings.BASE_DIR),
                capture_output=True,
                text=True,
                check=True
            )
            
            self.stdout.write(self.style.SUCCESS('Successfully updated translation files'))
            if process.stdout:
                self.stdout.write(process.stdout)
                
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR('Error updating translation files:'))
            self.stderr.write(e.stderr)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
    
    def handle_compile(self, options):
        """Compile translation files"""
        locales = options.get('locales')
        
        # Build compilemessages command
        cmd = ['django-admin', 'compilemessages']
        
        if locales:
            for locale in locales:
                cmd.extend(['--locale', locale])
        
        # Run compilemessages
        import subprocess
        try:
            self.stdout.write(self.style.NOTICE('Compiling translation files...'))
            
            process = subprocess.run(
                cmd,
                cwd=str(django_settings.BASE_DIR),
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
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
    
    def _output_text(self, status_data, output_file):
        """Output status data as text"""
        lines = []
        
        for locale_status in status_data:
            locale = locale_status['locale']
            lines.append(f"\nTranslation status for locale: {locale}")
            lines.append("=" * 50)
            
            if 'error' in locale_status:
                lines.append(f"ERROR: {locale_status['error']}")
                continue
            
            for file_status in locale_status['files']:
                file_name = file_status['file']
                total = file_status['total']
                translated = file_status['translated']
                untranslated = file_status['untranslated']
                fuzzy = file_status['fuzzy']
                percent = file_status['percent_translated']
                
                lines.append(f"File: {file_name}")
                lines.append(f"  Total: {total} strings")
                lines.append(f"  Translated: {translated} strings ({percent:.1f}%)")
                lines.append(f"  Untranslated: {untranslated} strings")
                lines.append(f"  Fuzzy: {fuzzy} strings")
                lines.append("")
        
        output = "\n".join(lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            self.stdout.write(self.style.SUCCESS(f'Status written to {output_file}'))
        else:
            self.stdout.write(output)
    
    def _output_json(self, status_data, output_file):
        """Output status data as JSON"""
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2)
            self.stdout.write(self.style.SUCCESS(f'Status written to {output_file}'))
        else:
            self.stdout.write(json.dumps(status_data, indent=2))
    
    def _output_csv(self, status_data, output_file):
        """Output status data as CSV"""
        rows = []
        
        for locale_status in status_data:
            locale = locale_status['locale']
            
            if 'error' in locale_status:
                rows.append({
                    'locale': locale,
                    'file': 'ERROR',
                    'total': 0,
                    'translated': 0,
                    'untranslated': 0,
                    'fuzzy': 0,
                    'percent_translated': 0,
                    'error': locale_status['error']
                })
                continue
            
            for file_status in locale_status['files']:
                rows.append({
                    'locale': locale,
                    'file': file_status['file'],
                    'total': file_status['total'],
                    'translated': file_status['translated'],
                    'untranslated': file_status['untranslated'],
                    'fuzzy': file_status['fuzzy'],
                    'percent_translated': file_status['percent_translated'],
                    'error': ''
                })
        
        # Write to CSV
        fieldnames = ['locale', 'file', 'total', 'translated', 'untranslated', 'fuzzy', 'percent_translated', 'error']
        
        if output_file:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
            self.stdout.write(self.style.SUCCESS(f'Status written to {output_file}'))
        else:
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
            self.stdout.write(output.getvalue())
            output.close()

def main(args=None):
    """Run the command with the given arguments"""
    parser = argparse.ArgumentParser(description='Manage translation workflow for TinySteps project')
    
    # Command category
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show translation status')
    status_parser.add_argument(
        '--locales', '-l',
        nargs='+',
        help='Locales to check (e.g., es en). '
    )
    status_parser.add_argument(
        '--format', '-f',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format (default: text)'
    )
    status_parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract strings for translation')
    extract_parser.add_argument(
        '--locale', '-l',
        required=True,
        help='Locale to extract (e.g., es)'
    )
    extract_parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output file (CSV format)'
    )
    extract_parser.add_argument(
        '--untranslated-only', '-u',
        action='store_true',
        help='Extract only untranslated strings'
    )
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import translations from CSV')
    import_parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input CSV file with translations'
    )
    import_parser.add_argument(
        '--locale', '-l',
        required=True,
        help='Target locale (e.g., es)'
    )
    import_parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help="Don't actually save translations, just show what would be done"
    )
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update translation files from source code')
    update_parser.add_argument(
        '--locales', '-l',
        nargs='+',
        help='Locales to update (e.g., es en). '
    )
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile translation files')
    compile_parser.add_argument(
        '--locales', '-l',
        nargs='+',
        help='Locales to compile (e.g., es en). '
    )
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Create command and run
    cmd = Command()
    cmd.handle(**vars(parsed_args))

if __name__ == '__main__':
    main()