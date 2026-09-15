from datetime import timedelta
import secrets

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import EmailMessage, send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    AsesoriaComprasForm,
    BusquedaFabricaForm,
    InspeccionForm,
    LogisticaForm,
    NacionalizacionForm,
    RegistroForm,
    RepresentacionForm,
    TransporteLocalForm,
)
from .models import AliadoEstrategico, Tramite, HistorialDocumentoTrámite


# Create your views here.

def signup_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión automáticamente tras registrarse
            return redirect('home')
    else:
        form = RegistroForm()

    # Aplicar clases de Bootstrap a los campos del formulario
    for field in form.visible_fields():
        field.field.widget.attrs['class'] = 'form-control mb-3'

    return render(request, 'core/signup.html', {'form': form})


def obtener_o_crear_usuario_anonimo(request, email, nombre_completo=None):
    """
    Gestiona la lógica de identificación:
    - Si está autenticado, devuelve el usuario actual.
    - Si no, busca por email; si existe lo retorna, si no, crea un usuario temporal.
    """
    if request.user.is_authenticated:
        return request.user

    if not email:
        return None

    user = User.objects.filter(email__iexact=email).first()

    if user:
        return user

    username = email.split('@')[0] + "_" + secrets.token_hex(3)
    while User.objects.filter(username=username).exists():
        username = email.split('@')[0] + "_" + secrets.token_hex(3)

    password = secrets.token_urlsafe(10)
    first_name = nombre_completo or "Cliente"

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name
    )

    return user


def crear_tramite_view(request, tipo_servicio):
    config_servicios = {
        'busqueda': {'form_class': BusquedaFabricaForm, 'nombre': 'Búsqueda de Fábrica'},
        'asesoria': {'form_class': AsesoriaComprasForm, 'nombre': 'Asesoría y Validación de Compras'},
        'logistica': {'form_class': LogisticaForm, 'nombre': 'Logística Internacional'},
        'nacionalizacion': {'form_class': NacionalizacionForm, 'nombre': 'Nacionalización y Aduanas'},
        'inspeccion': {'form_class': InspeccionForm, 'nombre': 'Inspección en Origen'},
        'transporte_local': {'form_class': TransporteLocalForm, 'nombre': 'Transporte Local y Entrega'},
        'representacion': {'form_class': RepresentacionForm, 'nombre': 'Representación y Distribución'},
    }

    if tipo_servicio not in config_servicios:
        return redirect('home')

    servicio_info = config_servicios[tipo_servicio]
    FormClass = servicio_info['form_class']

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            email = request.POST.get('email')
            nombre_contacto = request.POST.get('nombre_contacto') or request.POST.get('nombre')

            cliente = obtener_o_crear_usuario_anonimo(request, email, nombre_contacto)

            tramite = Tramite.objects.create(
                cliente=cliente,
                tipo_servicio=tipo_servicio,
                estado='pendiente'
            )

            detalle = form.save(commit=False)
            detalle.tramite = tramite
            detalle.save()

            return redirect('detalle_tramite_exito', numero_tramite=tramite.numero_tramite)
        else:
            print("ERRORES DEL FORMULARIO:", form.errors)
    else:
        initial_data = {}
        if tipo_servicio == 'busqueda' and 'producto' in request.GET:
            initial_data['producto'] = request.GET.get('producto')

        form = FormClass(initial=initial_data)

    context = {
        'form': form,
        'nombre_servicio': servicio_info['nombre'],
        'tipo_servicio': tipo_servicio
    }

    return render(request, 'core/crear_tramite.html', context)


def exito_tramite_view(request, numero_tramite):
    tramite = get_object_or_404(Tramite, numero_tramite=numero_tramite)
    return render(request, 'core/tramite_exito.html', {'tramite': tramite})


def home(request):
    return render(request, 'core/home.html')


def solicitud_busqueda(request):
    producto_inicial = request.GET.get('producto', '')
    if producto_inicial:
        return redirect(f"/tramite/busqueda/?producto={producto_inicial}")
    return redirect('crear_tramite', tipo_servicio='busqueda')


def nosotros(request):
    return render(request, 'core/nosotros.html')


def servicios(request):
    return render(request, 'core/servicios.html')


