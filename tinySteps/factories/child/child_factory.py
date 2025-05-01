from django.urls import path, include
from django.http import JsonResponse

class ChildService_Factory:
    @staticmethod
    def create_service():
        """Create a child service instance"""
        from tinySteps.services.core.child_service import Child_Service
        return Child_Service()

class ChildUrl_Factory:
    @staticmethod
    def create_urls():
        """Create URLs for child-related functionality"""
        from tinySteps.views.child import core_views, feature_views
        from django.contrib.auth.decorators import login_required
        
        # Debug view to check URL routing
        @login_required
        def debug_view(request):
            return JsonResponse({
                'status': 'ok',
                'message': 'Debug endpoint working correctly',
                'user': str(request.user)
            })
        
        urlpatterns = [
            # Child core URLs
            path('', core_views.your_children, name='your_children'),
            path('add/', core_views.add_child, name='add_child'),
            path('<int:child_id>/', core_views.your_child, name='child_detail'),
            path('<int:child_id>/edit/', core_views.edit_child, name='edit_child'),
            path('<int:child_id>/delete/', core_views.delete_child, name='delete_child'),
            
            # Feature-related URLs
            path('<int:child_id>/calendar/', feature_views.child_calendar, name='child_calendar'),
            path('<int:child_id>/milestones/', feature_views.child_milestone, name='child_milestones'),
            path('<int:child_id>/vaccine-card/', feature_views.child_vaccine_card, name='child_vaccine_card'),
            path('<int:child_id>/growth-status/', feature_views.growth_status_view, name='child_growth_status'),

            # Child statistics API
            path('statistics/', feature_views.get_child_statistics, name='child_statistics_api'),
            
            # Debug endpoint
            path('debug/', debug_view, name='debug_endpoint'),
        ]
        
        return urlpatterns