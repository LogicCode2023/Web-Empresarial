"""
URL configuration for web_empresarial project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import custom_admin_logout, CustomLoginView
from core import views

# Importaciones necesarias para servir archivos multimedia en modo desarrollo
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. Interceptamos el logout del admin primero para que redirija a home
    path('admin/logout/', custom_admin_logout, name='custom_admin_logout'),

    # 2. NUESTRO PANEL PRINCIPAL: Prioridad absoluta para el dashboard personalizado
    path('dashboard/tramites/', views.dashboard_tramites_view, name='dashboard_tramites'),

    # 3. Red de seguridad / Respaldo técnico: Panel nativo de Django (restringido a superusuario)
    path('admin/', admin.site.urls),

    # 4. Rutas principales de la app core
    path('', include('core.urls')),

    # 5. Vistas de autenticación global (Usando la vista inteligente para separar staff de clientes)
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

# Configuración para permitir que Django sirva las imágenes y documentos subidos (MEDIA_URL / MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)