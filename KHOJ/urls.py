"""
KHOJ - Main URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('family/', include('family.urls')),
    path('hospital/', include('hospital.urls')),
    path('police/', include('police.urls')),
    path('matching/', include('matching.urls')),
    path('notifications/', include('notifications.urls')),
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
