from django.utils import timezone
from django.utils.translation import gettext as _
from tinySteps.models import Guides_Model, Notification_Model

class AdminGuide_Service:
    """Service for guide administration tasks"""
    
    def get_guide(self, guide_id):
        """Get a guide by ID"""
        try:
            return Guides_Model.objects.get(id=guide_id)
        except Guides_Model.DoesNotExist:
            raise ValueError(_("Guide not found"))
    
    def approve_guide(self, guide_id):
        """Approve a guide"""
        guide = self.get_guide(guide_id)
        guide.status = 'approved'
        guide.approved_at = timezone.now()
        guide.save()
        
        # Create notification for the author
        Notification_Model.objects.create(
            user=guide.author,
            message=_("Your guide '{0}' has been approved and published!").format(guide.title),
            url=guide.get_absolute_url()
        )
        
        return guide
    
    def reject_guide(self, guide_id, rejection_reason):
        """Reject a guide"""
        guide = self.get_guide(guide_id)
        guide.status = 'rejected'
        guide.rejection_reason = rejection_reason
        guide.save()
        
        # Create notification for the author
        Notification_Model.objects.create(
            user=guide.author,
            message=_("Your guide '{0}' was not approved. Reason: {1}").format(
                guide.title, 
                rejection_reason or _('No specific reason provided')
            ),
            url='/guides/admin_guides_panel/'  # Link to their guides panel
        )
        
        return guide
    
    def get_pending_guides_count(self):
        """Get count of guides pending review"""
        return Guides_Model.objects.filter(status='pending').count()


class Notification_Repository:
    """Repository for notifications"""
    
    def create_notification(self, user, message):
        """Create a notification for a user"""
        return Notification_Model.objects.create(
            user=user,
            message=message
        )