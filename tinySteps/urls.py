import time
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseNotFound
from django.urls import path
from django.db import connections
from django.http import JsonResponse

from tinySteps.views.base import home_views 
from tinySteps.factories import (
    GuideUrl_Factory, CommentUrl_Factory, AuthUrl_Factory, 
    ChildUrl_Factory, ForumUrl_Factory, AdminUrl_Factory,
    ContactUrl_Factory, NutritionUrl_Factory
)

# -----------------------------------------------
# -- TESTING VIEWS (FOR DEVELOPMENT)
# -----------------------------------------------
def db_connection_test(_request):
    start_time = time.time()
    try:
        # Testing for the database connectivity (error 500 if fails!)
        with connections['default'].cursor() as cursor:
            cursor.execute('SELECT 1')
            result = cursor.fetchone()[0]
        
        response_time = time.time() - start_time
        return JsonResponse({
            'status': 'success',
            'message': 'Database connection successful',
            'response_time': f'{response_time:.4f}s',
            'result': result
        })
    except Exception as e:
        response_time = time.time() - start_time
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'response_time': f'{response_time:.4f}s',
            'error_type': type(e).__name__,
        }, status=500)

def favicon_view(_request):
    return HttpResponseNotFound()

# Main site URLs
urlpatterns = [
    # Home and common pages
    path('', home_views.index, name='index'),
    path('about/', home_views.about, name='about'),
    path('favicon.ico', favicon_view),
    path('db-test/', db_connection_test, name='db_test'),
    
    # Auth URLs
    *AuthUrl_Factory.create_urls(),
    
    # Child management
    *ChildUrl_Factory.create_urls(),
    
    # Guide URLs
    *GuideUrl_Factory.create_urls('parent'),
    *GuideUrl_Factory.create_urls('nutrition'),
    
    # Nutrition specific URLs (beyond guides)
    *NutritionUrl_Factory.create_urls(),
    
    # Forum URLs
    *ForumUrl_Factory.create_urls(),
    
    # Comment system
    *CommentUrl_Factory.create_urls(),
    
    # Admin functionality
    *AdminUrl_Factory.create_urls(),
    
    # Contact
    *ContactUrl_Factory.create_urls(),
]

# Static media for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)