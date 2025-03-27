from django.utils import timezone
from django.shortcuts import get_object_or_404
from tinySteps.repositories import Guide_Repository
from tinySteps.models import Guides_Model, Notification_Model

class AdminGuide_Service:
    """Service for guide administration tasks"""
    
    def __init__(self, repository=None):
        self.repository = repository or Guide_Repository()
        self.notification_repository = Notification_Repository()
    
    def get_pending_guides(self, guide_type=None):
        """Get guides pending approval"""
        query = Guides_Model.objects.filter(status='pending')
        
        if guide_type:
            query = query.filter(guide_type=guide_type)
            
        return query.order_by('-created_at')
    
    def get_pending_guides_stats(self):
        """Get statistics about pending guides"""
        total = Guides_Model.objects.filter(status='pending').count()
        parent = Guides_Model.objects.filter(status='pending', guide_type='parent').count()
        nutrition = Guides_Model.objects.filter(status='pending', guide_type='nutrition').count()
        
        return {
            'total': total,
            'parent': parent,
            'nutrition': nutrition
        }
    
    def get_guide(self, guide_id):
        """Get a specific guide by ID"""
        return get_object_or_404(Guides_Model, id=guide_id)
    
    def approve_guide(self, guide_id):
        """Approve a guide"""
        guide = self.get_guide(guide_id)
        guide.status = 'approved'
        guide.approved_at = timezone.now()
        guide.save()
        
        # Create notification for the author
        Notification_Model.objects.create(
            user=guide.author,
            message=f"Your guide '{guide.title}' has been approved and published!"
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
            message=f"Your guide '{guide.title}' was not approved. Reason: {rejection_reason or 'No specific reason provided'}"
        )
        
        return guide
    
    def get_admin_stats(self):
        """Get statistics for admin dashboard"""
        return {
            'total_guides': Guides_Model.objects.count(),
            'approved_guides': Guides_Model.objects.filter(status='approved').count(),
            'pending_guides': Guides_Model.objects.filter(status='pending').count(),
            'rejected_guides': Guides_Model.objects.filter(status='rejected').count(),
            'parent_guides': Guides_Model.objects.filter(guide_type='parent').count(),
            'nutrition_guides': Guides_Model.objects.filter(guide_type='nutrition').count(),
        }
    
    def get_recent_guides(self, limit=5):
        """Get recent guides for admin dashboard"""
        return Guides_Model.objects.all().order_by('-created_at')[:limit]
    
    def get_pending_guides_count(self):
        """Get count of pending guides"""
        return Guides_Model.objects.filter(status='pending').count()


class Notification_Repository:
    """Repository for notifications"""
    
    def create_notification(self, user, message):
        """Create a notification for a user"""
        return Notification_Model.objects.create(
            user=user,
            message=message
        )