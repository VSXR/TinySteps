from django.urls import path

class PagesUrl_Factory:
    @staticmethod
    def create_urls():
        """Create URL patterns for static pages and policies"""
        from tinySteps.views.pages import pages_views
        
        return [
            # Policy pages
            path('terms/', pages_views.terms_view, name='terms'),
            path('privacy/', pages_views.privacy_view, name='privacy'),
            path('cookies/', pages_views.cookies_view, name='cookies'),
            path('accessibility/', pages_views.accessibility_view, name='accessibility'),
            path('help-center/', pages_views.help_center_view, name='help_center'),
        ]