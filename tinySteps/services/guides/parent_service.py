from .base_service import Guide_Service
from tinySteps.models import ParentsGuides_Model, Category_Model
from django.db.models import Count, Q
from tinySteps.services.guides.category_service import Category_Service

class ParentGuide_Service(Guide_Service):
    """Parent-specific guide service"""
    
    def __init__(self):
        super().__init__('parent')
        self.category_service = Category_Service()
    
    def get_template_path(self, view_type):
        """Get the template path for the given view type"""
        templates = {
            'list': 'guides/parents/list.html',
            'detail': 'guides/parents/detail.html',
            'articles': 'guides/parents/articles.html',
            'article_detail': 'guides/parents/article_detail.html',
        }
        return templates.get(view_type)
    
    def get_recent_guides(self, limit=3, count=None):
        """Get recent parent guides"""
        if count is not None:
            limit = count
        
        return self.repository.get_guides_by_type(
            self.guide_type,
            status='approved',
            count=limit
        )
    
    def get_context_data(self, base_context, request=None):
        """Enhance the context data with additional information"""
        context = super().get_context_data(base_context, request)
        
        if base_context.get('view_type') == 'article_list':
            categories = self._get_guide_categories()
            context.update({
                'categories': categories,
                'total_count': ParentsGuides_Model.objects.filter(
                    guide_type='parent',
                    status='approved'
                ).count()
            })
            
            if request and request.GET.get('category'):
                try:
                    category_id = int(request.GET.get('category'))
                    current_category = self.category_service.get_category_by_id(category_id)
                    context['current_category'] = current_category
                except (ValueError, TypeError):
                    pass
        
        if base_context.get('view_type') == 'list':
            latest_articles = self.get_articles(3)
            context.update({
                'latest_articles': latest_articles
            })
        
        if base_context.get('view_type') == 'article_detail' and base_context.get('article'):
            article = base_context.get('article')
            related_articles = self._get_related_articles(article)
            context.update({
                'related_articles': related_articles
            })
        
        return context
    
    def _get_guide_categories(self):
        """Helper method to get guide categories with counts"""
        return self.category_service.get_guide_categories(guide_type='parent')

    def get_articles(self, limit=None, category_id=None):
        """Obtener artículos con posible filtro de categoría"""
        query = ParentsGuides_Model.objects.filter(
            guide_type='parent',
            status='approved'
        ).select_related('author').order_by('-created_at')
        
        if category_id:
            try:
                category_id = int(category_id)
                category = Category_Model.objects.get(id=category_id)
                query = query.filter(tags__icontains=category.name)
            except (ValueError, Category_Model.DoesNotExist):
                pass
        
        if limit:
            query = query[:limit]
            
        return query

    def search_articles(self, query, category=None):
        """Search parenting guides"""
        from django.db.models import Q
        
        guides = ParentsGuides_Model.objects.filter(
            Q(title__icontains=query) | 
            Q(desc__icontains=query),
            guide_type='parent',
            status='approved'
        )
        
        if category:
            try:
                category_id = int(category)
                guides = guides.filter(category_id=category_id)
            except (ValueError, TypeError):
                guides = guides.filter(category__name__icontains=category)
        
        return guides.order_by('-created_at')
    
    def get_popular_articles(self, limit=3):
        """Obtener artículos populares para padres"""
        guides = ParentsGuides_Model.objects.filter(
            guide_type='parent', 
            status='approved'
        ).order_by('-published_at', '-created_at')[:limit]
        
        if not guides.exists():
            guides = ParentsGuides_Model.objects.filter(
                guide_type='parent',
                status='approved'
            ).order_by('-created_at')[:limit]
        
        return guides
    
    def get_article_detail(self, article_id):
        """Obtener detalles de un artículo específico por ID"""
        try:
            article_id = int(article_id)
            guide = ParentsGuides_Model.objects.filter(
                id=article_id,
                guide_type='parent',
                status='approved'
            ).select_related('author').first()
            return guide
        except (ValueError, TypeError):
            return None
    
    def _get_related_articles(self, article, limit=3):
        """Obtener artículos relacionados basados en tags o categoría"""
        if not article:
            return []
            
        if article.tags:
            related = ParentsGuides_Model.objects.filter(
                guide_type='parent',
                status='approved',
                tags__icontains=article.tags
            ).exclude(id=article.id).order_by('-published_at')[:limit]
            
            if related.count() >= limit:
                return related
        
        return ParentsGuides_Model.objects.filter(
            guide_type='parent',
            status='approved'
        ).exclude(id=article.id).order_by('-published_at')[:limit]
    
    def get_article_comment_count(self, article_id):
        """Obtener el número de comentarios para un artículo"""
        try:
            article_id = int(article_id)
            guide = ParentsGuides_Model.objects.get(
                id=article_id,
                guide_type='parent',
                status='approved'
            )
            return guide.comments.count()
        except (ValueError, TypeError, ParentsGuides_Model.DoesNotExist):
            return 0
