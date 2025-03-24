from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Guides_Model, ExternalArticle_Model, ParentsForum_Model

class Guide_Repository:    
    @staticmethod
    def get_guides_by_type(guide_type, count=None):
        """Get guides by type with optional count limit"""
        query = Guides_Model.objects.filter(guide_type=guide_type).order_by('-created_at')
        
        if count:
            query = query[:count]
            
        return query
    
    @staticmethod
    def get_related_guides(guide, limit=3):
        """Get related guides based on guide type"""
        return Guides_Model.objects.filter(
            guide_type=guide.guide_type
        ).exclude(id=guide.id).order_by('-created_at')[:limit]

class Article_Repository:
    """Repository class for articles"""
    
    @staticmethod
    def get_articles_by_category(category, limit=None):
        """Get articles by category with optional limit"""
        query = ExternalArticle_Model.objects.filter(
            category=category
        ).order_by('-published_at')
        
        if limit:
            query = query[:limit]
            
        return query
    
    @staticmethod
    def get_article_by_id(article_id):
        """Get a specific article by ID"""
        return get_object_or_404(ExternalArticle_Model, pk=article_id)
    
    @staticmethod
    def search_articles(query, category=None):
        """Search articles by query string and optional category"""
        search_query = Q(title__icontains=query) | Q(description__icontains=query)
        
        if category:
            search_query &= Q(category=category)
        
        return ExternalArticle_Model.objects.filter(search_query).order_by('-published_at')
    
    @staticmethod
    def get_recent_articles(limit=5):
        """Get recent articles"""
        return ExternalArticle_Model.objects.all().order_by('-published_at')[:limit]
    
    @staticmethod
    def get_related_articles(article_id, limit=3):
        """Get related articles"""
        article = Article_Repository.get_article_by_id(article_id)
        return Article_Repository.get_articles_by_category(article.category, limit=limit)

class Forum_Repository:
    """Repository class for forum posts implementing the Dependency Inversion Principle"""
    
    @staticmethod
    def get_latest_posts(limit=5):
        """Get the latest forum posts"""
        return ParentsForum_Model.objects.all().order_by('-created_at')[:limit]
    
    @staticmethod
    def get_post_by_id(post_id):
        """Get a specific forum post by ID"""
        return get_object_or_404(ParentsForum_Model, pk=post_id)
    
    @staticmethod
    def search_posts(query):
        """Search forum posts by query string"""
        search_query = Q(title__icontains=query) | Q(content__icontains=query)
        return ParentsForum_Model.objects.filter(search_query).order_by('-created_at')
    
    @staticmethod
    def get_user_posts(user_id):
        """Get forum posts by a specific user"""
        return ParentsForum_Model.objects.filter(author_id=user_id).order_by('-created_at')
    
    @staticmethod
    def get_user_post_count(user_id):
        """Get the number of forum posts by a specific user"""
        return ParentsForum_Model.objects.filter(author_id=user_id).count()