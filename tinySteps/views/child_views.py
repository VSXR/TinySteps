from datetime import date, datetime, timedelta
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView

from ..forms import YourChild_Form, Milestone_Form
from ..models import (
    YourChild_Model, 
    CalendarEvent_Model, 
    VaccineCard_Model, 
    Vaccine_Model
)
from ..services.child_service import Child_Service

logger = logging.getLogger(__name__)

class BaseChildView(LoginRequiredMixin):
    """Base view for all child views"""
    login_url = 'login'
    
    def get_child_service(self):
        return Child_Service()
    
    def get_child_or_404(self, pk):
        """Get a child belonging to the current user or raise 404"""
        child = get_object_or_404(YourChild_Model, pk=pk) 
        if child.user != self.request.user:
            raise Http404(_("Child not found"))
        return child

    def handle_exception(self, exception, default_message):
        """Handle exceptions in a consistent way"""
        logger.error(f"Error in child view: {str(exception)}")
        from .error_views import database_error_view
        return database_error_view(self.request, default_message)

@login_required(login_url='login')
def your_children(request):
    """View to list all children for the current user (SRP)"""
    try:
        children = YourChild_Model.objects.filter(user=request.user)
        return render(request, 'children/list.html', {'children': children})
    except Exception as e:
        logger.error(f"Error loading children list: {str(e)}")
        from .error_views import database_error_view
        return database_error_view(request, _("Error loading your children. Please try again."))

@login_required(login_url='login')
def your_child(request, pk):
    """View to show a specific child's details (SRP)"""
    try:
        child = get_object_or_404(YourChild_Model, pk=pk)
        if child.user != request.user:
            raise Http404(_("Child not found"))
        
        return render(request, 'children/detail.html', {'child': child})
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error loading child details: {str(e)}")
        from .error_views import database_error_view
        return database_error_view(request, _("Error loading child details. Please try again."))

class YourChild_Add_View(LoginRequiredMixin, CreateView):
    """View to add a new child following SRP and OCP"""
    login_url = 'login'
    template_name = 'children/actions/create.html'
    model = YourChild_Model
    form_class = YourChild_Form
    success_url = reverse_lazy('your_children')
    
    def form_valid(self, form):
        """Assign the current user to the new child"""
        try:
            form.instance.user = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, _("Child added successfully!"))
            return response
        except Exception as e:
            logger.error(f"Error adding child: {str(e)}")
            messages.error(self.request, _("Error adding child. Please try again."))
            return self.form_invalid(form)

class YourChild_Delete_View(BaseChildView, DeleteView):
    """View to delete a child following SRP, OCP and DIP"""
    template_name = 'children/actions/delete.html'
    model = YourChild_Model
    success_url = reverse_lazy('your_children')
    
    def get_queryset(self):
        """Ensure users can only delete their own children"""
        return super().get_queryset().filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        """Get child and validate ownership"""
        obj = super().get_object(queryset)
        if not obj.user == self.request.user:
            raise Http404(_("Child not found"))
        return obj
    
    def child_has_events(self):
        """Check if the child has events (SRP)"""
        return CalendarEvent_Model.objects.filter(child=self.get_object()).exists()
    
    def get_context_data(self, **kwargs):
        """Add additional context data"""
        context = super().get_context_data(**kwargs)
        context['has_events'] = self.child_has_events()
        return context
    
    def delete(self, request, *args, **kwargs):
        """Delete the child and show success message"""
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(self.request, _("Child removed successfully!"))
            return response
        except Exception as e:
            logger.error(f"Error deleting child: {str(e)}")
            messages.error(self.request, _("Error removing child. Please try again."))
            return redirect('your_children')

