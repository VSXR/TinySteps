from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static

handler_404 = 'tinySteps.urls.page_404'

# URLs SIN prefijo de idioma
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Necesario para el selector de idiomas
    path('api/', include('api.urls')),  # APIs normalmente no necesitan prefijo de idioma
]

# URLs CON prefijo de idioma (como /es/admin/, /en/contact/)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('tinySteps.urls')),
    prefix_default_language=False  # False = el idioma por defecto no tiene prefijo
)

# Configuración de URLs para archivos estáticos y media
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)