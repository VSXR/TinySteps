from django.urls import path
from . import views
from django.http import HttpResponseNotFound, Http404
from django.contrib.auth import views as auth_views
from django.shortcuts import render

def favicon_view(request):
    return HttpResponseNotFound("Favicon no encontrado")

def page_404(request):
    raise Http404(request, '404.html', status=404)

def test_404(request):
    return render(request, '404.html')

urlpatterns = [
    # RUTA PARA LA PAGINA PRINCIPAL
    path('', views.index, name='index'), # FUNCIONA

    # RUTA PARA YOUR CHILDREN
    path('your-children/', views.your_children, name='your_children'),
    path('your-children/<int:pk>', views.your_child, name='child_details'),

    path('your-children/add/', views.YourChild_Add_View.as_view(), name='add_child'),
    path('your-children/<int:pk>/update/', views.YourChild_UpdateDetails_View.as_view(), name='child_update'),
    path('your-children/<int:pk>/delete/', views.YourChild_Delete_View.as_view(), name='child_delete'),

    path('your-children/<int:pk>/needs/calendar/', views.YourChild_Calendar_View.as_view(), name='child_calendar'),
    path('your-children/<int:pk>/needs/vaccine-card/', views.YourChild_VaccineCard_View.as_view(), name='child_vaccine_card'),
    
    # RUTA PARA PARENTS FORUM
    path('parents_forum/', views.parents_forum_page, name='parents_forum'),
    path('parents_forum/search/', views.search_posts, name='search_posts'),
    path('parents_forum/posts/add/', views.add_post, name='add_post'),
    path('parents_forum/posts/<int:post_id>/', views.view_post, name='view_post'),
    path('parents_forum/posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('parents_forum/posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('parents_forum/posts/<int:post_id>/comment/', views.add_post_comment, name='add_post_comment'),

    # RUTA PARA GUIDES (LAS GUIAS LAS ESCRIBE, ELIMINA Y EDITA EL ADMIN)
    # TODO: ACABAR DE IMPLEMENTAR RUTAS PARA GUIDES CON FILTROS (EDAD ...) CORRECTAMENTE
    path('guides/', views.guides_page, name='guides'),

    path('guides/parents-guides/', views.parents_guides_page, name='parents_guides'),
    path('guides/parents-guides/<int:pk>/', views.parent_guide_details, name='parents_guide_details'),

    path('guides/nutrition-guides/', views.nutrition_guides_page, name='nutrition_guides'),
    path('guides/nutrition-guides/<int:pk>/', views.nutrition_guide_details, name='nutrition_guide_details'),
    
    # RUTA PARA LA PAGINA DE INFO REQUEST
    path('info-request/', views.InfoRequest_View.as_view(), name='info_request'),  # FUNCIONA

    # RUTA ABOUT
    path('about/', views.about, name='about'), # FUNCIONA

    # RUTAS PARA LOGIN Y REGISTRO
    path('login/', views.Login_View.as_view(), name='login'), # FUNCIONA
    path('register/', views.Register_View.as_view(), name='register'), # FUNCIONA
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'), # FUNCIONA
   
    # Password reset URLs
    path('password/reset/', views.password_reset_request, name='password_reset'),
    path('password/reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password/reset/confirm/<uuid:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password/reset/complete/', views.password_reset_complete, name='password_reset_complete'),

    # OTRAS RUTAS
    path('favicon.ico', favicon_view), # FUNCIONA

    path('page-404/', views.page_not_found, name='page_404'),
    path('test-404/', page_404, name='test_404'),
]