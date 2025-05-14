import logging
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _

from tinySteps.models import Guides_Model
from tinySteps.services.core.admin_service import AdminGuide_Service
from tinySteps.views.guides.guide_views import admin_guides_panel_view
from tinySteps.views.admin.moderation_views import review_guides as moderation_review_guides
from tinySteps.views.admin.moderation_views import approve_guide as moderation_approve_guide
from tinySteps.views.admin.moderation_views import reject_guide as moderation_reject_guide

logger = logging.getLogger(__name__)

@staff_member_required
def review_guides(request):
    """Render the review page using the moderation service."""
    if not request.user.is_authenticated:
        return redirect('login')

    return moderation_review_guides(request)

@staff_member_required
def review_guide(request, guide_id):
    """View a specific guide for review - delegates to moderation service"""
    try:
        from tinySteps.views.admin.moderation_views import review_guide
        return review_guide(request, guide_id)
    except Exception as e:
        logger.error(f"Error in admin review_guide: {str(e)}")
        messages.error(request, _("An error occurred while reviewing the guide"))
        return redirect('review_guides')

@staff_member_required
def approve_guide(request, guide_id):
    """Approve a guide by ID - delegates to moderation service"""
    next_url = request.GET.get('next', 'review_guides')
    
    try:
        response = moderation_approve_guide(request, guide_id)
        
        # Handle redirection based on the 'next' parameter
        if next_url == 'detail':
            guide = get_object_or_404(Guides_Model, pk=guide_id)
            if guide.guide_type == 'nutrition':
                return redirect('nutrition_guide_details', guide.id)
            else:
                return redirect('parent_guide_details', guide.id)
        
        if next_url == 'admin_guides_panel':
            return redirect('admin_guides_panel')
            
        return response
    except Exception as e:
        logger.error(f"Error in admin approve_guide: {str(e)}")
        messages.error(request, _("An error occurred while approving the guide"))
        return redirect('review_guides')

@staff_member_required
def reject_guide(request, guide_id):
    """Reject a guide submission with reason - delegates to moderation service"""
    guide = get_object_or_404(Guides_Model, pk=guide_id)
    next_page = request.POST.get('next', request.GET.get('next', 'admin_guides_panel'))
    
    # For GET requests, show the rejection form
    if request.method != 'POST':
        return render(request, 'guides/admin/reject_guide.html', {'guide': guide})
    
    # For POST requests, delegate to moderation view
    response = moderation_reject_guide(request, guide_id)
    
    # Handle custom redirection after successful rejection
    if next_page == 'admin_guides_panel':
        return redirect('admin_guides_panel')
    
    return response

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

@staff_member_required
def admin_guides_panel_view(request):
    """Admin guides panel that calls the function from guide_views.py"""
    from tinySteps.views.guides.guide_views import admin_guides_panel_view as guide_admin_panel
    return guide_admin_panel(request)