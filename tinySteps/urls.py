from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views
from django.http import Http404, HttpResponseNotFound
from django.shortcuts import render
from django.urls import path, include
from . import views

def favicon_view(request):
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
    
    # Parents Guides
    path('guides/parents/articles/', views.parenting_articles, name='parenting_articles'),
    path('guides/parents/articles/<int:article_id>/', views.parenting_article_details, name='parenting_article_details'),
    path('guides/parents/', views.parents_guides_page, name='parents_guides'),
    path('guides/parents/<int:pk>/', views.parent_guide_details, name='parents_guide_details'),

    # Nutrition Guides
    path('guides/nutrition/analyzer/', views.nutrition_analyzer, name='nutrition_analyzer'),
    path('guides/nutrition/articles/', views.nutrition_articles, name='nutrition_articles'),
    path('guides/nutrition/articles/<int:article_id>/', views.nutrition_article_details, name='nutrition_article_details'),
    path('guides/nutrition/', views.nutrition_guides_page, name='nutrition_guides'),  # URL más general al final
    path('guides/nutrition/<int:pk>/', views.nutrition_guide_details, name='nutrition_guide_details'),

    # CONTACT
    path('contact/', views.Contact_View.as_view(), name='contact'),
    
    # ERROR PAGES
    path('page-404/', views.page_not_found, name='page_404'),
    path('favicon.ico', favicon_view),
    
    # INTERNATIONALIZATION
    path('i18n/', include('django.conf.urls.i18n')),
]

# Static/media files configuration for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