def contact(request):
    return render(request, 'core/contact.html')


def cotizar_logistica_view(request):
    return redirect('crear_tramite', tipo_servicio='logistica')


def cotizar_nacionalizacion_view(request):
    return redirect('crear_tramite', tipo_servicio='nacionalizacion')


def cotizar_inspeccion_view(request):
    return redirect('crear_tramite', tipo_servicio='inspeccion')


def cotizar_transporte_local_view(request):
    return redirect('crear_tramite', tipo_servicio='transporte_local')


def solicitud_asesoria_view(request):
    return redirect('crear_tramite', tipo_servicio='asesoria')


def solicitud_representacion_view(request):
    return redirect('crear_tramite', tipo_servicio='representacion')


def seleccion_etapas(request):
    return render(request, 'core/seleccion_etapas.html')


def custom_admin_logout(request):
    logout(request)
    return redirect('home')


@staff_member_required
def dashboard_tramites_view(request):
    tramites = Tramite.objects.all().select_related('cliente').order_by('-fecha_creacion')

    cliente_id = request.GET.get('cliente')
    tipo_servicio = request.GET.get('tipo_servicio')
    estado = request.GET.get('estado')
    rango_fecha = request.GET.get('fecha')

    if cliente_id:
        tramites = tramites.filter(cliente_id=cliente_id)
    if tipo_servicio:
        tramites = tramites.filter(tipo_servicio=tipo_servicio)
    if estado:
        tramites = tramites.filter(estado=estado)

    hoy = timezone.now().date()
    if rango_fecha == 'hoy':
        tramites = tramites.filter(fecha_creacion__date=hoy)
    elif rango_fecha == '7dias':
        tramites = tramites.filter(fecha_creacion__date__gte=hoy - timedelta(days=7))
    elif rango_fecha == 'mes':
        tramites = tramites.filter(fecha_creacion__date__gte=hoy - timedelta(days=30))
    elif rango_fecha == 'anio':
        tramites = tramites.filter(fecha_creacion__year=hoy.year)

    clientes = User.objects.filter(tramites__isnull=False).distinct()

    context = {
        'tramites': tramites,
        'clientes': clientes,
        'tipos_servicio': Tramite.TIPO_SERVICIO_CHOICES if hasattr(Tramite, 'TIPO_SERVICIO_CHOICES') else [],
        'estados': Tramite.ESTADO_CHOICES if hasattr(Tramite, 'ESTADO_CHOICES') else [],
        'selected_cliente': cliente_id,
        'selected_tipo': tipo_servicio,
        'selected_estado': estado,
        'selected_fecha': rango_fecha,
    }
    return render(request, 'core/dashboard_tramites.html', context)


