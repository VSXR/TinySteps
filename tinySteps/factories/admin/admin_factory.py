from django.urls import path

class AdminUrl_Factory:
    @staticmethod
    def create_urls():
        from tinySteps.views.admin import admin_views
        
        url_patterns = [
            # Dashboard
            path('staff/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
            
            # Guide review system
            path('staff/guides/review/', admin_views.review_guides, name='review_guides'),
            path('staff/guides/<int:guide_id>/approve/', admin_views.approve_guide, name='approve_guide'),
            path('staff/guides/<int:guide_id>/reject/', admin_views.reject_guide, name='reject_guide'),
        ]
        
        return url_patterns