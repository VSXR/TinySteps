from .guide_service import Guide_Service

class ParentGuide_Service(Guide_Service):
    """Parent-specific guide service"""
    
    def __init__(self):
        super().__init__('parent')
    
    def get_template_path(self, view_type):
        templates = {
            'list': 'guides/parents/list.html',
            'detail': 'guides/parents/detail.html',
            'articles': 'guides/parents/articles.html',
            'article_detail': 'guides/parents/article_detail.html',
        }
        return templates.get(view_type)
    
    def get_context_data(self, base_context, request=None):
        context = super().get_context_data(base_context, request)
        
        # Add parent-specific context
        if request and base_context.get('view_type') == 'list':
            latest_articles = self.get_articles(3)
            context.update({
                'latest_articles': latest_articles
            })
        
        return context