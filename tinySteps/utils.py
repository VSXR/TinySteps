from datetime import datetime, timedelta
from .models import Notification_Model, CalendarEvent_Model

def create_event_reminders():
    """
    Creates notifications for calendar events with reminders set
    that are scheduled for tomorrow
    """
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Get all events scheduled for tomorrow with reminders set
    # and that have not been notified for the same day
    events = CalendarEvent_Model.objects.filter(
        date=tomorrow,
        has_reminder=True 
    )
    
    # Create notifications for each event and checks if a notification
    # for the same event already exists for the same day
    for event in events:
        notification_exists = Notification_Model.objects.filter(
            user=event.child.user,
            title__contains=event.title,
            created_at__date=today
        ).exists()
        
        if not notification_exists:
            Notification_Model.objects.create(
                user=event.child.user,
                title=f"Reminder: {event.title}",
                message=f"Tomorrow {event.date} at {event.time or '00:00'}: {event.title} for {event.child.name}",
                read=False
            )