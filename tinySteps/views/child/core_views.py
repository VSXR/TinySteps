from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from tinySteps.models import YourChild_Model

@login_required
def your_children(request):
    """View to display all children of the logged-in user"""
    children = YourChild_Model.objects.filter(user=request.user)
    
    context = {
        'children': children,
    }
    
    return render(request, 'child/children_list.html', context)

@login_required
def your_child(request, pk):
    """View to display details of a specific child"""
    child = get_object_or_404(YourChild_Model, pk=pk, user=request.user)
    
    context = {
        'child': child,
        'recent_milestones': child.milestones.order_by('-achieved_date')[:3],
        'upcoming_events': child.events.filter(date__gte=timezone.now().date()).order_by('date')[:3]
    }
    
    return render(request, 'child/child_details.html', context)