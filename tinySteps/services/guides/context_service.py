from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist

from tinySteps.repositories import Guide_Repository, Article_Repository
from tinySteps.models import YourChild_Model
from tinySteps.factories import GuideService_Factory
from tinySteps.utils.helpers.age_helper import calculate_age_in_months
class GuideContext_Service:
    """Service for providing guide context data"""
    
    def __init__(self):
        """Initialize repositories"""
        self.guide_repository = Guide_Repository()
        self.article_repository = Article_Repository()
    
    def get_guides_page_context(self, request=None):
        """Get context data for the main guides page"""
        # Get parent guide service
        parent_service = GuideService_Factory.create_service('parent')
        parent_guides = parent_service.get_recent_guides(count=5)
        
        # Get nutrition guide service
        nutrition_service = GuideService_Factory.create_service('nutrition')
        nutrition_guides = nutrition_service.get_recent_guides(count=5)
        
        context = {
            'recent_guides': parent_guides[:3],
            'parent_guides': parent_guides,
            'nutrition_guides': nutrition_guides,
            'all_parent_guides': self.guide_repository.get_guides_by_type('parent', status='approved'),
            'all_nutrition_guides': self.guide_repository.get_guides_by_type('nutrition', status='approved'),
            'title': _('Parenting and Nutrition Guides'),
            'section': 'guides',
            'show_search': True
        }
        
        # Add personalized recommendations if user is authenticated
        if request and request.user.is_authenticated:
            context.update(self.get_personalized_recommendations(request.user))
        
        return context
    
    def get_personalized_recommendations(self, user):
        """Get personalized guide recommendations based on user's children's ages"""
        try:
            children = YourChild_Model.objects.filter(parent=user)
            if not children.exists():
                return {'baby_age': None, 'recommended_guides': []}
            
            youngest_child = children.order_by('birth_date').first()
            baby_age_months = calculate_age_in_months(youngest_child.birth_date)
            
            # Get age-appropriate recommendations
            parent_guides = self.guide_repository.get_guides_by_age(
                'parent', baby_age_months, count=4
            )
            nutrition_guides = self.guide_repository.get_guides_by_age(
                'nutrition', baby_age_months, count=4
            )
            
            # Combine and sort recommendations
            recommended_guides = list(parent_guides) + list(nutrition_guides)
            recommended_guides.sort(key=lambda x: x.created_at, reverse=True)
            
            return {
                'baby_age': baby_age_months,
                'recommended_guides': recommended_guides[:4]
            }
        except (ObjectDoesNotExist, Exception) as e:
            return {'baby_age': None, 'recommended_guides': []}
    
    def get_index_page_context(self):
        """Get context data for index page"""
        return {
            'nutrition_guides': self.guide_repository.get_guides_by_type('nutrition', status='approved', count=3),
            'parent_guides': self.guide_repository.get_guides_by_type('parent', status='approved', count=3),
            'nutrition_articles': self.article_repository.get_articles_by_category('nutrition', limit=3),
            'parent_articles': self.article_repository.get_articles_by_category('parenting', limit=3),
            'recent_articles': self.article_repository.get_recent_articles(limit=3),
            'show_search': True
        }
    
    def get_guide_context(self, guide_id):
        """Get context data for a specific guide"""
        try:
            guide = self.guide_repository.get_guide_by_id(guide_id)
            if not guide:
                return {'error': _('Guide not found')}
                
            related_guides = self.guide_repository.get_related_guides(guide, count=3)
            comments = self.guide_repository.get_guide_comments(guide_id)
            
            return {
                'guide': guide,
                'related_guides': related_guides,
                'comments': comments,
                'section': 'guides',
                'section_type': guide.guide_type
            }
        except ObjectDoesNotExist:
            return {'error': _('Guide not found')}
        except Exception as e:
            return {'error': _('An error occurred while retrieving the guide')}
    
    def get_articles_context(self, category, limit=5, page=1, query=None):
        """Get context data for articles of a specific category"""
        try:
            if query:
                articles = self.article_repository.search_articles(query, category, limit=limit, page=page)
            else:
                articles = self.article_repository.get_articles_by_category(
                    category, limit=limit, page=page
                )
            
            section_type = 'nutrition' if category == 'nutrition' else 'parent'
            
            return {
                'articles': articles,
                'category': category,
                'section_type': section_type,
                'query': query,
                'show_search': True
            }
        except Exception as e:
            return {
                'articles': [],
                'category': category,
                'error': _('Error retrieving articles')
            }
        
    def get_guide_context_by_type(self, guide_type, query=None, page=1):
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
        
        try:
            # Get guides with optional search filtering
            if query:
                guides = self.guide_repository.search_guides(query, guide_type, page=page)
            else:
                guides = self.guide_repository.get_guides_by_type(
                    guide_type, status='approved', page=page
                )
                
            # We build the context dictionary with the purpose of reusing it in the template
            context = {
                'guides': guides,
                'guide_type': guide_type,
                'guide_type_name': guide_label,
                'alternative_type': alt_type,
                'alternative_name': alt_label,
                'alternative_url': f'/guides/{alt_type}/',
                'page_title': guide_label,
                'show_search': True,
                'query': query,
                'section_type': guide_type
            }
            
            return context
        except Exception as e:
            # In production, log this error
            return {
                'guides': [],
                'guide_type': guide_type,
                'guide_type_name': guide_label,
                'error': _('Error retrieving guides')
            }
    
    def search_guides_and_articles(self, query, limit=10):
        """Search for guides and articles matching the query"""
        try:
            guides = self.guide_repository.search_all_guides(query, limit=limit)
            articles = self.article_repository.search_all_articles(query, limit=limit)
            
            return {
                'guides': guides,
                'articles': articles,
                'query': query,
                'show_search': True
            }
        except Exception as e:
            # In production, log this error
            return {
                'guides': [],
                'articles': [],
                'query': query,
                'error': _('Error performing search')
            }