class YourChild_UpdateDetails_View(BaseChildView, UpdateView):
    """View to update child details following SRP, OCP and DIP"""
    template_name = 'children/actions/edit.html'
    model = YourChild_Model
    form_class = YourChild_Form
    
    def get_queryset(self):
        """Ensure users can only update their own children"""
        return super().get_queryset().filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        """Get child and validate ownership"""
        return self.get_child_or_404(self.kwargs.get('pk'))
    
    def get_context_data(self, **kwargs):
        """Add additional context data"""
        context = super().get_context_data(**kwargs)
        context['children'] = YourChild_Model.objects.filter(user=self.request.user)
        return context
    
    def form_valid(self, form):
        """Save the form and show success message"""
        try:
            form.instance.user = self.request.user
            self.object = form.save(commit=True)
            self.object.refresh_from_db()
            
            messages.success(self.request, _("Child information updated successfully!"))
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Error updating child: {str(e)}")
            messages.error(self.request, _("Error updating child. Please try again."))
            return self.form_invalid(form)
    
    def get_success_url(self):
        """Return URL after successful update"""
        return reverse_lazy('child_details', kwargs={'pk': self.object.pk})

@login_required
def child_milestone(request, child_id):
    """View to manage child milestones following SRP and DIP"""
    try:
        # Get child and validate ownership
        child = get_object_or_404(YourChild_Model, id=child_id, user=request.user)
        
        if request.method == 'POST':
            form = Milestone_Form(request.POST, request.FILES)
            if form.is_valid():
                milestone = form.save(commit=False)
                milestone.child = child
                milestone.save()
                messages.success(request, _("Milestone added!"))
                return redirect('your_child', pk=child_id)
        else:
            form = Milestone_Form()
        
        return render(request, 'children/features/milestones/index.html', {
            'form': form, 
            'child': child,
            'today': timezone.now().date()
        })
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error in child_milestone: {str(e)}")
        from .error_views import database_error_view
        return database_error_view(request, _("Error managing milestone. Please try again."))

@login_required
def child_calendar(request, child_id):
    """View to show child calendar following SRP and DIP"""
    try:
        # Get child and validate ownership
        child = get_object_or_404(YourChild_Model, id=child_id, user=request.user)
        
        # Get event statistics
        event_stats = {
            'doctor': CalendarEvent_Model.objects.filter(child=child, type='doctor').count(),
            'vaccine': CalendarEvent_Model.objects.filter(child=child, type='vaccine').count(),
            'milestone': CalendarEvent_Model.objects.filter(child=child, type='milestone').count(),
            'feeding': CalendarEvent_Model.objects.filter(child=child, type='feeding').count(),
            'other': CalendarEvent_Model.objects.filter(child=child, type='other').count(),
        }
        
        # Get upcoming reminders and events
        upcoming_reminders = CalendarEvent_Model.objects.filter(
            child=child, 
            has_reminder=True,
            date__gte=date.today()
        ).order_by('date', 'time')[:5]

        upcoming_events = CalendarEvent_Model.objects.filter(
            child=child,
            date__gte=date.today()
        ).order_by('date', 'time')[:5]

        context = {
            'child': child,
            'event_stats': event_stats,
            'upcoming_reminders': upcoming_reminders,
            'upcoming_events': upcoming_events,
        }
        
        return render(request, 'children/features/calendar/index.html', context)
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error in child_calendar: {str(e)}")
        from .error_views import database_error_view
        return database_error_view(request, _("Error loading calendar. Please try again."))

@login_required
def child_vaccine_card(request, child_id):
    """View to show child vaccine card following SRP and DIP"""
    try:
        # Get child and validate ownership
        child = get_object_or_404(YourChild_Model, id=child_id, user=request.user)
        
        # Get or create vaccine card
        vaccine_card, _ = VaccineCard_Model.objects.get_or_create(child=child)
        vaccines = Vaccine_Model.objects.filter(vaccine_card=vaccine_card).order_by('next_dose_date', 'date')
        
        # Calculate statistics
        total_vaccines = vaccines.count()
        administered_vaccines = vaccines.filter(administered=True).count()
        pending_vaccines = total_vaccines - administered_vaccines
        
        # Get upcoming vaccines
        today = date.today()
        next_month = today + timedelta(days=30)
        upcoming_vaccines = vaccines.filter(
            next_dose_date__gte=today,
            next_dose_date__lte=next_month
        ).count()
        
        upcoming_vaccines_list = vaccines.filter(
            next_dose_date__gte=today
        ).order_by('next_dose_date')[:5]

        context = {
            'child': child,
            'vaccine_card': vaccine_card,
            'vaccines': vaccines,
            'total_vaccines': total_vaccines,
            'administered_vaccines': administered_vaccines,
            'pending_vaccines': pending_vaccines,
            'upcoming_vaccines': upcoming_vaccines,
            'upcoming_vaccines_list': upcoming_vaccines_list,
        }
        
        return render(request, 'children/features/vaccine-card/index.html', context)
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error in child_vaccine_card: {str(e)}")
        from .error_views import database_error_view
        return database_error_view(request, _("Error loading vaccine card. Please try again."))

