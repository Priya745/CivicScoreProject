"""
URL configuration for civicscore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


# Customize admin interface look and feel
admin.site.site_header = "CivicScore Administration"
admin.site.site_title = "CivicScore Admin"
admin.site.index_title = "Manage Activities & Civic Scores"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('activities/', include('apps.activities.urls')),
    path('reports/', include('apps.reports.urls')),
    path('leaderboard/', include('apps.leaderboard.urls')),
    path('', include('apps.core.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)