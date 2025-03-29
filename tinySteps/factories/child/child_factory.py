from django.urls import path

class ChildUrl_Factory:
    @staticmethod
    def create_urls():
        """Create URL patterns for child management views"""
        from tinySteps.views.child import core_views, feature_views, form_views
        
        return [
            # Core child views
            path('children/', core_views.your_children, name='your_children'),
            path('children/<int:child_id>/', core_views.your_child, name='child_detail'),
            
            # Child forms
            path('children/add/', form_views.YourChild_Add_View.as_view(), name='add_child'),
            path('children/<int:child_id>/edit/', form_views.YourChild_UpdateDetails_View.as_view(), name='edit_child'),
            path('children/<int:child_id>/delete/', form_views.YourChild_Delete_View.as_view(), name='delete_child'),
            
            # Features
            path('children/<int:child_id>/calendar/', feature_views.child_calendar, name='child_calendar'),
            path('children/<int:child_id>/vaccines/', feature_views.child_vaccine_card, name='child_vaccines'),
            path('children/<int:child_id>/milestones/', feature_views.child_milestone, name='child_milestones'),
        ]