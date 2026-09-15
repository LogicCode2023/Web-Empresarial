from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('solicitud/', views.solicitud_busqueda, name='solicitud_busqueda'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('servicios/', views.servicios, name='servicios'),
    path('services/', views.home, name='services'),
    path('contact/', views.home, name='contact'),
    path('cotizar/logistica-internacinal/', views.cotizar_logistica_view, name='cotizar_logistica'),
    path('cotizar/nacionalizacion-aduanas/', views.cotizar_nacionalizacion_view, name='cotizar_nacionalizacion'),
    path('cotizar/inspeccion-origen/', views.cotizar_inspeccion_view, name='cotizar_inspeccion'),
    path('cotizar/transporte-local/', views.cotizar_transporte_local_view, name='cotizar_transporte_local'),
    path('cotizar/asesoria-compras/', views.solicitud_asesoria_view, name='solicitud_asesoria'),
    path('cotizar/representacion-china/', views.solicitud_representacion_view, name='solicitud_representacion'),
    path('servicios/importacion-por-etapas/', views.seleccion_etapas, name='seleccion_etapas'),
    path('tramite/<str:tipo_servicio>/', views.crear_tramite_view, name='crear_tramite'),
    path('tramite/exito/<str:numero_tramite>/', views.exito_tramite_view, name='detalle_tramite_exito'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/tramites/', views.dashboard_tramites_view, name='dashboard_tramites'),
    path('dashboard/tramite/<int:tramite_id>/gestionar/', views.gestionar_tramite_view, name='gestionar_tramite'),
    path('dashboard/aliados/', views.lista_aliados, name='lista_aliados'),
    path('dashboard/aliados/crear/', views.crear_aliado, name='crear_aliado'),
    path('dashboard/aliados/editar/<int:pk>/', views.editar_aliado, name='editar_aliado'),
    path('dashboard/aliados/anular/<int:pk>/', views.anular_aliado, name='anular_aliado'),
    path('mis-tramites/', views.mis_tramites_cliente_view, name='mis_tramites'),
    path('tramite/detalle/<str:numero_tramite>/', views.detalle_tramite_cliente_view, name='detalle_tramite_cliente'),
    path('tramite/detalle/<str:numero_tramite>/', views.detalle_tramite_cliente_view, name='detalle_tramite_cliente'),
]

