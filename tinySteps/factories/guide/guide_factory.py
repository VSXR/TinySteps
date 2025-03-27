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
        from tinySteps.views.nutrition import (
            analyzer_views, comparison_views
        )
        
        url_patterns = [
            path(f'guides/{guide_type}/', guide_views.guide_list_view, {'guide_type': guide_type}, 
                name=f'{guide_type}_guides'),
            path(f'guides/{guide_type}/<int:pk>/', guide_views.guide_detail_view, {'guide_type': guide_type}, 
                name=f'{guide_type}_guide_detail'),
            path(f'guides/{guide_type}/articles/', article_views.article_list_view, {'guide_type': guide_type}, 
                name=f'{guide_type}_articles'),
            path(f'guides/{guide_type}/articles/<slug:slug>/', article_views.article_detail_view, {'guide_type': guide_type}, 
                name=f'{guide_type}_article_detail'),
            path(f'guides/submit/', submission_views.submit_guide, name='submit_guide'),
            path(f'guides/my-guides/', guide_views.my_guides, name='my_guides'),
        ]
        
        # Special cases for specific types
        if guide_type == 'nutrition':
            url_patterns.extend([
                path('nutrition/analyzer/', analyzer_views.nutrition_analyzer_view, name='nutrition_analyzer'),
                path('nutrition/comparison/', comparison_views.nutrition_comparison_view, name='nutrition_comparison'),
                path('nutrition/save/', analyzer_views.nutrition_save_view, name='nutrition_save'),
            ])
            
        return url_patterns