from django.urls import path
from . import views
from django.http import HttpResponseNotFound
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.shortcuts import redirect

def favicon_view(request):
    return HttpResponseNotFound("Favicon no encontrado")

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
    # TODO: ACABAR DE IMPLEMENTAR RUTAS PARA FORO CON FILTROS (EDAD ...) CORRECTAMENTE
    path('parents-forum/', views.parents_forum_page, name='parents_forum'),
    path('parents-forum/<int:pk>/', views.parents_forum_details, name='parents_forum_details'),

    path('parents-forum/add-forum/', views.ParentsForum_Add_View.as_view(), name='add_forum'),
    path('parents-forum/<int:pk>/update-forum/', views.ParentsForum_Update_View.as_view(), name='update_forum'),
    path('parents-forum/<int:pk>/delete-forum/', views.ParentsForum_Delete_View.as_view(), name='delete_forum'),


    # RUTA PARA GUIDES (LAS GUIAS LAS ESCRIBE, ELIMINA Y EDITA EL ADMIN)
    # TODO: ACABAR DE IMPLEMENTAR RUTAS PARA GUIDES CON FILTROS (EDAD ...) CORRECTAMENTE
    path('guides/', views.guides_page, name='guides'),

    path('guides/parents-guides/', views.parents_guides_page, name='parents_guides'),
    path('guides/parents-guides/<int:pk>/', views.parent_guide_details, name='parents_guide_details'),

    path('guides/nutrition-guides/', views.nutrition_guides_page, name='nutrition_guides'),
    path('guides/nutrition-guides/<int:pk>/', views.nutrition_guide_details, name='nutrition_guide_details'),
    
    # RUTA PARA LA PAGINA DE INFO REQUEST
    path('info-request/', views.InfoRequestCreate.as_view(), name='info_request'),  # FUNCIONA

    # RUTA ABOUT
    path('about/', views.about, name='about'), # FUNCIONA

   # RUTAS PARA LOGIN Y REGISTRO
    path('login/', views.Login_View.as_view(), name='login'), # FUNCIONA
    path('register/', views.Register_View.as_view(), name='register'), # FUNCIONA
    path('logout/', views.Logout_View.as_view(), name='logout'),
    
    # OTRAS RUTAS
    path('favicon.ico', favicon_view), # FUNCIONA
]