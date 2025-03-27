from tinySteps.repositories.base.base_repository import GenericRepository
from tinySteps.models import Comment_Model

class Comment_Repository(GenericRepository):
    """Repository for comment-related operations"""
    
    def __init__(self):
        super().__init__(Comment_Model)
    
    def create_comment(self, content_type, object_id, text, author):
        """Create a new comment"""
        return self.create(
            content_type=content_type,
            object_id=object_id,
            text=text,
            author=author
        )
    
    def get_comments_for_object(self, content_type, object_id):
        """Get all comments for a specific object"""
        return self.filter(
            content_type=content_type,
            object_id=object_id
        ).select_related('author').order_by('-created_at')
    
    def get_recent_comments(self, limit=10):
        """Get recent comments across all content types"""
        return self.model.objects.all().select_related(
            'author', 'content_type'
        ).order_by('-created_at')[:limit]