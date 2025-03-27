from django.core.management.base import BaseCommand
import logging
from tinySteps.utils import create_event_reminders

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sends reminders for calendar events scheduled for the near future'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days in advance to send reminders for (default: 1)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually sending reminders'
        )

    def handle(self, *args, **options):
        days_in_advance = options['days']
        dry_run = options['dry_run']
        
        self.stdout.write(f'Creating event reminders for events {days_in_advance} day(s) from now...')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No reminders will be sent'))
        
        try:
            reminder_count = create_event_reminders(
                days_in_advance=days_in_advance,
                dry_run=dry_run
            )
            
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'Dry run complete. {reminder_count} reminders would be created')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created {reminder_count} event reminders')
                )
                
        except Exception as e:
            logger.error(f"Error creating reminders: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Failed to create reminders: {str(e)}')
            )
