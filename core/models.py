from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Tramite(models.Model):
    TIPO_SERVICIO_CHOICES = [
        ('busqueda', 'Búsqueda de Fábrica'),
        ('asesoria', 'Asesoría y Validación de Compras'),
        ('logistica', 'Logística Internacional'),
        ('nacionalizacion', 'Nacionalización y Aduanas'),
        ('inspeccion', 'Inspección en Origen'),
        ('transporte_local', 'Transporte Local y Entrega'),
        ('representacion', 'Representación y Distribución'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Revisión'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tramites')
    numero_tramite = models.CharField(max_length=20, unique=True, blank=True)
    tipo_servicio = models.CharField(max_length=50, choices=TIPO_SERVICIO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Nuevos campos para la gestión de aliados (con el nombre entre comillas)
    aliado_asignado = models.ForeignKey(
        'AliadoEstrategico',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tramites_asignados",
        verbose_name="Aliado Estratégico"
    )
    enviado_a_aliado = models.BooleanField(default=False, verbose_name="¿Enviado a cotizar?")
    fecha_envio_aliado = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Envío al Aliado")


    def save(self, *args, **kwargs):
        if not self.numero_tramite:
            ultimo = Tramite.objects.all().order_by('id').last()
            nuevo_id = 1 if not ultimo else ultimo.id + 1
            self.numero_tramite = f"TRM-{nuevo_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_tramite} - {self.get_tipo_servicio_display()} ({self.cliente.username})"


# --- MODELOS ESPECÍFICOS POR FORMULARIO ---

class DetalleBusquedaFabrica(models.Model):
    tramite = models.OneToOneField(Tramite, on_delete=models.CASCADE, related_name='detalle_busqueda')
    producto = models.CharField(max_length=255)
    marca_referencia = models.CharField(max_length=255, blank=True, null=True)
    nombre_contacto = models.CharField(max_length=255)
    telefono = models.CharField(max_length=50)
    ha_importado_antes = models.CharField(max_length=50)
    link_producto = models.URLField(blank=True, null=True)
    archivo_adjunto = models.FileField(upload_to='tramites/busqueda/', blank=True, null=True)
    cantidad_estimada = models.CharField(max_length=100, blank=True, null=True)
    especificaciones = models.TextField(blank=True, null=True)


class DetalleAsesoriaCompras(models.Model):
    tramite = models.OneToOneField(Tramite, on_delete=models.CASCADE, related_name='detalle_asesoria')
    nombre_contacto = models.CharField(max_length=255)
    telefono = models.CharField(max_length=50)
    donde_encontro_proveedor = models.CharField(max_length=100)
    estado_negociacion = models.CharField(max_length=100)
    monto_aproximado = models.CharField(max_length=100, blank=True, null=True)
    tipo_asesoria_urgencia = models.CharField(max_length=100)
    archivo_adjunto = models.FileField(upload_to='tramites/asesoria/', blank=True, null=True)


class DetalleLogistica(models.Model):
    tramite = models.OneToOneField(Tramite, on_delete=models.CASCADE, related_name='detalle_logistica')
    tipo_carga = models.CharField(max_length=100)
    incoterm = models.CharField(max_length=50)
    puerto_origen = models.CharField(max_length=100)
    puerto_destino = models.CharField(max_length=100)
    archivo_adjunto = models.FileField(upload_to='tramites/logistica/', blank=True, null=True)


class DetalleNacionalizacion(models.Model):
    tramite = models.OneToOneField(Tramite, on_delete=models.CASCADE, related_name='detalle_nacionalizacion')
    descripcion_comercial = models.TextField()
    uso_aplicacion = models.CharField(max_length=255)
    valor_fob = models.DecimalField(max_digits=10, decimal_places=2)
    certificado_origen = models.CharField(max_length=50)
    entidad_control = models.CharField(max_length=100)
    tipo_regimen = models.CharField(max_length=100)
    archivo_adjunto = models.FileField(upload_to='tramites/nacionalizacion/', blank=True, null=True)


class DetalleInspeccion(models.Model):
    tramite = models.OneToOneField(Tramite, on_delete=models.CASCADE, related_name='detalle_inspeccion')
    nombre_proveedor = models.CharField(max_length=255)
    ciudad_china = models.CharField(max_length=100)
    cantidad_unidades = models.IntegerField()
    tipo_control = models.CharField(max_length=100)
    archivo_adjunto = models.FileField(upload_to='tramites/inspeccion/', blank=True, null=True)


class DetalleTransporteLocal(models.Model):
    tramite = models.OneToOneField(Tramite, on_delete=models.CASCADE, related_name='detalle_transporte')
    cuenta_con_levante = models.CharField(max_length=100)
    punto_partida = models.CharField(max_length=255)
    ciudad_destino = models.CharField(max_length=255)
    tipo_vehiculo = models.CharField(max_length=100)
    peso_estimado = models.CharField(max_length=100)
    archivo_adjunto = models.FileField(upload_to='tramites/transporte/', blank=True, null=True)


class DetalleRepresentacion(models.Model):
    tramite = models.OneToOneField(Tramite, on_delete=models.CASCADE, related_name='detalle_representacion')
    nombre_empresa = models.CharField(max_length=255)
    telefono = models.CharField(max_length=50)
    canales_distribucion = models.CharField(max_length=100)
    nombre_fabrica_china = models.CharField(max_length=255)
    alcance_representacion = models.CharField(max_length=100)
    proyeccion_anual = models.CharField(max_length=100, blank=True, null=True)
    archivo_adjunto = models.FileField(upload_to='tramites/representacion/', blank=True, null=True)


class AliadoEstrategico(models.Model):
    TIPO_SERVICIO_CHOICES = [
        ('busqueda', 'Búsqueda de Fábrica'),
        ('asesoria', 'Asesoría y Validación de Compras'),
        ('logistica', 'Logística Internacional'),
        ('nacionalizacion', 'Nacionalización y Aduanas'),
        ('inspeccion', 'Inspección en Origen'),
        ('transporte_local', 'Transporte Local'),
        ('representacion', 'Representación y Distribución'),
    ]

    nombre_empresa = models.CharField(max_length=150, verbose_name="Nombre de la Agencia/Aliado")
    contacto = models.CharField(max_length=100, verbose_name="Persona de Contacto", blank=True, null=True)
    email = models.EmailField(verbose_name="Correo Electrónico de Cotizaciones")
    telefono = models.CharField(max_length=30, blank=True, null=True, verbose_name="Teléfono")
    tipo_servicio = models.JSONField(default=list, blank=True, verbose_name="Especialidades / Servicios")
    activo = models.BooleanField(default=True, verbose_name="¿Activo?")

    @property
    def get_servicios_display(self):
        dict_choices = dict(self.TIPO_SERVICIO_CHOICES)
        nombres = [dict_choices.get(sev, sev) for sev in self.tipo_servicio]
        return ", ".join(nombres) if nombres else "Sin servicios asignados"

    def __str__(self):
        return f"{self.nombre_empresa}"


class HistorialDocumentoTrámite(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='historial_documentos')
    nombre_archivo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='tramites/historial/')
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=255, default='Reemplazo de documento original')

    def __str__(self):
        return f"Historial {self.nombre_archivo} - Trámite #{self.tramite.numero_tramite}"