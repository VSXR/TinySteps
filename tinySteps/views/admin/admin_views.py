from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from tinySteps.services import AdminGuide_Service
from tinySteps.forms import GuideRejection_Form

@login_required
@user_passes_test(lambda u: u.is_staff)
def review_guides(request, admin_service=None):
    service = admin_service or AdminGuide_Service()
    guide_type = request.GET.get('type')
    
    try:
        pending_guides = admin_service.get_pending_guides(guide_type)
        stats = admin_service.get_pending_guides_stats()
        context = {
            'guides': pending_guides, 
            'current_type': guide_type,
            'total_count': stats['total'],
            'parent_count': stats['parent'],
            'nutrition_count': stats['nutrition']
        }
        
        return render(request, 'guides/admin/review_guides.html', context)
    except Exception as e:
        from tinySteps.views.base.error_views import database_error_view
        return database_error_view(request, _("Error loading guides for review."))

@login_required
@user_passes_test(lambda u: u.is_staff)
def approve_guide(request, guide_id):
    """Admin view to approve a guide"""
    admin_service = AdminGuide_Service()
    
    try:
        guide = admin_service.approve_guide(guide_id)
        messages.success(request, _("Guide approved and published successfully!"))
        guide_type = request.GET.get('type')
        if guide_type:
            return redirect(f'/admin/guides/review?type={guide_type}')
        return redirect('/admin/guides/review')
    except Exception as e:
        from tinySteps.views.base.error_views import database_error_view
        return database_error_view(request, _("Error approving guide."))

@login_required
@user_passes_test(lambda u: u.is_staff)
def reject_guide(request, guide_id):
    """Admin view to reject a guide"""
    admin_service = AdminGuide_Service()
    
    try:
        if request.method == 'POST':
            form = GuideRejection_Form(request.POST)
            if form.is_valid():
                rejection_reason = form.cleaned_data['rejection_reason']
                guide = admin_service.reject_guide(guide_id, rejection_reason)
                messages.success(request, _("Guide rejected successfully."))
                guide_type = request.GET.get('type')
                if guide_type:
                    return redirect(f'/admin/guides/review?type={guide_type}')
                return redirect('/admin/guides/review')
        else:
            form = GuideRejection_Form()
            guide = admin_service.get_guide(guide_id)
            
            return render(request, 'guides/admin/reject_guide.html', {
                'form': form,
                'guide': guide
            })
    except Exception as e:
        from tinySteps.views.base.error_views import database_error_view
        return database_error_view(request, _("Error rejecting guide."))

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