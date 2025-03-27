from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _

from tinySteps.models import YourChild_Model, VaccineCard_Model
from tinySteps.forms import Milestone_Form, CalendarEvent_Form, Vaccine_Form

@login_required
def child_milestone(request, pk):
    """View to manage child milestones"""
    child = get_object_or_404(YourChild_Model, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = Milestone_Form(request.POST, request.FILES)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.child = child
            milestone.save()
            return redirect('child_milestone', pk=pk)
    else:
        form = Milestone_Form()
    
    milestones = child.milestones.order_by('-achieved_date')
    
    context = {
        'child': child,
        'milestones': milestones,
        'form': form
    }
    
    return render(request, 'child/milestone.html', context)

@login_required
def child_calendar(request, pk):
    """View to display and manage child calendar"""
    child = get_object_or_404(YourChild_Model, pk=pk, user=request.user)
    
    context = {
        'child': child,
        'events': child.events.all().order_by('date')
    }
    
    return render(request, 'child/calendar.html', context)

@login_required
def child_vaccine_card(request, pk):
    """View to display child vaccine card"""
    child = get_object_or_404(YourChild_Model, pk=pk, user=request.user)
    
    # Ensure child has a vaccine card
    vaccine_card, created = VaccineCard_Model.objects.get_or_create(child=child)
    
    context = {
        'child': child,
        'vaccine_card': vaccine_card,
        'vaccines': vaccine_card.vaccines.all().order_by('date')
    }
    
    return render(request, 'child/vaccine_card.html', context)

class YourChild_Calendar_View(LoginRequiredMixin, View):
    """Class-based view for child calendar management"""
    
    def get(self, request, pk):
        """Display calendar and event form"""
        child = get_object_or_404(YourChild_Model, pk=pk, user=request.user)
        form = CalendarEvent_Form()
        
        context = {
            'child': child,
            'events': child.events.all().order_by('date'),
            'form': form
        }
        
        return render(request, 'child/calendar_manage.html', context)
    
    def post(self, request, pk):
        """Process event form submission"""
        child = get_object_or_404(YourChild_Model, pk=pk, user=request.user)
        form = CalendarEvent_Form(request.POST)
        
        if form.is_valid():
            event = form.save(commit=False)
            event.child = child
            event.save()
            return redirect('child_calendar', pk=pk)
        
        context = {
            'child': child,
            'events': child.events.all().order_by('date'),
            'form': form
        }
        
        return render(request, 'child/calendar_manage.html', context)

class YourChild_VaccineCard_View(LoginRequiredMixin, View):
    """Class-based view for vaccine card management"""
    
    def get(self, request, pk):
        """Display vaccine card and vaccine form"""
        child = get_object_or_404(YourChild_Model, pk=pk, user=request.user)
        vaccine_card, created = VaccineCard_Model.objects.get_or_create(child=child)
        form = Vaccine_Form()
        
        context = {
            'child': child,
            'vaccine_card': vaccine_card,
            'vaccines': vaccine_card.vaccines.all().order_by('date'),
            'form': form
        }
        
        return render(request, 'child/vaccine_card_manage.html', context)
    
    def post(self, request, pk):
        """Process vaccine form submission"""
        child = get_object_or_404(YourChild_Model, pk=pk, user=request.user)
        vaccine_card, created = VaccineCard_Model.objects.get_or_create(child=child)
        form = Vaccine_Form(request.POST)
        
        if form.is_valid():
            vaccine = form.save(commit=False)
            vaccine.vaccine_card = vaccine_card
            vaccine.save()
            return redirect('child_vaccine_card', pk=pk)
        
        context = {
            'child': child,
            'vaccine_card': vaccine_card,
            'vaccines': vaccine_card.vaccines.all().order_by('date'),
            'form': form
        }
        
        return render(request, 'child/vaccine_card_manage.html', context)