class CustomLoginView(LoginView):
    template_name = 'core/login.html'

    def get_success_url(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return '/dashboard/tramites/'
        return '/'


@staff_member_required
def gestionar_tramite_view(request, tramite_id):
  tramite = get_object_or_404(Tramite, id=tramite_id)

  # Filtrar aliados usando lookups para que coincida con la lista servicios_ofrecidos
  aliados_disponibles = AliadoEstrategico.objects.filter(
      tipo_servicio__contains=[tramite.tipo_servicio], activo=True
  )

  if request.method == 'POST':
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado:
      tramite.estado = nuevo_estado

    aliados_seleccionados_ids = request.POST.getlist('aliados_seleccionados')

    if aliados_seleccionados_ids:
      aliados_a_cotizar = AliadoEstrategico.objects.filter(
          id__in=aliados_seleccionados_ids, activo=True
      )

      if aliados_a_cotizar.exists():
        tramite.aliado_asignado = aliados_a_cotizar.first()

      correos_enviados = 0

      for aliado in aliados_a_cotizar:
        if not aliado.email:
          continue

        asunto = f'Nueva Solicitud de Cotización - Trámite {tramite.numero_tramite}'
        cuerpo = (
            f'Estimado equipo de {aliado.nombre_empresa},\n\n'
            f'Tenemos una nueva solicitud de servicio '
            f'({tramite.get_tipo_servicio_display()}) '
            f'que requiere su cotización con el margen acordado.\n\n'
            f'Código de Trámite: {tramite.numero_tramite}\n'
            f'Cliente: {tramite.cliente.get_full_name() or tramite.cliente.username} '
            f'({tramite.cliente.email})\n\n'
            f'Por favor revisar los documentos adjuntos para emitir la cotización correspondiente.\n\n'
            f'Atentamente,\nEquipo de Operaciones - Portium Group'
        )

        email_msg = EmailMessage(
            subject=asunto,
            body=cuerpo,
            from_email=None,  # Utiliza DEFAULT_FROM_EMAIL del settings.py
            to=[aliado.email],
        )

        try:
          posibles_detalles = [
              getattr(tramite, 'detalle_busqueda', None),
              getattr(tramite, 'detalle_asesoria', None),
              getattr(tramite, 'detalle_logistica', None),
              getattr(tramite, 'detalle_nacionalizacion', None),
              getattr(tramite, 'detalle_inspeccion', None),
              getattr(tramite, 'detalle_transporte', None),
              getattr(tramite, 'detalle_representacion', None),
          ]

          for rel in posibles_detalles:
            if rel and hasattr(rel, 'archivo_adjunto') and rel.archivo_adjunto:
              # Usar .read() directo de Django FieldFile previene errores de apertura en disco
              file_name = rel.archivo_adjunto.name.split('/')[-1]
              file_content = rel.archivo_adjunto.read()
              if file_content:
                email_msg.attach(file_name, file_content)
              break
        except Exception as e:
          print(f'Aviso: No se pudo adjuntar archivo para {aliado.nombre_empresa}:', e)

        try:
          email_msg.send(fail_silently=False)
          correos_enviados += 1
        except Exception as e:
          print(f'Error enviando correo a {aliado.email}:', e)

      if correos_enviados > 0:
        tramite.enviado_a_aliado = True
        tramite.fecha_envio_aliado = timezone.now()
        messages.success(
            request,
            f'¡Trámite actualizado y correo(s) enviado(s) con éxito a {correos_enviados} aliado(s)!',
        )
      else:
        messages.warning(
            request,
            'Se guardaron los cambios, pero no se pudo enviar ningún correo (verifique los emails de los aliados).',
        )
    else:
      messages.success(
          request, '¡Cambios y estado del trámite guardados exitosamente!'
      )

    tramite.save()
    return redirect('gestionar_tramite', tramite_id=tramite.id)

  context = {
      'tramite': tramite,
      'aliados_disponibles': aliados_disponibles,
  }
  return render(request, 'core/gestionar_tramite.html', context)


# --- MÓDULO DE ALIADOS ESTRATÉGICOS (Protegidos con staff_member_required) ---

@staff_member_required
def lista_aliados(request):
    """Muestra el listado de empresas aliadas en el panel personalizado"""
    aliados = AliadoEstrategico.objects.all().order_by('-id')
    return render(request, 'core/admin_aliados.html', {'aliados': aliados})


@staff_member_required
def crear_aliado(request):
    """Permite registrar un nuevo aliado reutilizando la lógica unificada"""
    return guardar_aliado(request, pk=None)


@staff_member_required
def editar_aliado(request, pk):
    """Permite editar un aliado existente reutilizando la lógica unificada"""
    return guardar_aliado(request, pk=pk)


@staff_member_required
def anular_aliado(request, pk):
    """Cambia el estado del aliado a inactivo o activo (anulación lógica)"""
    aliado = get_object_or_404(AliadoEstrategico, pk=pk)
    aliado.activo = not aliado.activo
    aliado.save()
    return redirect('lista_aliados')


@staff_member_required
def guardar_aliado(request, pk=None):
    # Lógica para obtener el aliado si se está editando, o crear uno nuevo
    aliado = get_object_or_404(AliadoEstrategico, pk=pk) if pk else AliadoEstrategico()

    if request.method == 'POST':
        aliado.nombre_empresa = request.POST.get('nombre_empresa')
        aliado.contacto = request.POST.get('contacto')
        aliado.email = request.POST.get('email')
        aliado.telefono = request.POST.get('telefono')

        # Captura todos los checkboxes seleccionados como una lista de Python
        aliado.tipo_servicio = request.POST.getlist('servicios_ofrecidos')

        if not pk:
            aliado.activo = True

        aliado.save()
        return redirect('lista_aliados')

    # Contexto para enviar las opciones al template
    context = {
        'aliado': aliado,
        'tipo_servicio_choices': AliadoEstrategico.TIPO_SERVICIO_CHOICES,
        'accion': 'Editar' if pk else 'Crear'
    }
    return render(request, 'core/form_aliado.html', context)


def enviar_cotizacion_aliados(request, tramite_id):
    tramite = get_object_or_404(Tramite, id=tramite_id)

    if request.method == 'POST':
        # Capturamos los IDs de los aliados seleccionados en los checkboxes del formulario
        aliados_ids = request.POST.getlist(
            'aliados_seleccionados')  # Asegúrate de que el name del checkbox en tu HTML sea este

        if not aliados_ids:
            messages.warning(request, "Por favor, selecciona al menos un aliado estratégico.")
            return redirect('detalle_tramite', pk=tramite_id)  # Ajusta tu URL de redirección

        aliados = AliadoEstrategico.objects.filter(id__in=aliados_ids)

        # Preparamos los datos del correo
        asunto = f"Nuevo Requerimiento de Cotización - Trámite #{tramite.id}"
        mensaje = (
            f"Estimado equipo,\n\n"
            f"Se ha generado un nuevo requerimiento para cotización asociado al trámite.\n"
            f"Detalles del trámite:\n"
            f"- Descripción/Uso: {tramite.uso_aplicacion}\n"
            f"- Valor FOB: {tramite.valor_fob}\n"
            f"- Régimen: {tramite.tipo_regimen}\n\n"
            f"Por favor, ingresar al sistema para revisar los archivos adjuntos y proceder con la cotización.\n\n"
            f"Atentamente,\nPanel Operativo"
        )

        destinatarios = [aliado.email for aliado in aliados if aliado.email]

        try:
            # Envío masivo o individual de correos
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=None,  # Utiliza DEFAULT_FROM_EMAIL
                recipient_list=destinatarios,
                fail_silently=False,
            )
            messages.success(request, "¡Requerimiento enviado exitosamente a los aliados seleccionados!")
        except Exception as e:
            messages.error(request, f"Hubo un error al enviar los correos: {e}")

        return redirect('dashboard_tramites')


