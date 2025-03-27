from django.urls import path

class AdminUrl_Factory:
    @staticmethod
    def create_urls():
        """Create URL patterns for admin-related views"""
        from tinySteps.views.admin import admin_views
        
        return [
            path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
            path('admin/guides/review/', admin_views.review_guides, name='review_guides'),
            path('admin/guides/approve/<int:guide_id>/', admin_views.approve_guide, name='approve_guide'),
            path('admin/guides/reject/<int:guide_id>/', admin_views.reject_guide, name='reject_guide'),

        ]