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
        from tinySteps.views.admin import admin_views
        
        return [
            path('guides/admin-guides-panel/', 
                 admin_views.admin_guides_panel_view, 
                 name='admin_guides_panel'),
            
            # LIST OF GUIDES
            path('guides/review/', 
                 admin_views.review_guides, 
                 name='review_guides'),
            
            # INDIVIDUAL GUIDE
            path('guides/review/<int:guide_id>/', 
                 admin_views.review_guide, 
                 name='review_guide'),
            
            # GUIDE APPROVAL
            path('guides/<int:guide_id>/approve/', 
                 admin_views.approve_guide, 
                 name='approve_guide'),
                 
            # GUIDE REJECTION
            path('guides/<int:guide_id>/reject/', 
                 admin_views.reject_guide, 
                 name='reject_guide'),
        ]