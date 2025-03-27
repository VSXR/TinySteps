from django.urls import path

class ContactUrl_Factory:
    @staticmethod
    def create_urls():
        """Create URL patterns for contact-related views"""
        from tinySteps.views.contact import contact_views
        
        return [
            path('contact/', contact_views.Contact_View.as_view(), name='contact'),
            path('contact/success/', contact_views.contact_success, name='contact_success'),
        ]