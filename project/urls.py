from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.utils.translation import gettext_lazy as _

# Debug Toolbar
if settings.DEBUG:
    import debug_toolbar
    debug_patterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
else:
    debug_patterns = []

# URLs SIN prefijo de idioma
urlpatterns = debug_patterns + [
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('api.urls')), 
]

if settings.DEBUG:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls')),
    ]

# URLs CON prefijo de idioma (como /es/admin/, /en/contact/)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('tinySteps.urls')),
    prefix_default_language=False
)

handler400 = 'tinySteps.views.custom_error_400'
handler403 = 'tinySteps.views.custom_error_403'
handler404 = 'tinySteps.views.custom_error_404'
handler500 = 'tinySteps.views.custom_error_500'

# Static and media files for development (only needed in DEBUG mode)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)