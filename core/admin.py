from django.contrib import admin
from .models import (
    AliadoEstrategico,
    Tramite,
    DetalleBusquedaFabrica,
    DetalleAsesoriaCompras,
    DetalleLogistica,
    DetalleNacionalizacion,
    DetalleInspeccion,
    DetalleTransporteLocal,
    DetalleRepresentacion
)


# Registramos los modelos secundarios como Inline para que aparezcan dentro de la misma vista del Trámite
class DetalleBusquedaInline(admin.StackedInline):
    model = DetalleBusquedaFabrica
    can_delete = False
    extra = 0


class DetalleAsesoriaInline(admin.StackedInline):
    model = DetalleAsesoriaCompras
    can_delete = False
    extra = 0


class DetalleLogisticaInline(admin.StackedInline):
    model = DetalleLogistica
    can_delete = False
    extra = 0


class DetalleNacionalizacionInline(admin.StackedInline):
    model = DetalleNacionalizacion
    can_delete = False
    extra = 0


class DetalleInspeccionInline(admin.StackedInline):
    model = DetalleInspeccion
    can_delete = False
    extra = 0


class DetalleTransporteLocalInline(admin.StackedInline):
    model = DetalleTransporteLocal
    can_delete = False
    extra = 0


class DetalleRepresentacionInline(admin.StackedInline):
    model = DetalleRepresentacion
    can_delete = False
    extra = 0


@admin.register(Tramite)
class TramiteAdmin(admin.ModelAdmin):
    list_display = ('numero_tramite', 'cliente', 'tipo_servicio', 'estado', 'fecha_creacion')
    list_filter = ('tipo_servicio', 'estado', 'fecha_creacion')
    search_fields = ('numero_tramite', 'cliente__username', 'cliente__email')
    readonly_fields = ('numero_tramite', 'fecha_creacion', 'fecha_actualizacion')

    # Esto asocia automáticamente el formulario específico correspondiente en el panel según el trámite
    inlines = [
        DetalleBusquedaInline,
        DetalleAsesoriaInline,
        DetalleLogisticaInline,
        DetalleNacionalizacionInline,
        DetalleInspeccionInline,
        DetalleTransporteLocalInline,
        DetalleRepresentacionInline,
    ]



@admin.register(AliadoEstrategico)
class AliadoEstrategicoAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'contacto', 'email', 'tipo_servicio', 'activo')
    list_filter = ('tipo_servicio', 'activo')
    search_fields = ('nombre_empresa', 'email')
