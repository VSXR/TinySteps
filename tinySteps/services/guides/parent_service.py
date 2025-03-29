from .base_service import Guide_Service

class ParentGuide_Service(Guide_Service):
    """Parent-specific guide service"""
    
    def __init__(self):
        super().__init__('parent')
    
    def get_template_path(self, view_type):
        """Get the template path for the given view type"""
        templates = {
            'list': 'guides/parents/list.html',
            'detail': 'guides/parents/detail.html',
            'articles': 'guides/parents/articles.html',
            'article_detail': 'guides/parents/article_detail.html',
        }
        return templates.get(view_type)
    
    def get_recent_guides(self, limit=3):
        """Get recent parent guides"""
        return self.repository.get_guides_by_type(
            self.guide_type,
            count=limit
        )
    
    def get_context_data(self, base_context, request=None):
        """Enhance the context data with additional information"""
        context = super().get_context_data(base_context, request)
        
        if request and base_context.get('view_type') == 'list':
            latest_articles = self.get_articles(3)
            context.update({
                'latest_articles': latest_articles
            })
        
        return context