class YourChild_Calendar_View(BaseChildView, View):
    """Class-based view for child calendar implementing SRP, OCP and DIP"""
    template_name = 'children/features/calendar/index.html'
    
    def get(self, request, pk):
        """Handle GET request for calendar view"""
        try:
            # Get child and validate ownership
            child = self.get_child_or_404(pk)
            
            # Get events
            events = CalendarEvent_Model.objects.filter(child=child).order_by('date', 'time')
            
            # Filter for specific date ranges
            today = datetime.now().date()
            week_later = today + timedelta(days=7)
            
            # Get upcoming reminders
            upcoming_reminders = events.filter(
                date__gte=today,
                date__lte=week_later,
                has_reminder=True
            ).order_by('date', 'time')
            
            # Get upcoming events
            upcoming_events = events.filter(
                date__gte=today,
                date__lte=week_later
            ).order_by('date', 'time')
            
            # Calculate event statistics
            event_stats = {
                'doctor': events.filter(type='doctor').count(),
                'vaccine': events.filter(type='vaccine').count(),
                'milestone': events.filter(type='milestone').count(),
                'feeding': events.filter(type='feeding').count(),
                'other': events.filter(type='other').count(),
            }
            
            return render(request, self.template_name, {
                'child': child,
                'events': events,
                'upcoming_reminders': upcoming_reminders,
                'upcoming_events': upcoming_events,
                'event_stats': event_stats
            })
        except Http404:
            raise
        except Exception as e:
            return self.handle_exception(e, _("Error loading calendar view. Please try again."))

class YourChild_VaccineCard_View(BaseChildView, DetailView):
    """Class-based view for vaccine card implementing SRP, OCP and DIP"""
    template_name = 'children/features/vaccine-card/index.html'
    model = YourChild_Model
    context_object_name = 'child'
    
    def get_queryset(self):
        """Ensure users can only view their own children's vaccine cards"""
        return super().get_queryset().filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        """Get child and validate ownership"""
        obj = super().get_object(queryset)
        if not obj.user == self.request.user:
            raise Http404(_("Child not found"))
        return obj
    
    def get_context_data(self, **kwargs):
        """Add vaccine card data to the context"""
        try:
            context = super().get_context_data(**kwargs)
            
            # Get or create vaccine card
            vaccine_card, _ = VaccineCard_Model.objects.get_or_create(child=self.object)
            
            # Get vaccines
            vaccines = Vaccine_Model.objects.filter(vaccine_card=vaccine_card).order_by('next_dose_date', 'date')
            context['vaccines'] = vaccines
            
            # Calculate statistics
            context['total_vaccines'] = vaccines.count()
            context['administered_vaccines'] = vaccines.filter(administered=True).count()
            context['pending_vaccines'] = context['total_vaccines'] - context['administered_vaccines']
            
            # Get upcoming vaccines
            today = date.today()
            next_month = today + timedelta(days=30)
            context['upcoming_vaccines'] = vaccines.filter(
                next_dose_date__gte=today,
                next_dose_date__lte=next_month
            ).count()
            
            context['upcoming_vaccines_list'] = vaccines.filter(
                next_dose_date__gte=today
            ).order_by('next_dose_date')[:5]
            
            return context
        except Exception as e:
            logger.error(f"Error in YourChild_VaccineCard_View: {str(e)}")
            raise
