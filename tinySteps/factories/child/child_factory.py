from django.urls import path, include

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
        
        # Define URL patterns WITHOUT the children/ prefix
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
        ]
        
        return urlpatterns