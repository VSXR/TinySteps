from django.shortcuts import get_object_or_404
from django.db.models import Q
from tinySteps.models import ExternalArticle_Model
from tinySteps.repositories.base.base_repository import GenericRepository

class Article_Repository(GenericRepository):
    """Repository for external article-related operations"""
    
    def __init__(self):
        super().__init__(ExternalArticle_Model)
    
    def get_articles_by_category(self, category, limit=None):
        """Get articles by category with optional limit"""
        query = self.model.objects.filter(
            category=category
        ).order_by('-published_at')
        
        if limit:
            query = query[:limit]
            
        return query
    
    def get_article_by_id(self, article_id):
        """Get a specific article by ID"""
        return get_object_or_404(self.model, pk=article_id)
    
    def search_articles(self, query, category=None):
        """Search articles by query string and optional category"""
        search_query = Q(title__icontains=query) | Q(description__icontains=query)
        
        if category:
            search_query &= Q(category=category)
        
        return self.model.objects.filter(search_query).order_by('-published_at')
    
    def get_recent_articles(self, limit=5):
        """Get recent articles"""
        return self.model.objects.all().order_by('-published_at')[:limit]
    
    def get_related_articles(self, article_id, limit=3):
        """Get related articles"""
        article = self.get_article_by_id(article_id)
        return self.get_articles_by_category(article.category, limit=limit)