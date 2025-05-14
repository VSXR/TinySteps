from django.db.models import Q
from tinySteps.models import Guides_Model
from tinySteps.repositories.base.base_repository import GenericRepository

class Guide_Repository(GenericRepository):
    """Repository for accessing guide data in a consistent way"""
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    def get_by_id(self, guide_id):
        """Get a guide by ID"""
        try:
            return self.model_class.objects.get(id=guide_id)
        except self.model_class.DoesNotExist:
            return None
    
    def get_guide_details(self, guide_id, guide_type=None):
        """
        Get detailed guide information by ID and optional guide type
        
        Args:
            guide_id (int): The ID of the guide to retrieve
            guide_type (str, optional): The type of guide ('parent' or 'nutrition')
            
        Returns:
            Guide model instance or None if not found
        """
        query = Q(id=guide_id)
        
        if guide_type:
            query &= Q(guide_type=guide_type)
            
        try:
            # Get the guide with select_related to reduce database queries
            return self.model_class.objects.select_related('author').get(query)
        except self.model_class.DoesNotExist:
            return None
    
    def get_guides_by_type(self, guide_type, status=None, count=None, page=None, exclude_id=None):
        """
        Get guides filtered by type and optionally by status
        
        Args:
            guide_type (str): Type of guide ('parent' or 'nutrition')
            status (str, optional): Status filter ('approved', 'pending', 'rejected')
            count (int, optional): Number of results to return
            page (int, optional): Page number for pagination
            exclude_id (int, optional): ID of guide to exclude from results
                
        Returns:
            QuerySet: Filtered guides
        """
        query = self.model_class.objects.filter(guide_type=guide_type)
        
        if status:
            query = query.filter(status=status)
            
        if exclude_id:
            query = query.exclude(id=exclude_id)
            
        query = query.order_by('-created_at')
        
        if count and not page:
            query = query[:count]
                
        return query
    
    def get_guide_by_id(self, guide_id):
        """Get a specific guide by ID"""
        try:
            return self.model_class.objects.get(id=guide_id)
        except self.model_class.DoesNotExist:
            return None
    
    def get_related_guides(self, guide, count=3):
        """Get guides related to the given guide"""
        return self.model_class.objects.filter(
            guide_type=guide.guide_type,
            status='approved'
        ).exclude(id=guide.id).order_by('-created_at')[:count]
    
    def get_guide_comments(self, guide_id):
        """Get comments for a specific guide"""
        try:
            guide = self.get_guide_by_id(guide_id)
            if guide:
                return guide.comments.all().order_by('-created_at')
            return []
        except Exception:
            return []
        
    def get_guides_by_age(self, guide_type, age_months, count=4):
        """Get guides appropriate for a specific age"""
        # Filtrar por tipo y status, ordenar por relevancia
        guides = self.model_class.objects.filter(
            guide_type=guide_type,
            status='approved'
        ).order_by('-created_at')
        
        return guides[:count]
    
    def search_guides(self, query_text, guide_type=None, status='approved', page=None):
        """Search guides by text"""
        search_query = Q(title__icontains=query_text) | Q(description__icontains=query_text)
        
        filters = Q(status=status)
        if guide_type:
            filters &= Q(guide_type=guide_type)
            
        return self.model_class.objects.filter(search_query, filters).order_by('-created_at')
    
    def search_all_guides(self, query_text, status='approved', limit=10):
        """Search all guides regardless of type"""
        search_query = Q(title__icontains=query_text) | Q(description__icontains=query_text)
        result = self.model_class.objects.filter(search_query, status=status).order_by('-created_at')
        
        if limit:
            result = result[:limit]
            
        return result
    
    def get_all(self):
        """Get all guides"""
        return self.model_class.objects.all()
    
    def get_by_status(self, status):
        """Get guides by status"""
        return self.model_class.objects.filter(status=status)
    
    def get_by_author(self, author):
        """Get guides by author"""
        return self.model_class.objects.filter(author=author)
    
    def get_by_type(self, guide_type):
        """Get guides by type"""
        return self.model_class.objects.filter(guide_type=guide_type)
    
    def get_pending_count(self):
        """Get count of pending guides"""
        return self.model_class.objects.filter(status='pending').count()
    
    def save(self, guide):
        """Save a guide instance"""
        guide.save()
        return guide