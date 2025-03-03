from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('tinySteps.urls')),
    path('api/', include('api.urls')),
    path("admin/", admin.site.urls),
]

handler404 = 'tinySteps.views.page_not_found'
