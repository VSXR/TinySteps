import logging
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _

from tinySteps.models import Guides_Model
from tinySteps.forms import GuideRejection_Form
from tinySteps.services.core.admin_service import AdminGuide_Service
from django.shortcuts import redirect
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
    service = AdminGuide_Service()
    guide = service.approve_guide(guide_id)
    
    messages.success(request, _(f"The guide '{guide.title}' has been approved."))
    
    if next_url == 'detail':
        if guide.guide_type == 'nutrition':
            return redirect('nutrition_guide_details', guide.id)
        else:
            return redirect('parent_guide_details', guide.id)
    
    if next_url == 'review':
        return redirect('review_guides')
    
    return redirect(next_url)

@staff_member_required
def reject_guide(request, guide_id):
    """Reject a guide submission with reason"""
    guide = get_object_or_404(Guides_Model, pk=guide_id)
    next_page = request.POST.get('next', request.GET.get('next', 'admin_guides_panel'))
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if guide.status == 'pending' and rejection_reason:
            guide.status = 'rejected'
            guide.rejection_reason = rejection_reason
            guide.save()
            messages.success(request, _("Guide rejected with feedback."))
        else:
            messages.error(request, _("Unable to reject guide. Please provide a reason."))
        
        return redirect('admin_guides_panel')
    
    # If not POST, show the rejection form
    form = GuideRejection_Form()
    context = {
        'guide': guide,
        'form': form,
        'next': next_page
    }
    
    return render(request, 'guides/admin/reject_guide.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    """Admin dashboard view"""
    admin_service = AdminGuide_Service()
    
    try:
        stats = admin_service.get_admin_stats()
        context = {
            'stats': stats,
            'recent_guides': admin_service.get_recent_guides(5),
            'pending_guides': admin_service.get_pending_guides_count()
        }
        
        return render(request, 'guides/admin/dashboard.html', context)
    except Exception as e:
        from tinySteps.views.base.error_views import database_error_view
