from django.urls import path

class GuideService_Factory:
    @staticmethod
    def create_service(guide_type):
        """Create a guide service instance for the given type"""
        from tinySteps.registry import GuideType_Registry
        service_class = GuideType_Registry.get_service_class(guide_type)
        if not service_class:
            raise ValueError(f"No service class registered for guide type: {guide_type}")
        
        return service_class()


class GuideUrl_Factory:
    """Factory class for creating guide-related URL patterns"""
    
    @staticmethod
    def create_urls(guide_type):
        """Create URL patterns for a guide section"""
        from tinySteps.views.guides import (
            guide_views, article_views, submission_views
        )
        
        url_patterns = [
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
            
            path(f'guides/{guide_type}/submit/', 
                submission_views.SubmitGuide_View.as_view(), 
                {'guide_type': guide_type}, 
                name=f'submit_{guide_type}_guide'),
        ]
        
        if hasattr(article_views, f'{guide_type}_article_list'):
            url_patterns.append(
                path(f'guides/{guide_type}/articles/', 
                    getattr(article_views, f'{guide_type}_article_list'), 
                    name=f'{guide_type}_articles')
            )
            
            url_patterns.append(
                path(f'guides/{guide_type}/articles/<int:pk>/', 
                    getattr(article_views, f'{guide_type}_article_detail'), 
                    name=f'{guide_type}_article_details')
            )
        else:
            url_patterns.extend([
                path(f'guides/{guide_type}/articles/', 
                    article_views.article_list_view, 
                    {'guide_type': guide_type}, 
                    name=f'{guide_type}_articles'),
                    
                path(f'guides/{guide_type}/articles/<int:pk>/', 
                    article_views.article_detail_view, 
                    {'guide_type': guide_type}, 
                    name=f'{guide_type}_article_details'),
            ])
        
        return url_patterns