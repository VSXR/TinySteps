from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _

from tinySteps.models import Guides_Model
from tinySteps.forms import GuideRejection_Form
from tinySteps.services.core.admin_service import AdminGuide_Service

@staff_member_required
def review_guides(request):
    """Admin view for reviewing pending guides"""
    guide_type = request.GET.get('type')
    
    # Base query - only get pending guides
    pending_guides = Guides_Model.objects.filter(status='pending')
    
    # Get counts for the dashboard
    total_count = pending_guides.count()
    parent_count = pending_guides.filter(guide_type='parent').count()
    nutrition_count = pending_guides.filter(guide_type='nutrition').count()
    
    # Filter by type if specified
    if guide_type in ['parent', 'nutrition']:
        guides = pending_guides.filter(guide_type=guide_type)
    else:
        guides = pending_guides
    
    # Order by newest first
    guides = guides.order_by('-created_at')
    
    context = {
        'guides': guides,
        'current_type': guide_type,
        'total_count': total_count,
        'parent_count': parent_count,
        'nutrition_count': nutrition_count,
    }
    
    return render(request, 'guides/admin/review_guides.html', context)

@staff_member_required
def approve_guide(request, guide_id):
    """Approve a guide submission"""
    guide = get_object_or_404(Guides_Model, pk=guide_id)
    next_page = request.GET.get('next', 'my_guides')
    
    if guide.status == 'pending':
        guide.status = 'approved'
        guide.save()
        messages.success(request, _("Guide successfully approved!"))
    else:
        messages.warning(request, _("This guide is not pending approval."))
    
    # Redirect back to either review panel or my guides
    if next_page == 'review':
        return redirect('review_guides')
    return redirect('my_guides')

@staff_member_required
def reject_guide(request, guide_id):
    """Reject a guide submission with reason"""
    guide = get_object_or_404(Guides_Model, pk=guide_id)
    next_page = request.POST.get('next', request.GET.get('next', 'my_guides'))
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if guide.status == 'pending' and rejection_reason:
            guide.status = 'rejected'
            guide.rejection_reason = rejection_reason
            guide.save()
            messages.success(request, _("Guide rejected with feedback."))
        else:
            messages.error(request, _("Unable to reject guide. Please provide a reason."))
        
        # Redirect back to either review panel or my guides
        if next_page == 'review':
            return redirect('review_guides')
        return redirect('my_guides')
    
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
        return database_error_view(request, _("Error loading admin dashboard."))
    
