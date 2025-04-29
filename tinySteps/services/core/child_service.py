import logging
from datetime import date, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.db.models import Q

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
    
    # ===== Vaccine Card Methods =====
    def get_or_create_vaccine_card(self, child_id, user):
        """Get or create a vaccine card for a child"""
        child = self.get_child_by_id(child_id, user)
        vaccine_card, created = VaccineCard_Model.objects.get_or_create(child=child)
        return vaccine_card
    
    def get_vaccines(self, child_id, user, **filters):
        """
        Get all vaccines for a child with optional filtering
        
        Filters:
        - administered: boolean to filter by administration status
        - search: string to search in name and notes
        - upcoming_only: boolean to get only vaccines with future next_dose_date
        - sort_by: field to sort by ('name', 'date', 'next_dose_date')
        - sort_dir: direction to sort ('asc' or 'desc')
        """
        vaccine_card = self.get_or_create_vaccine_card(child_id, user)
        query = vaccine_card.vaccines.all()
        
        # Apply filters
        if 'administered' in filters:
            query = query.filter(administered=filters['administered'])
            
        if 'search' in filters and filters['search']:
            search_term = filters['search']
            query = query.filter(
                Q(name__icontains=search_term) | 
                Q(notes__icontains=search_term)
            )
            
        if filters.get('upcoming_only'):
            today = timezone.now().date()
            query = query.filter(next_dose_date__gte=today)
        
        # Apply sorting
        sort_field = filters.get('sort_by', 'date')
        sort_dir = filters.get('sort_dir', 'desc')
        
        if sort_field not in ['name', 'date', 'next_dose_date']:
            sort_field = 'date'
            
        if sort_dir == 'asc':
            sort_str = sort_field
        else:
            sort_str = f"-{sort_field}"
            
        if sort_field != 'name':
            if sort_dir == 'asc':
                sort_str = f"{sort_str},name"
                
        query = query.order_by(sort_str.replace(',', ''), sort_str.split(',')[1] if ',' in sort_str else 'name')
        
        return query
    
    def get_vaccine_by_id(self, vaccine_id, user):
        """Get a single vaccine ensuring user ownership"""
        return get_object_or_404(
            Vaccine_Model,
            pk=vaccine_id,
            vaccine_card__child__user=user
        )
    
    def get_vaccine_statistics(self, child_id, user):
        """Get statistics about a child's vaccines"""
        vaccine_card = self.get_or_create_vaccine_card(child_id, user)
        vaccines = vaccine_card.vaccines.all()
        
        total = vaccines.count()
        administered = vaccines.filter(administered=True).count()
        pending = total - administered
        
        today = timezone.now().date()
        upcoming = vaccines.filter(next_dose_date__gte=today).count()
        
        upcoming_30days = vaccines.filter(
            next_dose_date__gte=today,
            next_dose_date__lte=today + timedelta(days=30)
        ).count()
        
        return {
            'total': total,
            'administered': administered,
            'pending': pending,
            'upcoming': upcoming,
            'upcoming_30days': upcoming_30days
        }
    
    def get_upcoming_vaccines(self, child_id, user, days=30, limit=None):
        """Get upcoming vaccines for a child (next_dose_date in future)"""
        vaccine_card = self.get_or_create_vaccine_card(child_id, user)
        today = timezone.now().date()
        
        query = vaccine_card.vaccines.filter(next_dose_date__gte=today)
        
        if days:
            end_date = today + timedelta(days=days)
            query = query.filter(next_dose_date__lte=end_date)
            
        query = query.order_by('next_dose_date', 'name')
        
        if limit:
            query = query[:limit]
            
        return query
    
    def add_vaccine(self, child_id, user, vaccine_data):
        """Add a new vaccine for a child"""
        vaccine_card = self.get_or_create_vaccine_card(child_id, user)
        
        try:
            vaccine = Vaccine_Model.objects.create(
                vaccine_card=vaccine_card,
                name=vaccine_data['name'],
                date=vaccine_data['date'],
                administered=vaccine_data.get('administered', False),
                next_dose_date=vaccine_data.get('next_dose_date'),
                notes=vaccine_data.get('notes', '')
            )
            
            # If a vaccine is administered and creates a calendar event is enabled
            if vaccine.administered and vaccine_data.get('create_event', False):
                self._create_vaccine_event(child_id, user, vaccine)
                
            return vaccine
            
        except Exception as e:
            logger.error(f"Error creating vaccine: {str(e)}")
            raise
    
    def update_vaccine(self, vaccine_id, user, vaccine_data):
        """Update an existing vaccine"""
        vaccine = self.get_vaccine_by_id(vaccine_id, user)
        
        # Track if administration status changed
        was_administered = vaccine.administered
        
        # Update fields
        if 'name' in vaccine_data:
            vaccine.name = vaccine_data['name']
            
        if 'date' in vaccine_data:
            vaccine.date = vaccine_data['date']
            
        if 'administered' in vaccine_data:
            vaccine.administered = vaccine_data['administered']
            
        if 'next_dose_date' in vaccine_data:
            vaccine.next_dose_date = vaccine_data.get('next_dose_date')
            
        if 'notes' in vaccine_data:
            vaccine.notes = vaccine_data.get('notes', '')
        
        try:
            vaccine.save()
            
            # If vaccine was just marked as administered and create_event is enabled
            if not was_administered and vaccine.administered and vaccine_data.get('create_event', False):
                self._create_vaccine_event(vaccine.vaccine_card.child.id, user, vaccine)
                
            return vaccine
            
        except Exception as e:
            logger.error(f"Error updating vaccine {vaccine_id}: {str(e)}")
            raise
    
    def delete_vaccine(self, vaccine_id, user):
        """Delete a vaccine"""
        vaccine = self.get_vaccine_by_id(vaccine_id, user)
        
        try:
            # Optionally delete related calendar events
            if vaccine.administered:
                self._delete_vaccine_events(vaccine)
                
            vaccine.delete()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vaccine {vaccine_id}: {str(e)}")
            raise
    
    def batch_update_vaccines(self, child_id, user, updates):
        """
        Batch update multiple vaccines
        
        Args:
            child_id: ID of the child
            user: User performing the action
            updates: List of dicts with vaccine_id and fields to update
        
        Returns:
            dict: Summary of updates
        """
        results = {
            'success': 0,
            'failed': 0,
            'messages': []
        }
        
        for update in updates:
            try:
                vaccine_id = update.pop('id', None)
                if not vaccine_id:
                    results['failed'] += 1
                    results['messages'].append(f"Missing vaccine ID in update")
                    continue
                
                self.update_vaccine(vaccine_id, user, update)
                results['success'] += 1
                
            except Exception as e:
                results['failed'] += 1
                results['messages'].append(f"Error updating vaccine {vaccine_id}: {str(e)}")
        
        return results
    
    def _create_vaccine_event(self, child_id, user, vaccine):
        """Create a calendar event for an administered vaccine"""
        event_data = {
            'title': _("Vaccination: %(name)s") % {'name': vaccine.name},
            'type': 'vaccine',
            'date': vaccine.date,
            'time': None,
            'description': vaccine.notes if vaccine.notes else _("Vaccine administered"),
            'has_reminder': False
        }
        
        try:
            self.add_calendar_event(child_id, user, event_data)
            return True
        except Exception as e:
            logger.error(f"Error creating calendar event for vaccine: {str(e)}")
            return False
    
    def _delete_vaccine_events(self, vaccine):
        """Delete calendar events associated with a vaccine"""
        try:
            # Find events with matching title and date
            events = CalendarEvent_Model.objects.filter(
                child=vaccine.vaccine_card.child,
                type='vaccine',
                date=vaccine.date,
                title__contains=vaccine.name
            )
            
            if events.exists():
                events.delete()
                
            return True
        except Exception as e:
            logger.error(f"Error deleting vaccine events: {str(e)}")
            return False
    
    def get_recommended_vaccines(self, child_id, user):
        """
        Get recommended vaccines based on child's age
        """
        child = self.get_child_by_id(child_id, user)
        today = timezone.now().date()
        
        # Calculate child's age in months
        if not child.birth_date:
            return []
            
        birth_date = child.birth_date
        age_days = (today - birth_date).days
        age_months = age_days // 30
        recommendations = []
        
        if age_months <= 2:
            recommendations.append({
                'name': 'Hepatitis B (HepB)',
                'recommended_age': '0-2 months'
            })
            
        if 2 <= age_months <= 4:
            recommendations.extend([
                {'name': 'Diphtheria, Tetanus, & Pertussis (DTaP)', 'recommended_age': '2 months'},
                {'name': 'Polio (IPV)', 'recommended_age': '2 months'},
                {'name': 'Pneumococcal (PCV13)', 'recommended_age': '2 months'},
                {'name': 'Rotavirus (RV)', 'recommended_age': '2 months'}
            ])
            
        if 4 <= age_months <= 6:
            recommendations.extend([
                {'name': 'Diphtheria, Tetanus, & Pertussis (DTaP) - 2nd dose', 'recommended_age': '4 months'},
                {'name': 'Polio (IPV) - 2nd dose', 'recommended_age': '4 months'},
                {'name': 'Pneumococcal (PCV13) - 2nd dose', 'recommended_age': '4 months'},
                {'name': 'Rotavirus (RV) - 2nd dose', 'recommended_age': '4 months'}
            ])
        
        
        return recommendations
    
    # ===== Growth Data Methods =====
    def get_growth_data(self, child_id, user):
        """Get growth data for a child"""
        child = self.get_child_by_id(child_id, user)
        
        estimated_birth_weight = 3.5
        estimated_birth_height = 50.0
        
        # Basic data structure
        data = {
            'birthWeight': estimated_birth_weight,
            'currentWeight': child.weight or 0.0,
            'birthHeight': estimated_birth_height,
            'currentHeight': child.height or 0.0,
            'birthDate': child.birth_date.strftime('%Y-%m-%d') if child.birth_date else None,
            'currentDate': timezone.now().strftime('%Y-%m-%d'),
            'gender': child.gender,
            'ageMonths': child.age
        }
        
        return data
