from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from tinySteps.views import page_not_found

urlpatterns = [
    path('', include('tinySteps.urls')),
    path('api/', include('api.urls')),
    path("admin/", admin.site.urls),
]

handler404 = 'tinySteps.views.page_not_found'

# Para que Django pueda servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)