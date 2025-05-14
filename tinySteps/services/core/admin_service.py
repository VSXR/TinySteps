from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from tinySteps.repositories import Guide_Repository
from tinySteps.models import Guides_Model, Notification_Model
from tinySteps.registry import GuideType_Registry

class AdminGuide_Service:
    """Service for administrative guide operations"""
    
    def __init__(self):
        """Initialize repositories"""
        self.guide_repository = Guide_Repository(Guides_Model)
        self.notification_repository = Notification_Repository()
    
    def get_pending_guides_count(self):
        """Get count of all pending guides"""
        pending_guides = self.guide_repository.get_guides_by_type('parent', status='pending')
        pending_nutrition_guides = self.guide_repository.get_guides_by_type('nutrition', status='pending')
        return pending_guides.count() + pending_nutrition_guides.count()
    
    def get_related_guides(self, guide_id, count=3):
        """
        Get guides related to the given guide
        
        Args:
            guide_id (int): ID of the guide to find related guides for
            count (int, optional): Number of related guides to return
            
        Returns:
            QuerySet: A queryset of related guides
        """
        try:
            # Get the current guide
            guide = self.guide_repository.get_by_id(guide_id)
            if not guide:
                return []
                
            # Find guides of the same type, excluding the current one
            related_guides = self.guide_repository.get_guides_by_type(
                guide_type=guide.guide_type, 
                status='approved',
                count=count,
                exclude_id=guide_id
            )
            
            # If the guide has tags, we can filter by them
            if hasattr(guide, 'tags') and guide.tags.exists():
                tag_ids = guide.tags.values_list('id', flat=True)
                
                # More complex query would need to be implemented in the repository
                # For now, we'll just return guides of the same type if we have more time :)
                
            return related_guides
            
        except Exception as e:
            print(f"Error retrieving related guides: {e}")
            return []
            
    def approve_guide(self, guide_id):
        """
        Approve a guide
        
        Args:
            guide_id (int): ID of the guide to approve
            
        Returns:
            Guide: The approved guide
            
        Raises:
            ValueError: If the guide does not exist
        """
        guide = self.guide_repository.get_by_id(guide_id)
        if not guide:
            raise ValueError(_("Guide not found"))
            
        guide.status = 'approved'
        guide.approved_at = timezone.now()
        approved_guide = self.guide_repository.save(guide)
        
        # Create notification for the author
        self.notification_repository.create_notification(
            user=guide.author,
            message=_("Your guide '{0}' has been approved and published!").format(guide.title),
            url=guide.get_absolute_url()
        )
        
        return approved_guide
        
    def reject_guide(self, guide_id, rejection_reason, specific_feedback=None):
        """
        Reject a guide
        
        Args:
            guide_id (int): ID of the guide to reject
            rejection_reason (str): The main reason for rejection
            specific_feedback (str, optional): Specific feedback for the author
            
        Returns:
            Guide: The rejected guide
            
        Raises:
            ValueError: If the guide does not exist
        """
        guide = self.guide_repository.get_by_id(guide_id)
        if not guide:
            raise ValueError(_("Guide not found"))
            
        guide.status = 'rejected'
        guide.rejection_reason = rejection_reason
        guide.rejection_feedback = specific_feedback
        rejected_guide = self.guide_repository.save(guide)
        
        # Create notification for the author
        self.notification_repository.create_notification(
            user=guide.author,
            message=_("Your guide '{0}' was not approved. Reason: {1}").format(
                guide.title, 
                rejection_reason or _('No specific reason provided')
            ),
            url='/guides/admin_guides_panel/'  # Link to their guides panel
        )
        
        return rejected_guide


class Notification_Repository:
    """Repository for notifications"""
    
    def create_notification(self, user, message):
        """Create a notification for a user"""
        return Notification_Model.objects.create(
            user=user,
            message=message
        )