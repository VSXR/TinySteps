from django.shortcuts import get_object_or_404
from django.db.models import Q
from tinySteps.models import ParentsForum_Model
from tinySteps.repositories.base.base_repository import GenericRepository

class Forum_Repository(GenericRepository):
    """Repository for forum post-related operations"""
    
    def __init__(self):
        super().__init__(ParentsForum_Model)
    
    def get_latest_posts(self, limit=5):
        """Get the latest forum posts"""
        return self.model.objects.all().order_by('-created_at')[:limit]
    
    def get_post_by_id(self, post_id):
        """Get a specific forum post by ID"""
        return get_object_or_404(self.model, pk=post_id)
    
    def search_posts(self, query_string, category=None):
        """Search forum posts by query string and optional category"""
        search_query = Q(title__icontains=query_string) | Q(desc__icontains=query_string)
        
        if category:
            search_query &= Q(category=category)
        
        return self.model.objects.filter(search_query).order_by('-created_at')
    
    def get_posts_by_category(self, category, limit=None):
        """Get forum posts by category with optional limit"""
        query = self.model.objects.filter(category=category).order_by('-created_at')
        
        if limit:
            query = query[:limit]
            
        return query
    
    def get_popular_posts(self, days=7, limit=5):
        """Get popular forum posts from the last N days"""
        from django.utils import timezone
        from datetime import timedelta
        
        start_date = timezone.now() - timedelta(days=days)
        
        return self.model.objects.filter(
            created_at__gte=start_date
        ).order_by('-likes')[:limit]
    
    def get_user_posts(self, user_id):
        """Get forum posts by a specific user"""
        return self.model.objects.filter(author_id=user_id).order_by('-created_at')
    
    def get_user_post_count(self, user_id):
        """Get the number of forum posts by a specific user"""
        return self.model.objects.filter(author_id=user_id).count()