@login_required
def mis_tramites_cliente_view(request):
    # Filtramos los trámites que pertenecen exclusivamente al usuario logueado
    tramites = Tramite.objects.filter(cliente=request.user).order_by('-fecha_creacion')
    return render(request, 'core/mis_tramites.html', {'tramites': tramites})


@login_required
def detalle_tramite_cliente_view(request, numero_tramite):
    tramite = get_object_or_404(Tramite, numero_tramite=numero_tramite, cliente=request.user)

    detalle_rel = None
    posibles_relaciones = [
        getattr(tramite, 'detalle_busqueda', None),
        getattr(tramite, 'detalle_asesoria', None),
        getattr(tramite, 'detalle_logistica', None),
        getattr(tramite, 'detalle_nacionalizacion', None),
        getattr(tramite, 'detalle_inspeccion', None),
        getattr(tramite, 'detalle_transporte', None),
        getattr(tramite, 'detalle_representacion', None),
    ]
    for rel in posibles_relaciones:
        if rel:
            detalle_rel = rel
            break

    if request.method == 'POST':
        nuevo_archivo = request.FILES.get('nuevo_archivo')
        if nuevo_archivo and detalle_rel:
            if detalle_rel.archivo_adjunto:
                HistorialDocumentoTrámite.objects.create(
                    tramite=tramite,
                    nombre_archivo=detalle_rel.archivo_adjunto.name.split('/')[-1],
                    archivo=detalle_rel.archivo_adjunto,
                    subido_por=request.user,
                    accion='Reemplazo de documento original'
                )

            detalle_rel.archivo_adjunto = nuevo_archivo
            detalle_rel.save()

            messages.success(request, "Documento actualizado correctamente. El historial ha sido registrado.")
            return redirect('detalle_tramite_cliente', numero_tramite=tramite.numero_tramite)

    context = {
        'tramite': tramite,
        'detalle_rel': detalle_rel,
        'historial': tramite.historial_documentos.all().order_by('-fecha_subida')
    }
    return render(request, 'core/detalle_tramite_cliente.html', context)

