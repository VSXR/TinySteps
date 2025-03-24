from ..repositories import Guide_Repository, Article_Repository
from ..models import Guides_Model

class GuideContext_Service:
    """Service for providing guide context data following DIP"""
    
    def __init__(self):
        """Initialize repositories"""
        self.guide_repository = Guide_Repository()
        self.article_repository = Article_Repository()
    
    def get_guides_page_context(self):
        """Get context data for guides page"""
        return {
            'nutrition_guides': self.guide_repository.get_guides_by_type('nutrition', count=3),  # Changed limit to count
            'parent_guides': self.guide_repository.get_guides_by_type('parent', count=3),  # Changed limit to count
            'nutrition_articles': self.article_repository.get_articles_by_category('nutrition', limit=3),
            'parent_articles': self.article_repository.get_articles_by_category('parenting', limit=3),
        }
    
    def get_index_page_context(self):
        """Get context data for index page"""
        return {
            'nutrition_guides': self.guide_repository.get_guides_by_type('nutrition', count=3),  # Changed limit to count
            'parent_guides': self.guide_repository.get_guides_by_type('parent', count=3),  # Changed limit to count
            'nutrition_articles': self.article_repository.get_articles_by_category('nutrition', limit=3),
            'parent_articles': self.article_repository.get_articles_by_category('parenting', limit=3),
        }
    
    def get_guide_context(self, guide_id):
        """Get context data for a specific guide"""
        guide = Guides_Model.objects.get(id=guide_id)
        related_guides = self.guide_repository.get_related_guides(guide)
        
        return {
            'guide': guide,
            'related_guides': related_guides,
        }
    
    def get_articles_context(self, category, limit=5):
        """Get context data for articles of a specific category"""
        articles = self.article_repository.get_articles_by_category(category, limit=limit)
        
        return {
            'articles': articles,
            'category': category,
        }