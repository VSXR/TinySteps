from django.utils.translation import gettext as _
from tinySteps.repositories import Guide_Repository, Article_Repository
from tinySteps.models import Guides_Model

class GuideContext_Service:
    """Service for providing guide context data"""
    
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
        
    def get_guide_context_by_type(self, guide_type):
        """Get context data for listing guides of a specific type (parent/nutrition)"""
        # We determine the alternative guide type and label with the purpose of displaying it in the template
        if guide_type == 'parent':
            alt_type = 'nutrition'
            guide_label = _('Parenting Guides')
            alt_label = _('Nutrition Guides')
        else:
            alt_type = 'parent'
            guide_label = _('Nutrition Guides')
            alt_label = _('Parenting Guides')
            
        # We build the context dictionary with the purpose of reusing it in the template
        context = {
            'guide_type': guide_type,
            'guide_type_name': guide_label,
            'alternative_type': alt_type,
            'alternative_name': alt_label,
            'alternative_url': f'/guides/{alt_type}/',
            'page_title': guide_label,
            'show_search': True
        }
        
        return context