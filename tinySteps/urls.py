from django.urls import path
from .templates import views
from django.http import HttpResponseNotFound
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.shortcuts import redirect

def favicon_view(request):
    return HttpResponseNotFound("Favicon no encontrado")

def custom_logout_view(request):
    messages.success(request, "You have successfully logged out.")
    return redirect('index')

urlpatterns = [
    # RUTA PARA LA PAGINA PRINCIPAL
    path('', views.index, name='index'), # FUNCIONA
    
    # RUTA PARA LA PAGINA DE INFO REQUEST
    path('info_request/', views.InfoRequestCreate.as_view(), name='info_request'),  # FUNCIONA

    # RUTA ABOUT
    path('about/', views.about, name='about'), # FUNCIONA

    # OTRAS RUTAS
    path('favicon.ico', favicon_view), # FUNCIONA

   
    # RUTAS PARA REGISTRO Y LOGIN
    # path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # path('logout/', custom_logout_view, name='logout'),
    # path('register/', views.register, name='register'),
    
]