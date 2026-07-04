"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.views.generic import TemplateView
from users.views import DeleteAccountWebView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('privacy-policy/', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    path('delete-account/', DeleteAccountWebView.as_view(), name='delete_account'),
    # Default django admin (You can remove this if you strictly don't want it accessible at all)
    path('django-admin/', admin.site.urls),

    # API endpoints for our custom apps
    path('api/users/', include('users.urls')),
    path('api/learning/', include('learning.urls')),



    path('custom-admin/login/', TemplateView.as_view(
        template_name='admin_panel/login.html'), name='custom-admin-login'),
    path('custom-admin/dashboard/', TemplateView.as_view(
        template_name='admin_panel/dashboard.html'), name='custom-admin-dashboard'),
    path('custom-admin/domains/', TemplateView.as_view(
        template_name='admin_panel/domains.html'), name='custom-admin-domains'),
    path('custom-admin/courses/', TemplateView.as_view(
        template_name='admin_panel/courses.html'), name='custom-admin-courses'),
    path('custom-admin/subcourses/', TemplateView.as_view(
        template_name='admin_panel/subcourses.html'), name='custom-admin-subcourses'),
    path('custom-admin/flashcards/', TemplateView.as_view(
        template_name='admin_panel/flashcards.html'), name='custom-admin-flashcards'),
    path('custom-admin/mcqs/', TemplateView.as_view(
        template_name='admin_panel/mcqs.html'), name='custom-admin-mcqs'),
    path('custom-admin/users/', TemplateView.as_view(
        template_name='admin_panel/users.html'), name='custom-admin-users'),

    path('teacher-panel/login/', TemplateView.as_view(
        template_name='teacher_panel/login.html'), name='teacher-panel-login'),
    path('teacher-panel/dashboard/', TemplateView.as_view(
        template_name='teacher_panel/dashboard.html'), name='teacher-panel-dashboard'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
