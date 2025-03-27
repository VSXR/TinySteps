import logging
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from tinySteps.models import (
    YourChild_Model,
    Milestone_Model,
    CalendarEvent_Model,
    VaccineCard_Model,
    Vaccine_Model
)

logger = logging.getLogger(__name__)

class Child_Service:
    """Service for child-related operations"""
    
    def get_children_for_user(self, user):
        """Get all children for a user"""
        return YourChild_Model.objects.filter(user=user).order_by('name')
    
    def get_child_by_id(self, child_id, user=None):
        """Get a child by ID with optional user ownership validation"""
        query = {'pk': child_id}
        if user:
            query['user'] = user
            
        return get_object_or_404(YourChild_Model, **query)
    
    def create_child(self, form, user):
        """Create a new child"""
        child = form.save(commit=False)
        child.user = user
        child.save()
        return child
    
    def update_child(self, form, child_id, user):
        """Update a child's information"""
        child = self.get_child_by_id(child_id, user)
        form.instance.user = user
        updated_child = form.save()
        return updated_child
    
    def delete_child(self, child_id, user):
        """Delete a child"""
        child = self.get_child_by_id(child_id, user)
        child.delete()
        return True
    
    def child_has_events(self, child_id):
        """Check if a child has calendar events"""
        return CalendarEvent_Model.objects.filter(child_id=child_id).exists()
    
    # Milestone methods
    def add_milestone(self, child_id, user, form_data):
        """Add a milestone for a child"""
        child = self.get_child_by_id(child_id, user)
        
        milestone = Milestone_Model(
            child=child,
            title=form_data.get('title'),
            achieved_date=form_data.get('achieved_date'),
            description=form_data.get('description')
        )
        
        if form_data.get('photo'):
            milestone.photo = form_data.get('photo')
            
        milestone.save()
        return milestone
    
    def get_milestones(self, child_id, user=None):
        """Get all milestones for a child"""
        child = self.get_child_by_id(child_id, user)
        return Milestone_Model.objects.filter(child=child).order_by('-achieved_date')
    
    # Calendar methods
    def get_calendar_events(self, child_id, user=None, future_only=False, limit=None):
        """Get calendar events for a child"""
        child = self.get_child_by_id(child_id, user)
        
        query = CalendarEvent_Model.objects.filter(child=child)
        
        if future_only:
            query = query.filter(date__gte=date.today())
            
        query = query.order_by('date', 'time')
        
        if limit:
            query = query[:limit]
            
        return query
    
    def get_event_statistics(self, child_id, user=None):
        """Get event statistics for a child"""
        child = self.get_child_by_id(child_id, user)
        
        return {
            'doctor': CalendarEvent_Model.objects.filter(child=child, type='doctor').count(),
            'vaccine': CalendarEvent_Model.objects.filter(child=child, type='vaccine').count(),
            'milestone': CalendarEvent_Model.objects.filter(child=child, type='milestone').count(),
            'feeding': CalendarEvent_Model.objects.filter(child=child, type='feeding').count(),
            'other': CalendarEvent_Model.objects.filter(child=child, type='other').count(),
        }
    
    def get_upcoming_reminders(self, child_id, user=None, days=30, limit=5):
        """Get upcoming reminders for a child"""
        child = self.get_child_by_id(child_id, user)
        today = date.today()
        end_date = today + timedelta(days=days)
        
        return CalendarEvent_Model.objects.filter(
            child=child,
            has_reminder=True,
            date__gte=today,
            date__lte=end_date
        ).order_by('date', 'time')[:limit]
    
    def add_calendar_event(self, child_id, user, event_data):
        """Add a calendar event for a child"""
        child = self.get_child_by_id(child_id, user)
        
        event = CalendarEvent_Model(
            child=child,
            title=event_data.get('title'),
            type=event_data.get('type', 'other'),
            date=event_data.get('date'),
            time=event_data.get('time'),
            description=event_data.get('description', ''),
            has_reminder=event_data.get('has_reminder', False)
        )
        
        if event_data.get('reminder_minutes'):
            event.reminder_minutes = event_data.get('reminder_minutes')
            
        event.save()
        return event
    
    # Vaccine card methods
    def get_or_create_vaccine_card(self, child_id, user=None):
        """Get or create a vaccine card for a child"""
        child = self.get_child_by_id(child_id, user)
        vaccine_card, created = VaccineCard_Model.objects.get_or_create(child=child)
        return vaccine_card
    
    def get_vaccines(self, child_id, user=None):
        """Get all vaccines for a child"""
        vaccine_card = self.get_or_create_vaccine_card(child_id, user)
        return Vaccine_Model.objects.filter(vaccine_card=vaccine_card).order_by('next_dose_date', 'date')
    
    def get_vaccine_statistics(self, child_id, user=None):
        """Get vaccine statistics for a child"""
        vaccines = self.get_vaccines(child_id, user)
        
        total = vaccines.count()
        administered = vaccines.filter(administered=True).count()
        
        return {
            'total': total,
            'administered': administered,
            'pending': total - administered
        }
    
    def get_upcoming_vaccines(self, child_id, user=None, days=30, limit=5):
        """Get upcoming vaccines for a child"""
        vaccines = self.get_vaccines(child_id, user)
        today = date.today()
        end_date = today + timedelta(days=days)
        
        return vaccines.filter(
            next_dose_date__gte=today,
            next_dose_date__lte=end_date
        ).order_by('next_dose_date')[:limit]
    
    def add_vaccine(self, child_id, user, vaccine_data):
        """Add a vaccine for a child"""
        vaccine_card = self.get_or_create_vaccine_card(child_id, user)
        
        vaccine = Vaccine_Model(
            vaccine_card=vaccine_card,
            name=vaccine_data.get('name'),
            date=vaccine_data.get('date'),
            administered=vaccine_data.get('administered', False)
        )
        
        if vaccine_data.get('notes'):
            vaccine.notes = vaccine_data.get('notes')
            
        if vaccine_data.get('next_dose_date'):
            vaccine.next_dose_date = vaccine_data.get('next_dose_date')
            
        vaccine.save()
        return vaccine
    
    def mark_vaccine_administered(self, vaccine_id, user):
        """Mark a vaccine as administered"""
        try:
            vaccine = Vaccine_Model.objects.get(pk=vaccine_id)
            
            # Verify ownership
            if vaccine.vaccine_card.child.user != user:
                raise PermissionError(_("You do not have permission to modify this vaccine"))
                
            vaccine.administered = True
            vaccine.save()
            return True
        except Vaccine_Model.DoesNotExist:
            logger.error(f"Vaccine with ID {vaccine_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error marking vaccine administered: {str(e)}")
            return False