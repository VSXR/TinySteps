from django.utils import timezone
import logging
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings

from tinySteps.models.content.guide_models import Guides_Model
from tinySteps.services.logger.audit_logger import Audit_Logger

logger = logging.getLogger(__name__)
audit_logger = Audit_Logger()

class GuideModeration_Service:
    """Service to manage guide moderation operations"""
    
    def get_guide(self, guide_id):
        """Get a guide by ID"""
        try:
            return Guides_Model.objects.get(id=guide_id)
        except Guides_Model.DoesNotExist:
            return None
    
    def approve_guide(self, guide_id, moderator=None):
        """Approve a guide and manage all related operations"""
        guide = self.get_guide(guide_id)
        if not guide:
            return None
            
        # Update guide status
        guide.status = 'approved'
        guide.approved_at = timezone.now()
        guide.published_at = timezone.now()
        
        # Record moderator information
        if moderator:
            guide.approved_by = moderator
        
        guide.save()
        
        # Send email notification
        self._send_approval_email(guide)
        
        # Log the action
        self._log_moderation_action(guide, "approved", moderator)
        
        return guide
    
    def reject_guide(self, guide_id, rejection_reason, moderator=None):
        """Reject a guide and manage all related operations"""
        guide = self.get_guide(guide_id)
        if not guide:
            return None
            
        # Update guide status
        guide.status = 'rejected'
        guide.rejected_at = timezone.now()
        guide.rejection_reason = rejection_reason
        
        # Record moderator information
        if moderator:
            guide.rejected_by = moderator
        
        guide.save()
        
        # Send email notification
        self._send_rejection_email(guide)
        
        # Log the action
        self._log_moderation_action(guide, "rejected", moderator, reason=rejection_reason)
        
        return guide
    
    def get_pending_guides_count(self):
        """Get count of pending guides"""
        return Guides_Model.objects.filter(status='pending').count()
    
    def get_pending_guides(self):
        """Get all pending guides"""
        return Guides_Model.objects.filter(status='pending').order_by('-created_at')
    
    def get_guides_by_status(self, status=None, guide_type=None):
        """Get guides filtered by status and optionally by type"""
        if status and status != 'all':
            guides = Guides_Model.objects.filter(status=status)
        else:
            # Return all guides when status is None or 'all'
            guides = Guides_Model.objects.all()
        
        if guide_type and guide_type != 'all':
            guides = guides.filter(guide_type=guide_type)
            
        return guides.order_by('-created_at')

    def _send_approval_email(self, guide):
        """Send approval notification email to guide author"""
        try:
            send_mail(
                subject=_("Your guide has been approved"),
                message=_(f"Your guide '{guide.title}' has been approved and is now published."),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[guide.author.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Error sending approval email: {str(e)}")
    
    def _send_rejection_email(self, guide):
        """Send rejection notification email to guide author"""
        try:
            send_mail(
                subject=_("Your guide needs revision"),
                message=_(f"Your guide '{guide.title}' was not approved for the following reason: {guide.rejection_reason}"),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[guide.author.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Error sending rejection email: {str(e)}")
    
    def _log_moderation_action(self, guide, action, moderator=None, reason=None):
        """Log moderation action for auditing"""
        actor = moderator.username if moderator else 'system'
        guide_id = guide.id
        guide_title = guide.title
        
        if action == "approved":
            message = f"Guide '{guide_title}' (ID: {guide_id}) was approved by {actor}"
        elif action == "rejected":
            message = f"Guide '{guide_title}' (ID: {guide_id}) was rejected by {actor}. Reason: {reason}"
        
        # Log to audit system
        audit_logger.log_action(
            actor=actor,
            action=f"guide_{action}",
            resource_id=guide_id,
            resource_type="guide",
            message=message
        )
