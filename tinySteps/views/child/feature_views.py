from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _

from tinySteps.models import YourChild_Model, VaccineCard_Model
from tinySteps.forms import Milestone_Form, CalendarEvent_Form, Vaccine_Form
from tinySteps.services.core.child_service import Child_Service

@login_required
def child_milestone(request, child_id):
    """View to manage child milestones"""
    child = get_object_or_404(YourChild_Model, pk=child_id, user=request.user)
    
    if request.method == 'POST':
        form = Milestone_Form(request.POST, request.FILES)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.child = child
            milestone.save()
            return redirect('child_milestone', child_id=child_id)
    else:
        form = Milestone_Form()
    
    milestones = child.milestones.order_by('-achieved_date')
    context = {
        'child': child,
        'milestones': milestones,
        'form': form
    }
    
    return render(request, 'children/features/milestones/index.html', context)

@login_required
def child_calendar(request, child_id):
    """View to display and manage child calendar"""
    child = get_object_or_404(YourChild_Model, pk=child_id, user=request.user)
    
    context = {
        'child': child,
        'events': child.events.all().order_by('date')
    }
    
    return render(request, 'children/features/calendar/index.html', context)

@login_required
def child_vaccine_card(request, child_id):
    """View to display child vaccine card"""
    service = Child_Service()
    child = service.get_child_by_id(child_id, request.user)
    vaccine_card = service.get_or_create_vaccine_card(child_id, request.user)
    stats = service.get_vaccine_statistics(child_id, request.user)
    vaccines = service.get_vaccines(child_id, request.user)
    upcoming_vaccines = service.get_upcoming_vaccines(child_id, request.user)
    
    context = {
        'child': child,
        'vaccine_card': vaccine_card,
        'vaccines': vaccines,
        'upcoming_vaccines_list': upcoming_vaccines,
        'total_vaccines': stats['total'],
        'administered_vaccines': stats['administered'],
        'pending_vaccines': stats['pending'],
        'upcoming_vaccines': upcoming_vaccines.count()
    }
    
    return render(request, 'children/features/vaccine-card/index.html', context)

class YourChild_Calendar_View(LoginRequiredMixin, View):
    """Class-based view for child calendar management"""
    
    def get(self, request, child_id):
        """Display calendar and event form"""
        child = get_object_or_404(YourChild_Model, pk=child_id, user=request.user)
        form = CalendarEvent_Form()
        
        context = {
            'child': child,
            'events': child.events.all().order_by('date'),
            'form': form
        }
        
        return render(request, 'children/features/calendar/manage.html', context)
    
    def post(self, request, child_id):
        """Process event form submission"""
        child = get_object_or_404(YourChild_Model, pk=child_id, user=request.user)
        form = CalendarEvent_Form(request.POST)
        
        if form.is_valid():
            event = form.save(commit=False)
            event.child = child
            event.save()
            return redirect('child_calendar', child_id=child_id)
        
        context = {
            'child': child,
            'events': child.events.all().order_by('date'),
            'form': form
        }
        
        return render(request, 'children/features/calendar/manage.html', context)

class YourChild_VaccineCard_View(LoginRequiredMixin, View):
    """Class-based view for vaccine card management"""
    
    def get(self, request, child_id):
        """Display vaccine card and vaccine form"""
        child = get_object_or_404(YourChild_Model, pk=child_id, user=request.user)
        vaccine_card, _ = VaccineCard_Model.objects.get_or_create(child=child)
        form = Vaccine_Form()
        
        context = {
            'child': child,
            'vaccine_card': vaccine_card,
            'vaccines': vaccine_card.vaccines.all().order_by('date'),
            'form': form
        }
        
        return render(request, 'children/features/vaccines/manage.html', context)
    
    def post(self, request, child_id):
        """Process vaccine form submission"""
        child = get_object_or_404(YourChild_Model, pk=child_id, user=request.user)
        vaccine_card, _ = VaccineCard_Model.objects.get_or_create(child=child)
        form = Vaccine_Form(request.POST)
        
        if form.is_valid():
            vaccine = form.save(commit=False)
            vaccine.vaccine_card = vaccine_card
            vaccine.save()
            return redirect('child_vaccine_card', child_id=child_id)
        
        context = {
            'child': child,
            'vaccine_card': vaccine_card,
            'vaccines': vaccine_card.vaccines.all().order_by('date'),
            'form': form
        }
        
        return render(request, 'children/features/vaccine/manage.html', context)