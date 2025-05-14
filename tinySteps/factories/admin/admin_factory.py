from django.urls import path

class AdminUrl_Factory:
    """Factory class for creating admin-related URLs"""
        
    @staticmethod
    def create_urls():
        """Create all admin-related URLs"""
        return [
            *AdminUrl_Factory._create_dashboard_urls(),
            *AdminUrl_Factory._create_guide_management_urls(),
        ]
    
    @staticmethod
    def _create_dashboard_urls():
        """Create URLs for the admin dashboard"""
        from tinySteps.views.admin import admin_views
        
        return [
            path('staff/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
        ]
    
    @staticmethod
    def _create_guide_management_urls():
        """Create URLs for guide management"""
        from tinySteps.views.admin import moderation_views 
        
        return [
            # Main guides panel - direct reference to moderation_views
            path('guides/admin-guides-panel/', 
                 moderation_views.review_guides, 
                 name='admin_guides_panel'),
            
            # Review guides list - same view as above for consistency
            path('guides/review/', 
                 moderation_views.review_guides, 
                 name='review_guides'),
            
            # Individual guide review
            path('guides/review/<int:guide_id>/', 
                 moderation_views.review_guide, 
                 name='review_guide'),
            
            # Guide approval action
            path('guides/<int:guide_id>/approve/', 
                 moderation_views.approve_guide, 
                 name='approve_guide'),
                 
            # Guide rejection action
            path('guides/<int:guide_id>/reject/', 
                 moderation_views.reject_guide, 
                 name='reject_guide'),
        ]