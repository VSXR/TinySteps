from django.db.models import Q
from tinySteps.models import Guides_Model
from tinySteps.repositories.base.base_repository import GenericRepository

class Guide_Repository(GenericRepository):
    """Repository for guide-related operations"""
    
    def __init__(self):
        super().__init__(Guides_Model)
    
    def get_guides_by_type(self, guide_type, count=None):
        """Get guides by type with optional count limit"""
        query = self.model.objects.filter(guide_type=guide_type).order_by('-created_at')
        
        if count:
            query = query[:count]
            
        return query
    
    def get_related_guides(self, guide, limit=3):
        """Get related guides based on guide type"""
        return self.model.objects.filter(
            guide_type=guide.guide_type
        ).exclude(id=guide.id).order_by('-created_at')[:limit]
    
    def get_user_guides(self, user, status=None):
        """Get guides created by a specific user with optional status filter"""
        query = self.model.objects.filter(author=user)
        
        if status:
            query = query.filter(status=status)
            
        return query.order_by('-created_at')
    
    def get_guides_by_status(self, status, guide_type=None):
        """Get guides by status with optional guide type filter"""
        query = self.model.objects.filter(status=status)
        
        if guide_type:
            query = query.filter(guide_type=guide_type)
            
        return query.order_by('-created_at')
    
    def search_guides(self, query_string, guide_type=None):
        """Search guides by query string with optional guide type filter"""
        search_query = Q(title__icontains=query_string) | Q(desc__icontains=query_string)
        
        if guide_type:
            search_query &= Q(guide_type=guide_type)
        
        return self.model.objects.filter(search_query).order_by('-created_at')