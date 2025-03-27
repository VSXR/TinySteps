from django.urls import path

class AuthUrl_Factory:
    @staticmethod
    def create_urls():
        """Create URL patterns for authentication-related views"""
        from tinySteps.views.auth import auth_views
        
        return [
            path('accounts/login/', auth_views.Login_View.as_view(), name='login'),            
            path('accounts/logout/', auth_views.Logout_View.as_view(), name='logout'),
            path('accounts/register/', auth_views.Register_View.as_view(), name='register'),
            path('accounts/profile/', auth_views.profile, name='profile'),
            path('accounts/profile/edit/', auth_views.edit_profile, name='edit_profile'),
            path('accounts/password/change/', auth_views.password_reset, name='change_password'),
        ]