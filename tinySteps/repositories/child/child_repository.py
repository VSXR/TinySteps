from django.shortcuts import get_object_or_404
from django.db.models import Q
from tinySteps.models import YourChild_Model, Milestone_Model, VaccineCard_Model, Vaccine_Model, CalendarEvent_Model
from tinySteps.repositories.base.base_repository import GenericRepository

class Child_Repository(GenericRepository):
    """Repository for child-related operations"""
    
    def __init__(self):
        super().__init__(YourChild_Model)
    
    def get_user_children(self, user):
        """Get all children for a specific user"""
        return self.model.objects.filter(user=user).order_by('name')
    
    def get_child_by_id(self, child_id, user=None):
        """Get a specific child by ID, optionally filtering by user"""
        if user:
            return get_object_or_404(self.model, pk=child_id, user=user)
        return get_object_or_404(self.model, pk=child_id)
    
    def search_children(self, query_string, user=None):
        """Search children by name, optionally filtering by user"""
        search_query = Q(name__icontains=query_string) | Q(second_name__icontains=query_string)
        
        if user:
            search_query &= Q(user=user)
        
        return self.model.objects.filter(search_query).order_by('name')

class Milestone_Repository(GenericRepository):
    """Repository for milestone-related operations"""
    
    def __init__(self):
        super().__init__(Milestone_Model)
    
    def get_child_milestones(self, child_id):
        """Get all milestones for a specific child"""
        return self.model.objects.filter(child_id=child_id).order_by('-achieved_date')
    
    def get_recent_milestones(self, child_id, limit=3):
        """Get recent milestones for a specific child"""
        return self.model.objects.filter(child_id=child_id).order_by('-achieved_date')[:limit]

class VaccineCard_Repository(GenericRepository):
    """Repository for vaccine card-related operations"""
    
    def __init__(self):
        super().__init__(VaccineCard_Model)
    
    def get_or_create_for_child(self, child_id):
        """Get or create a vaccine card for a specific child"""
        card, created = self.model.objects.get_or_create(child_id=child_id)
        return card

class Vaccine_Repository(GenericRepository):
    """Repository for vaccine-related operations"""
    
    def __init__(self):
        super().__init__(Vaccine_Model)
    
    def get_child_vaccines(self, child_id):
        """Get all vaccines for a specific child"""
        return self.model.objects.filter(vaccine_card__child_id=child_id).order_by('date')
    
    def get_upcoming_vaccines(self, child_id):
        """Get upcoming vaccines for a specific child"""
        from django.utils import timezone
        
        return self.model.objects.filter(
            vaccine_card__child_id=child_id,
            date__gte=timezone.now().date(),
            administered=False
        ).order_by('date')

class CalendarEvent_Repository(GenericRepository):
    """Repository for calendar event-related operations"""
    
    def __init__(self):
        super().__init__(CalendarEvent_Model)
    
    def get_child_events(self, child_id):
        """Get all events for a specific child"""
        return self.model.objects.filter(child_id=child_id).order_by('date', 'time')
    
    def get_upcoming_events(self, child_id, limit=5):
        """Get upcoming events for a specific child"""
        from django.utils import timezone
        
        return self.model.objects.filter(
            child_id=child_id,
            date__gte=timezone.now().date()
        ).order_by('date', 'time')[:limit]
    
    def get_events_by_type(self, child_id, event_type):
        """Get events of a specific type for a specific child"""
        return self.model.objects.filter(
            child_id=child_id,
            type=event_type
        ).order_by('date', 'time')