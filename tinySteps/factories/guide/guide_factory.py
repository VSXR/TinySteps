from django.urls import path
from tinySteps.registry import GuideType_Registry

class GuideService_Factory:
    @staticmethod
    def create_service(guide_type):
        """Create a guide service instance for the given type"""
        service_class = GuideType_Registry.get_service_class(guide_type)
        if not service_class:
            raise ValueError(f"Unsupported guide type: {guide_type}")
        return service_class()

class GuideUrl_Factory:
    @staticmethod
    def create_urls(guide_type):
        """Create URL patterns for a guide section"""
        from tinySteps.views.guides import (
            guide_views, article_views, submission_views
        )
        from tinySteps.views.guides.guide_views import guides_page
        from tinySteps.views.nutrition import (
            analyzer_views, comparison_views
        )
        
        url_patterns = []
        
        # To avoid circular import issues, we import the views here!
        if guide_type == 'parent':
            url_patterns.append(path('guides/', guides_page, name='guides'))
        
        # These are the core URL patterns for each guide type
        url_patterns.extend([
            # Guide list view
            path(f'guides/{guide_type}/', 
                guide_views.guide_list_view, 
                {'guide_type': guide_type}, 
                name=f'{guide_type}_guides'),
            
            # Guide detail view
            path(f'guides/{guide_type}/<int:pk>/', 
                guide_views.guide_detail_view, 
                {'guide_type': guide_type}, 
                name=f'{guide_type}_guide_details'),
            
            # Article list view
            path(f'guides/{guide_type}/articles/', 
                article_views.article_list_view, 
                {'guide_type': guide_type}, 
                name=f'{guide_type}_articles'),
            
            # Article detail view - using guide_type for the URL name
            path(f'guides/{guide_type}/articles/<int:article_id>/', 
                article_views.article_detail_view, 
                {'guide_type': guide_type, 'category': guide_type}, 
                name=f'{guide_type}_article_details'),
        ])
        
        # Special cases for parent guide type
        if guide_type == 'parent':
            url_patterns.extend([
                path('guides/submit/', submission_views.submit_guide, name='submit_guide'),
                path('guides/my-guides/', guide_views.my_guides_view, name='my_guides'),
            ])
        
        # Special cases for nutrition guide type
        if guide_type == 'nutrition':
            url_patterns.extend([
                path('nutrition/analyzer/', analyzer_views.nutrition_analyzer_view, name='nutrition_analyzer'),
                path('nutrition/comparison/', comparison_views.nutrition_comparison_view, name='nutrition_comparison'),
                path('nutrition/save/', analyzer_views.nutrition_save_view, name='nutrition_save'),
            ])
        
        return url_patterns