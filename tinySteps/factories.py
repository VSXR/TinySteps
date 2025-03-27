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
        from tinySteps.views import (
            guide_list_view, guide_detail_view, 
            article_list_view, article_detail_view,
            nutrition_analyzer_view, nutrition_comparison_view, 
            nutrition_save_view
        )
        
        url_patterns = [
            path(f'guides/{guide_type}/', guide_list_view, {'guide_type': guide_type}, 
                 name=f'{guide_type}_guides'),
            path(f'guides/{guide_type}/<slug:slug>/', guide_detail_view, {'guide_type': guide_type}, 
                 name=f'{guide_type}_guide_detail'),
            path(f'guides/{guide_type}/articles/', article_list_view, {'guide_type': guide_type}, 
                 name=f'{guide_type}_articles'),
            path(f'guides/{guide_type}/articles/<slug:slug>/', article_detail_view, {'guide_type': guide_type}, 
                 name=f'{guide_type}_article_detail'),
        ]
        
        # Special cases for specific types
        if guide_type == 'nutrition':
            url_patterns.extend([
                path(f'guides/{guide_type}/analyzer/', nutrition_analyzer_view, name=f'{guide_type}_analyzer'),
                path(f'guides/{guide_type}/comparison/', nutrition_comparison_view, name=f'{guide_type}_comparison'),
                path(f'guides/{guide_type}/save/', nutrition_save_view, name=f'{guide_type}_save'),
            ])
            
        return url_patterns

class ForumService_Factory:
    @staticmethod
    def create_service():
        """Create a forum service instance"""
        from tinySteps.services import Forum_Service
        return Forum_Service()