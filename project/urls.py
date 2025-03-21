from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.utils.translation import gettext_lazy as _
from tinySteps.views import custom_error_400, custom_error_403, custom_error_404, custom_error_500

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

# Configuración de páginas de error
handler400 = 'tinySteps.views.custom_error_400'  # Bad request (400)
handler403 = 'tinySteps.views.custom_error_403'  # Permission denied (403)
handler404 = 'tinySteps.views.custom_error_404'  # Page not found (404)
handler500 = 'tinySteps.views.custom_error_500'  # Server error (500)
