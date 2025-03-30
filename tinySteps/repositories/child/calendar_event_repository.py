from django.db.models import Count
from datetime import date, timedelta
from tinySteps.models.child.child_models import CalendarEvent_Model
from tinySteps.repositories.base.base_repository import GenericRepository

class CalendarEvent_Repository(GenericRepository):
    """Repository for calendar event-related operations"""
    
    def __init__(self):
        super().__init__(CalendarEvent_Model)
    
    def get_child_events(self, child_id, start_date=None, end_date=None):
        """Get events for a specific child with optional date filtering"""
        query = self.model.objects.filter(child_id=child_id)
        
        if start_date:
            query = query.filter(date__gte=start_date)
        if end_date:
            query = query.filter(date__lte=end_date)
            
        return query.order_by('date', 'time')
    
    def get_upcoming_events(self, child_id, days=7, limit=None):
        """Get upcoming events for a specific child"""
        today = date.today()
        end_date = today + timedelta(days=days)
        
        query = self.model.objects.filter(
            child_id=child_id,
            date__gte=today,
            date__lte=end_date
        ).order_by('date', 'time')
        
        if limit:
            return query[:limit]
        return query
    
    def get_events_by_type(self, child_id, event_type):
        """Get events of a specific type for a specific child"""
        return self.model.objects.filter(
            child_id=child_id,
            type=event_type
        ).order_by('date', 'time')
    
    def get_events_with_reminders(self, child_id, days=7):
        """Get upcoming events with reminders enabled"""
        today = date.today()
        end_date = today + timedelta(days=days)
        
        return self.model.objects.filter(
            child_id=child_id,
            date__gte=today,
            date__lte=end_date,
            has_reminder=True
        ).order_by('date', 'time')
    
    def get_event_stats(self, child_id):
        """Get event statistics for a child"""
        # Count events by type
        event_counts = self.model.objects.filter(child_id=child_id)\
            .values('type')\
            .annotate(count=Count('id'))
        
        stats = {
            'doctor': 0,
            'vaccine': 0,
            'milestone': 0,
            'feeding': 0,
            'other': 0
        }
        
        for item in event_counts:
            stats[item['type']] = item['count']
        
        # Calculate total and upcoming
        today = date.today()
        stats['total'] = sum(stats.values())
        stats['upcoming'] = self.model.objects.filter(
            child_id=child_id, 
            date__gte=today
        ).count()
        
        return stats