from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from tinySteps.models import YourChild_Model
from tinySteps.forms import YourChild_Form
from tinySteps.factories.child.child_factory import ChildService_Factory

child_service = ChildService_Factory.create_service()

@login_required
def your_children(request):
    """View to display all children of the logged-in user"""
    children_list = YourChild_Model.objects.filter(user=request.user).order_by('name')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(children_list, 6)  # We show 6 children per page
    
    try:
        children = paginator.page(page)
    except PageNotAnInteger:
        children = paginator.page(1)
    except EmptyPage:
        children = paginator.page(paginator.num_pages)
    
    context = {
        'children': children,
    }
    
    return render(request, 'children/list.html', context)

@login_required
def your_child(request, child_id):
    """View to display details of a specific child"""
    child = get_object_or_404(YourChild_Model, pk=child_id, user=request.user)
    
    context = {
        'child': child,

        # TODO: IMPLEMENTAR SI DA TIEMPO
        'recent_milestones': child.milestones.order_by('-achieved_date')[:3],
        'upcoming_events': child.events.filter(date__gte=timezone.now().date()).order_by('date')[:3]
    }
    
    return render(request, 'children/detail.html', context)

@login_required
def add_child(request):
    """View to add a new child"""
    if request.method == 'POST':
        form = YourChild_Form(request.POST, request.FILES)
        if form.is_valid():
            child = child_service.create_child(form, request.user)
            messages.success(request, _("Child added successfully!"))
            return redirect('children:child_detail', child_id=child.pk)
    else:
        form = YourChild_Form()
    
    context = {
        'form': form,
        'children': request.user.children.all(),
        'today': timezone.now().date(),
    }
    
    return render(request, 'children/actions/create.html', context)

@login_required
def edit_child(request, child_id):
    """View to edit an existing child"""
    child = get_object_or_404(YourChild_Model, pk=child_id, user=request.user)
    
    if request.method == 'POST':
        form = YourChild_Form(request.POST, request.FILES, instance=child)
        if form.is_valid():
            updated_child = child_service.update_child(form, child_id, request.user)
            messages.success(request, _("Child details updated successfully!"))
            return redirect('children:child_detail', child_id=updated_child.pk)
    else:
        form = YourChild_Form(instance=child)
    
    context = {
        'child': child,
        'form': form,
        'update_subtitle': _("Update information for {name}").format(name=child.name),
    }
    
    return render(request, 'children/actions/edit.html', context)

@login_required
def delete_child(request, child_id):
    """View to delete a child"""
    child = get_object_or_404(YourChild_Model, pk=child_id, user=request.user)
    
    if request.method == 'POST':
        child_service.delete_child(child_id, request.user)
        messages.success(request, _("{name}'s profile has been deleted.").format(name=child.name))
        return redirect('children:your_children')
    
    context = {
        'yourchild_model': child,
        'children': request.user.children.exclude(pk=child_id),
    }
    
    return render(request, 'children/actions/delete.html', context)