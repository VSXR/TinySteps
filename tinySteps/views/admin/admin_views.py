import logging
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _

from tinySteps.models import Guides_Model
from tinySteps.forms import GuideRejection_Form
from tinySteps.services.core.admin_service import AdminGuide_Service
from tinySteps.views.guides.guide_views import admin_guides_panel_view

logger = logging.getLogger(__name__)

@staff_member_required
def review_guides(request):
    """Render the review page using the proper context from admin_guides_panel_view."""
    if not request.user.is_authenticated:
        return redirect('login')
    return admin_guides_panel_view(request)

@staff_member_required
def approve_guide(request, guide_id):
    """Approve a guide by ID"""
    next_url = request.GET.get('next', 'review_guides')
    
    try:
        service = AdminGuide_Service()
        guide = service.approve_guide(guide_id)
        
        messages.success(request, _(f"The guide '{guide.title}' has been approved and published!"))
        
        if next_url == 'detail':
            if guide.guide_type == 'nutrition':
                return redirect('nutrition_guide_details', guide.id)
            else:
                return redirect('parent_guide_details', guide.id)
        
        if next_url == 'admin_guides_panel':
            return redirect('admin_guides_panel')
            
        return redirect('review_guides')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('review_guides')
    except Exception as e:
        logger.error(f"Error approving guide: {str(e)}")
        messages.error(request, _("An error occurred while approving the guide"))
        return redirect('review_guides')

@staff_member_required
def reject_guide(request, guide_id):
    """Reject a guide submission with reason"""
    guide = get_object_or_404(Guides_Model, pk=guide_id)
    next_page = request.POST.get('next', request.GET.get('next', 'admin_guides_panel'))
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if not rejection_reason:
            messages.error(request, _("Please provide a reason for rejecting this guide."))
            return render(request, 'guides/admin/reject_guide.html', {'guide': guide})
            
        try:
            service = AdminGuide_Service()
            service.reject_guide(guide_id, rejection_reason)
            
            messages.success(request, _("The guide has been rejected and the author has been notified."))
            
            if next_page == 'admin_guides_panel':
                return redirect('admin_guides_panel')
            return redirect('review_guides')
        except Exception as e:
            logger.error(f"Error rejecting guide: {str(e)}")
            messages.error(request, _("An error occurred while rejecting the guide"))
            return redirect('review_guides')
    
    # If not POST, show the rejection form
    return render(request, 'guides/admin/reject_guide.html', {'guide': guide})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    """Admin dashboard view"""
    service = AdminGuide_Service()
    pending_guides_count = service.get_pending_guides_count()
    
    context = {
        'pending_guides_count': pending_guides_count,
    }
    
    return render(request, 'admin/dashboard.html', context)
