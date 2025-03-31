from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from tinySteps.views.base import home_views
from tinySteps.views.guides import guide_views, submission_views

from tinySteps.factories import (
    GuideUrl_Factory, CommentUrl_Factory, AuthUrl_Factory, 
    ChildUrl_Factory, ForumUrl_Factory, AdminUrl_Factory,
    ContactUrl_Factory, NutritionUrl_Factory
)

# Main URL patterns
urlpatterns = [
    # Home routes
    path('', home_views.index, name='index'),
    path('about/', home_views.about, name='about'),
    
    # Auth routes
    *AuthUrl_Factory.create_urls(),
    
    # Children routes - add prefix here
    path('children/', include((ChildUrl_Factory.create_urls(), 'children'))),
    
    # Forum routes - add prefix here
    path('forum/', include((ForumUrl_Factory.create_urls(), 'forum'))),
    
    # Guide routes - primary URLs
    path('guides/', guide_views.guides_page, name='guides'),
    path('guides/submit/', submission_views.SubmitGuide_View.as_view(), name='submit_guide'),
    path('guides/my-guides/', guide_views.my_guides_view, name='my_guides'),
    
    # Guide type-specific routes
    *GuideUrl_Factory.create_urls('parent'),
    *GuideUrl_Factory.create_urls('nutrition'),
    
    # Nutrition tools
    *NutritionUrl_Factory.create_urls(),
    
    # Comment routes
    path('comments/', include((CommentUrl_Factory.create_urls(), 'comments'))),  
      
    # Admin routes
    *AdminUrl_Factory.create_urls(),
    
    # Contact routes
    *ContactUrl_Factory.create_urls(),
]

# Media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler400 = 'tinySteps.views.base.error_views.custom_error_400'
handler403 = 'tinySteps.views.base.error_views.custom_error_403'
handler404 = 'tinySteps.views.base.error_views.custom_error_404'
handler500 = 'tinySteps.views.base.error_views.custom_error_500'