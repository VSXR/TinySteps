from django.core.management.base import BaseCommand
from tinySteps.utils import create_event_reminders

class Command(BaseCommand):
    help = 'Sends reminders for calendar events scheduled for tomorrow'

    def handle(self, *args, **options):
        self.stdout.write('Creating event reminders...')
        create_event_reminders()
        self.stdout.write(self.style.SUCCESS('Successfully created event reminders'))