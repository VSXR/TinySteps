import time
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from tinySteps.repositories import Guide_Repository
from tinySteps.models import Guides_Model, ExternalArticle_Model, Comment_Model, Guides_Model

class Guide_Service:
    """Base service class for guide operations"""
    
    def __init__(self, guide_type):
        self.guide_type = guide_type
        self.repository = Guide_Repository()
    
    # Core guide operations
    def get_guide_listing(self, limit=None, exclude_id=None):
        """Get guides listing with optional filtering"""
        return self.repository.get_guides_by_type(
            self.guide_type, 
            status='approved',
            count=limit, 
            exclude_id=exclude_id
        )
    
    def get_guide_detail(self, guide_id):
        """Get a specific guide with details"""
        return self.repository.get_guide_details(guide_id, self.guide_type)
    
    def create_guide_from_form(self, form, user):
        """Create a guide from form data"""
        guide = Guides_Model(
            title=form.cleaned_data['title'],
            desc=form.cleaned_data['desc'],
            image=form.cleaned_data.get('image'),
            author=user,
            guide_type=self.guide_type,
            slug=f"{slugify(form.cleaned_data['title'])}-{int(time.time())}"
        )
        
        guide.save()
        
        # Handle tags
        tags_text = form.cleaned_data.get('tags', '')
        if tags_text:
            guide.set_tags(tags_text)
            
        return guide
    
    def get_related_guides(self, guide_id, limit=3):
        """Get related guides"""
        return self.repository.get_guides_by_type(
            self.guide_type, 
            exclude_id=guide_id,
            count=limit
        )
    
    # Guide comments
    def get_guide_comments(self, guide_id):
        """Get comments for a guide"""
        content_type = ContentType.objects.get_for_model(Guides_Model)
        return Comment_Model.objects.filter(
            content_type=content_type,
            object_id=guide_id
        ).select_related('author').order_by('-created_at')
    
    # Article operations
    def get_articles(self, limit=None):
        """Get articles related to this guide type"""
        category = 'nutrition' if self.guide_type == 'nutrition' else 'parenting'
        query = ExternalArticle_Model.objects.filter(
            category=category
        ).order_by('-published_at')
        
        if limit:
            query = query[:limit]
        
        return query
    
    def get_article_detail(self, article_id):
        """Get a specific article by ID"""
        category = 'nutrition' if self.guide_type == 'nutrition' else 'parenting'
        return get_object_or_404(
            ExternalArticle_Model,
            id=article_id,
            category=category
        )
    
    # Template and view-related operations
    def get_context_data(self, base_context, request=None):
        """Get context data for templates"""
        base_context['section_type'] = self.guide_type
        return base_context
    
    def get_template_path(self, view_type):
        """Get template path - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement this method")