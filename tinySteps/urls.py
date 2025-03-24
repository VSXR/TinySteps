from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseNotFound
from django.urls import path, include
import time
from django.db import connections
from django.http import JsonResponse
from . import views
from .factories import GuideUrl_Factory

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
    return HttpResponseNotFound("Favicon no encontrado")

# Main site URLs
urlpatterns = [
    # HOME
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    
    # USER MANAGEMENT
    path('login/', views.Login_View.as_view(), name='login'),
    path('register/', views.Register_View.as_view(), name='register'),
    path('logout/', views.Logout_View.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password/reset/', views.password_reset, name='password_reset'),

    # CHILDREN MANAGEMENT
    path('your-children/', views.your_children, name='your_children'),
    path('your-children/<int:pk>/', views.your_child, name='child_details'),
    path('your-children/<int:child_id>/add-milestone/', views.child_milestone, name='child_milestone'),    
    path('your-children/add/', views.YourChild_Add_View.as_view(), name='add_child'),
    path('your-children/<int:pk>/update/', views.YourChild_UpdateDetails_View.as_view(), name='child_update'),
    path('your-children/<int:pk>/delete/', views.YourChild_Delete_View.as_view(), name='child_delete'),
    path('your-children/<int:pk>/needs/calendar/', views.YourChild_Calendar_View.as_view(), name='child_calendar'),
    path('your-children/<int:pk>/needs/vaccine-card/', views.YourChild_VaccineCard_View.as_view(), name='child_vaccine_card'),
    
    # FORUM
    path('parents-forum/', views.parents_forum_page, name='parents_forum'),
    path('parents-forum/search/', views.parents_forum_page, name='search_posts'),
    path('parents-forum/posts/add/', views.add_post, name='add_post'),
    path('parents-forum/posts/<int:post_id>/', views.view_post, name='view_post'),
    path('parents-forum/posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('parents-forum/posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('parents-forum/posts/<int:post_id>/comment/', views.add_post_comment, name='add_post_comment'),
    path('parents-forum/posts/<int:post_id>/like/', views.forum_post_like_toggle, name='forum_post_like_toggle'),
        
    # GUIDES
    path('guides/', views.guides_page, name='guides'),
    path('guides/my-guides/', views.my_guides, name='my_guides'),
    path('guides/submit/', views.SubmitGuide_View.as_view(), name='submit_guide'),
    
    # Review guides (admin only)
    path('guides/review/', views.review_guides, name='review_guides'),
    path('guides/approve/<int:pk>/', views.approve_guide, name='approve_guide'),
    path('guides/reject/<int:pk>/', views.reject_guide, name='reject_guide'),
    
    # Guide sections (nutrition & parent)
    *GuideUrl_Factory.create_urls('nutrition'),
    *GuideUrl_Factory.create_urls('parent'),

    # CONTACT
    path('contact/', views.Contact_View.as_view(), name='contact'),
    
    # ERROR PAGES
    path('page-404/', views.page_not_found, name='page_404'),
    path('favicon.ico', favicon_view),
    
    # INTERNATIONALIZATION
    path('i18n/', include('django.conf.urls.i18n')),

    # TESTING
    path('db-test/', db_connection_test, name='db_test'),
]

# Static/media files configuration for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)