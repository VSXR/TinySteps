from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings
import logging

from tinySteps.models.content.guide_models import Guides_Model
from tinySteps.services.logger.audit_logger import Audit_Logger

logger = logging.getLogger(__name__)
audit_logger = Audit_Logger()

class GuideModerationService:
    """Servicio para gestionar operaciones de moderación de guías"""
    
    def get_guide(self, guide_id):
        """Obtener una guía por ID"""
        try:
            return Guides_Model.objects.get(id=guide_id)
        except Guides_Model.DoesNotExist:
            raise ValueError(_("Guía no encontrada"))
    
    def approve_guide(self, guide_id, moderator=None):
        """Aprobar una guía y gestionar todas las operaciones relacionadas"""
        guide = self.get_guide(guide_id)
        
        # Actualizar estado de la guía
        guide.status = 'approved'
        guide.approved_at = timezone.now()
        guide.published_at = timezone.now()
        
        # Registrar información del moderador
        if moderator:
            guide.moderated_by = moderator
            guide.moderation_date = timezone.now()
            guide.moderation_notes = _("Aprobado por moderador")
        
        guide.save()
        
        # Enviar notificación por email
        self._send_approval_email(guide)
        
        # Registrar la acción
        self._log_moderation_action(guide, "approved", moderator)
        
        return guide
    
    def reject_guide(self, guide_id, rejection_reason, moderator=None):
        """Rechazar una guía con un motivo y gestionar todas las operaciones relacionadas"""
        guide = self.get_guide(guide_id)
        
        # Actualizar estado de la guía
        guide.status = 'rejected'
        guide.rejection_reason = rejection_reason
        
        # Registrar información del moderador
        if moderator:
            guide.moderated_by = moderator
            guide.moderation_date = timezone.now()
            guide.moderation_notes = _("Rechazado por moderador")
        
        guide.save()
        
        # Enviar notificación por email
        self._send_rejection_email(guide)
        
        # Registrar la acción
        self._log_moderation_action(guide, "rejected", moderator, rejection_reason)
        
        return guide
    
    def get_pending_guides_count(self):
        """Obtener el número de guías pendientes de revisión"""
        return Guides_Model.objects.filter(status='pending').count()
    
    def get_pending_guides(self):
        """Obtener todas las guías pendientes de revisión"""
        return Guides_Model.objects.filter(status='pending').order_by('-created_at')
    
    def get_guides_by_status(self, status=None, guide_type=None):
        """Get guides filtered by status and optionally by type"""
        if status and status != 'all':
            guides = Guides_Model.objects.filter(status=status)
        else:
            # Return all guides when status is None or 'all'
            guides = Guides_Model.objects.all()
        
        if guide_type:
            guides = guides.filter(guide_type=guide_type)
            
        return guides.order_by('-created_at')

    def _send_approval_email(self, guide):
        """Enviar notificación por email para aprobación de guía"""
        try:
            subject = _("¡Tu guía ha sido aprobada!")
            message = _("""
            Hola {author},
            
            Nos complace informarte que tu guía "{title}" ha sido aprobada y ya está publicada en nuestro sitio.
            
            Puedes ver tu guía publicada aquí: {site_url}{guide_url}
            
            Gracias por tu valiosa contribución.
            
            Saludos cordiales,
            El Equipo de TinySteps
            """).format(
                author=guide.author.get_full_name() or guide.author.username,
                title=guide.title,
                site_url=settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://tinysteps.com',
                guide_url=guide.get_absolute_url()
            )
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'no-reply@tinysteps.com',
                [guide.author.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Error al enviar email de aprobación para la guía {guide.id}: {str(e)}")
    
    def _send_rejection_email(self, guide):
        """Enviar notificación por email para rechazo de guía"""
        try:
            subject = _("Feedback sobre tu guía enviada")
            message = _("""
            Hola {author},
            
            Gracias por enviar tu guía "{title}".
            
            Hemos revisado tu envío y lamentablemente, no podemos publicarla en su forma actual.
            
            Motivo del rechazo:
            {reason}
            
            Te animamos a revisar tu guía basándote en este feedback y enviarla nuevamente.
            
            Saludos cordiales,
            El Equipo de TinySteps
            """).format(
                author=guide.author.get_full_name() or guide.author.username,
                title=guide.title,
                reason=guide.rejection_reason or _('No se proporcionó un motivo específico')
            )
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'no-reply@tinysteps.com',
                [guide.author.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Error al enviar email de rechazo para la guía {guide.id}: {str(e)}")
    
    def _log_moderation_action(self, guide, action, moderator=None, reason=None):
        """Registrar una acción de moderación para auditoría"""
        moderator_name = moderator.username if moderator else "Sistema"
        log_message = f"Guía '{guide.title}' (ID: {guide.id}) {action} por {moderator_name}"
        
        if reason:
            log_message += f". Motivo: {reason}"
            
        audit_logger.log_moderation_action(
            guide_id=guide.id,
            guide_title=guide.title,
            action=action,
            moderator=moderator_name,
            reason=reason
        )
        
        logger.info(log_message)