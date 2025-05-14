import logging
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _

# Ajusta las importaciones según tu estructura
from tinySteps.models.content.guide_models import Guides_Model
from tinySteps.forms.content.guide_rejection_forms import GuideRejection_Form
from tinySteps.services.guides.moderation_service import GuideModerationService

logger = logging.getLogger(__name__)

@staff_member_required
def review_guides(request):
    """Renderizar el panel de moderación de guías"""
    service = GuideModerationService()
    
    # Obtener filtros de la URL
    status = request.GET.get('status', 'pending')
    guide_type = request.GET.get('type', None)
    
    # Obtener guías según filtros
    guides = service.get_guides_by_status(status, guide_type)
    
    # Estadísticas para el panel
    pending_count = service.get_pending_guides_count()
    approved_count = Guides_Model.objects.filter(status='approved').count()
    rejected_count = Guides_Model.objects.filter(status='rejected').count()
    
    context = {
        'guides': guides,
        'status': status,
        'guide_type': guide_type,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'title': _("Revisión de Guías"),
    }
    
    return render(request, 'guides/admin/admin_guides_panel.html', context)

@staff_member_required
def approve_guide(request, guide_id):
    """Aprobar una guía por ID"""
    next_url = request.GET.get('next', 'admin_guides_panel')
    
    try:
        service = GuideModerationService()
        guide = service.approve_guide(guide_id, request.user)
        
        messages.success(request, _(f"La guía '{guide.title}' ha sido aprobada y publicada!"))
        
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
        logger.error(f"Error al aprobar la guía: {str(e)}")
        messages.error(request, _("Ha ocurrido un error al aprobar la guía"))
        return redirect('review_guides')

@staff_member_required
def reject_guide(request, guide_id):
    """Rechazar una guía con motivo"""
    guide = get_object_or_404(Guides_Model, pk=guide_id)
    next_page = request.POST.get('next', request.GET.get('next', 'admin_guides_panel'))
    
    if request.method == 'POST':
        form = GuideRejection_Form(request.POST)
        
        if form.is_valid():
            rejection_reason = form.cleaned_data['rejection_reason']
            internal_notes = form.cleaned_data.get('internal_notes', '')
            
            try:
                service = GuideModerationService()
                guide = service.reject_guide(guide_id, rejection_reason, request.user)
                
                # Guardar notas internas si se proporcionaron
                if internal_notes:
                    guide.moderation_notes = internal_notes
                    guide.save(update_fields=['moderation_notes'])
                
                messages.success(request, _("La guía ha sido rechazada y se ha notificado al autor."))
                
                if next_page == 'admin_guides_panel':
                    return redirect('admin_guides_panel')
                return redirect('review_guides')
            except Exception as e:
                logger.error(f"Error al rechazar la guía: {str(e)}")
                messages.error(request, _("Ha ocurrido un error al rechazar la guía"))
                return redirect('review_guides')
        else:
            # Falló la validación del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # Visualización inicial del formulario
        form = GuideRejection_Form()
    
    context = {
        'form': form,
        'guide': guide,
        'title': _("Rechazar Guía"),
        'next': next_page,
    }
    
    return render(request, 'guides/admin/reject_guide.html', context)