import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect

from tinySteps.models.content.guide_models import Guides_Model
from tinySteps.services.guides.moderation_service import GuideModeration_Service

logger = logging.getLogger(__name__)
moderation_service = GuideModeration_Service()

@staff_member_required
def review_guides(request):
    """Show guides for review"""
    # Get filters from URL
    status = request.GET.get('status', 'all')
    guide_type = request.GET.get('type', None)
    
    # Direct database queries to ensure we get results
    if status == 'all' or not status:
        guides = Guides_Model.objects.all()
    else:
        guides = Guides_Model.objects.filter(status=status)
    
    # Apply guide type filter if provided and not "all"
    if guide_type and guide_type != 'all':
        guides = guides.filter(guide_type=guide_type)
    
    # Always apply ordering
    guides = guides.order_by('-created_at')
    
    # Debug info - uncomment to troubleshoot
    print(f"Found {guides.count()} guides for status={status}, type={guide_type}")
    
    # Statistics for panel
    pending_count = Guides_Model.objects.filter(status='pending').count()
    approved_count = Guides_Model.objects.filter(status='approved').count()
    rejected_count = Guides_Model.objects.filter(status='rejected').count()
    total_count = Guides_Model.objects.count()
    
    context = {
        'guides': guides,
        'status': status,
        'guide_type': guide_type,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_count': total_count,
        'title': _("Guides Review"),
    }
    
    return render(request, 'guides/admin/admin_guides_panel.html', context)

@staff_member_required
def review_guide(request, guide_id):
    """View a specific guide for review"""
    guide = get_object_or_404(Guides_Model, pk=guide_id)
    
    related_guides = []
    try:
        # Get related guides directly
        related_guides = Guides_Model.objects.filter(
            guide_type=guide.guide_type, 
            status='approved'
        ).exclude(id=guide.id).order_by('-created_at')[:3]
    except Exception as e:
        logger.warning(f"Error retrieving related guides: {e}")
    
    return render(request, 'guides/admin/review_guide.html', {
        'guide': guide,
        'related_guides': related_guides,
        'title': _("Review Guide"),
    })

@staff_member_required
def approve_guide(request, guide_id):
    """Approve a guide"""
    guide = get_object_or_404(Guides_Model, id=guide_id)
    
    # Only approve if it's pending
    if guide.status != 'approved':
        moderation_service.approve_guide(guide_id, moderator=request.user)
        messages.success(request, _("Guide approved successfully"))
    else:
        messages.info(request, _("Guide was already approved"))
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/guides/review/'))

@staff_member_required
def reject_guide(request, guide_id):
    """Reject a guide"""
    guide = get_object_or_404(Guides_Model, id=guide_id)
    
    # Process rejection form
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if not rejection_reason:
            messages.error(request, _("Please provide a rejection reason"))
            return redirect('review_guides')
        
        moderation_service.reject_guide(guide_id, rejection_reason, moderator=request.user)
        messages.success(request, _("Guide rejected successfully"))
    else:
        messages.error(request, _("Invalid request method"))
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/guides/review/'))