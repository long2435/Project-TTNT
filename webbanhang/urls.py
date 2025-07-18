"""
URL configuration for webbanhang project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include

# Load image
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Chỉ thêm media URL khi đang ở chế độ DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
