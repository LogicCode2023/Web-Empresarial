from datetime import timedelta
import secrets

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import EmailMessage, send_mail
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.files.base import ContentFile

from .forms import (
    AliadoEstrategicoForm,
    AsesoriaComprasForm,
    BusquedaFabricaForm,
    ContactoAliadoForm,
    InspeccionForm,
    LogisticaForm,
    NacionalizacionForm,
    RegistroForm,
    RepresentacionForm,
    TransporteLocalForm,
)
from .models import AliadoEstrategico, ContactoAliado, HistorialDocumentoTrámite, Tramite, CorreoEnviado, CorreoAdjunto
from django.conf import settings
from .forms import CorreoManualForm
import os
import base64
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
import traceback
from django.http import HttpResponse

REMITENTES_POR_USUARIO = {
    'juanjose': 'Juan Daste <ejecutivo1@portiumgroup.com>',
    'juansebas': 'Gerencia Portium <gerencia@portiumgroup.com>',
}

ContactoAliadoFormSet = inlineformset_factory(
    AliadoEstrategico,
    ContactoAliado,
    form=ContactoAliadoForm,
    extra=1,
    can_delete=True
)


def signup_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistroForm()

    for field in form.visible_fields():
        field.field.widget.attrs['class'] = 'form-control mb-3'

    return render(request, 'core/signup.html', {'form': form})


def obtener_o_crear_usuario_anonimo(request, email, nombre_completo=None):
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
    return render(request, 'core/dashboard_tramites.html', {'tramites': tramites})


class CustomLoginView(LoginView):
    template_name = 'core/login.html'

    def get_success_url(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return '/dashboard/tramites/'
        return '/'


@staff_member_required
def gestionar_tramite_view(request, tramite_id):
    tramite = get_object_or_404(Tramite, id=tramite_id)
    return render(request, 'core/gestionar_tramite.html', {'tramite': tramite})


@staff_member_required
def lista_aliados(request):
    aliados = AliadoEstrategico.objects.all().order_by('-id')
    return render(request, 'core/admin_aliados.html', {'aliados': aliados})


@staff_member_required
def crear_aliado(request):
    return guardar_aliado(request, pk=None)


@staff_member_required
def editar_aliado(request, pk):
    return guardar_aliado(request, pk=pk)


@staff_member_required
def anular_aliado(request, pk):
    aliado = get_object_or_404(AliadoEstrategico, pk=pk)
    aliado.activo = not aliado.activo
    aliado.save()
    return redirect('lista_aliados')


@staff_member_required
def guardar_aliado(request, pk=None):
    aliado = get_object_or_404(AliadoEstrategico, pk=pk) if pk else AliadoEstrategico()
    if request.method == 'POST':
        form = AliadoEstrategicoForm(request.POST, instance=aliado)
        formset = ContactoAliadoFormSet(request.POST, instance=aliado)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('lista_aliados')
    else:
        form = AliadoEstrategicoForm(instance=aliado)
        formset = ContactoAliadoFormSet(instance=aliado)
    return render(request, 'core/form_aliado.html', {'form': form, 'formset': formset})


@login_required
def mis_tramites_cliente_view(request):
    tramites = Tramite.objects.filter(cliente=request.user).order_by('-fecha_creacion')
    return render(request, 'core/mis_tramites.html', {'tramites': tramites})


@login_required
def detalle_tramite_cliente_view(request, numero_tramite):
    tramite = get_object_or_404(Tramite, numero_tramite=numero_tramite, cliente=request.user)
    return render(request, 'core/detalle_tramite_cliente.html', {'tramite': tramite})


@login_required
def redactar_correo_view(request):
    remitentes_disponibles = [
        "ejecutivo1@portiumgroup.com",
        "ejecutivo2@portiumgroup.com",
        "contacto@portiumgroup.com"
    ]
    username_actual = request.user.username.lower()
    remitente_correo = REMITENTES_POR_USUARIO.get(username_actual, remitentes_disponibles[0])
    destinatario_initial = request.GET.get('email', '')

    if request.method == 'POST':
        form = CorreoManualForm(request.POST, request.FILES)
        if form.is_valid():
            destinatario_raw = form.cleaned_data['destinatario']
            asunto = form.cleaned_data['asunto']
            mensaje = form.cleaned_data['mensaje']
            archivo = form.cleaned_data.get('archivo_adjunto')

            destinatarios = [e.strip() for e in destinatario_raw.replace(';', ',').split(',') if e.strip()]

            try:
                configuration = sib_api_v3_sdk.Configuration()
                configuration.api_key['api-key'] = os.environ.get('BREVO_API_KEY')
                api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

                to_dest = [{"email": email_addr} for email_addr in destinatarios]
                attachments = None
                if archivo:
                    contenido_base64 = base64.b64encode(archivo.read()).decode('utf-8')
                    attachments = [{"content": contenido_base64, "name": archivo.name}]

                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    sender={"name": "Portium Group", "email": "contacto@portiumgroup.com"},
                    to=to_dest,
                    subject=asunto,
                    text_content=mensaje,
                    attachment=attachments
                )
                api_instance.send_transac_email(send_smtp_email)

                CorreoEnviado.objects.create(
                    remitente_usuario=request.user,
                    remitente_correo=remitente_correo,
                    destinatario=", ".join(destinatarios)[:254],
                    asunto=asunto,
                    mensaje=mensaje,
                    archivo_adjunto=archivo,
                    tipo='ENVIADO',
                    leido=True
                )

                messages.success(request, "¡Correo enviado exitosamente!")
                return redirect(f"{request.path}?email={destinatarios[0] if destinatarios else ''}")
            except Exception as e:
                messages.error(request, f"Error al enviar: {e}")

    form = CorreoManualForm(initial={'destinatario': destinatario_initial})
    historial_correos = CorreoEnviado.objects.all().order_by('-fecha_envio')[:15]

    context = {
        'form': form,
        'remitentes': remitentes_disponibles,
        'remitente_correo': remitente_correo,
        'historial_correos': historial_correos,
        'destinatario_actual': destinatario_initial
    }
    return render(request, 'core/redactar_correo.html', context)


@csrf_exempt
def webhook_recibir_correo_view(request):
    """
    Endpoint robusto para recibir respuestas de Cloudflare Worker o Brevo con soporte para adjuntos.
    """
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json' or request.body:
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except Exception:
                    data = request.POST
            else:
                data = request.POST

            print("PAYLOAD DE CLOUDFLARE RECIBIDO:", data)

            remitente_email = data.get('from', '') or data.get('sender', '') or data.get('From', '')
            destinatario_email = data.get('to', '') or data.get('recipient', '') or data.get('To', '')
            asunto = data.get('subject', 'Sin asunto') or data.get('Subject', 'Sin asunto')
            cuerpo = data.get('text', '') or data.get('html', '') or data.get('body-plain', '')
            msg_id = data.get('message_id', '') or data.get('Message-ID', '')
            attachments = data.get('attachments', [])

            # Convertir a texto limpio si viene en lista o dict
            if isinstance(remitente_email, list):
                remitente_email = remitente_email[0] if remitente_email else ''
            if isinstance(destinatario_email, list):
                destinatario_email = destinatario_email[0] if destinatario_email else ''

            remitente_email = str(remitente_email)
            destinatario_email = str(destinatario_email)

            if '<' in remitente_email and '>' in remitente_email:
                remitente_email = remitente_email.split('<')[1].split('>')[0].strip()

            if '<' in destinatario_email and '>' in destinatario_email:
                destinatario_email = destinatario_email.split('<')[1].split('>')[0].strip()

            if not remitente_email:
                return JsonResponse({'status': 'error', 'message': 'Falta el correo remitente'}, status=400)

            if msg_id and CorreoEnviado.objects.filter(message_id=msg_id).exists():
                return JsonResponse({'status': 'ok', 'message': 'Ya registrado previamente'}, status=200)

            # 1. Crear el registro del mensaje entrante
            nuevo_correo = CorreoEnviado.objects.create(
                remitente_correo=remitente_email,
                destinatario=destinatario_email or 'contacto@portiumgroup.com',
                asunto=asunto,
                mensaje=cuerpo,
                tipo='RECIBIDO',
                leido=False,
                message_id=msg_id
            )

            # 2. Procesar y guardar los archivos adjuntos recibidos desde el Worker
            for att in attachments:
                filename = att.get('filename')
                b64_content = att.get('content_base64')

                if filename and b64_content:
                    try:
                        file_data = base64.b64decode(b64_content)
                        file_file = ContentFile(file_data, name=filename)

                        CorreoAdjunto.objects.create(
                            mensaje=nuevo_correo,
                            archivo=file_file,
                            nombre_archivo=filename
                        )
                    except Exception as ex_att:
                        print(f"Error procesando adjunto {filename}: {ex_att}")

            print(f"CORREO ENTRANTE GUARDADO CON ÉXITO: ID {nuevo_correo.id} DE {remitente_email}")
            return JsonResponse({'status': 'ok', 'message': 'Correo registrado correctamente con adjuntos'}, status=200)

        except Exception as e:
            error_msg = traceback.format_exc()
            print("ERROR CRÍTICO EN WEBHOOK:\n", error_msg)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'método no permitido'}, status=405)


@login_required
def bandeja_correos(request):
    CorreoEnviado.objects.filter(tipo='ENVIADO').exclude(
        remitente_correo__icontains='portiumgroup.com'
    ).update(tipo='RECIBIDO')

    todos_los_correos = CorreoEnviado.objects.all().order_by('-fecha_envio')

    hilos_dict = {}
    for correo in todos_los_correos:
        asunto_limpio = (correo.asunto or "").strip()
        while True:
            lower_asunto = asunto_limpio.lower()
            if lower_asunto.startswith(('re:', 'rv:', 'fwd:')):
                asunto_limpio = asunto_limpio[3:].strip()
            else:
                break

        if not asunto_limpio:
            asunto_limpio = "Sin Asunto"

        correo_externo = correo.remitente_correo if correo.tipo == 'RECIBIDO' else correo.destinatario
        clave_hilo = f"{asunto_limpio.lower()}_{correo_externo.lower()}"

        if clave_hilo not in hilos_dict:
            hilos_dict[clave_hilo] = {
                'ultimo_correo': correo,
                'tiene_no_leidos': False,
                'es_recibido': False
            }

        if correo.tipo == 'RECIBIDO' and not correo.leido:
            hilos_dict[clave_hilo]['tiene_no_leidos'] = True

        if correo.tipo == 'RECIBIDO':
            hilos_dict[clave_hilo]['es_recibido'] = True

    lista_hilos = []
    for clave, datos in hilos_dict.items():
        c = datos['ultimo_correo']
        c.tiene_no_leidos = datos['tiene_no_leidos']
        c.es_recibido_hilo = datos['es_recibido']
        lista_hilos.append(c)

    lista_hilos.sort(key=lambda x: x.fecha_envio, reverse=True)

    return render(request, 'core/bandeja_correos.html', {'correos': lista_hilos})


@login_required
def detalle_correo(request, correo_id):
    try:
        correo_principal = get_object_or_404(CorreoEnviado, id=correo_id)

        if correo_principal.tipo == 'RECIBIDO' and not correo_principal.leido:
            correo_principal.leido = True
            correo_principal.save()

        asunto_limpio = (correo_principal.asunto or "").strip()
        while True:
            lower_asunto = asunto_limpio.lower()
            if lower_asunto.startswith(('re:', 'rv:', 'fwd:')):
                asunto_limpio = asunto_limpio[3:].strip()
            else:
                break

        correo_externo = correo_principal.remitente_correo if correo_principal.tipo == 'RECIBIDO' else correo_principal.destinatario

        hilo_completo = CorreoEnviado.objects.filter(
            models.Q(asunto__icontains=asunto_limpio) &
            (models.Q(destinatario__icontains=correo_externo) | models.Q(remitente_correo__icontains=correo_externo))
        ).order_by('fecha_envio')

        for m in hilo_completo:
            if m.tipo == 'RECIBIDO' and not m.leido:
                m.leido = True
                m.save()

        context = {
            'correo': correo_principal,
            'respuestas': hilo_completo
        }
        return render(request, 'core/detalle_correo.html', context)

    except Exception as e:
        error_detallado = traceback.format_exc()
        return HttpResponse(f"<h1>Error de Python:</h1><pre>{error_detallado}</pre>", status=500)


def responder_correo(request, correo_id):
    correo_original = get_object_or_404(CorreoEnviado, id=correo_id)

    if request.method == 'POST':
        cuerpo = request.POST.get('cuerpo_respuesta')
        destinatarios_cc = request.POST.get('destinatario_cc', '')  # Recibimos las copias si las hay

        # Lógica para enviar el correo real y guardarlo en la base de datos:
        nuevo_correo = CorreoEnviado.objects.create(
            remitente_usuario=request.user,
            remitente_correo=request.user.email or "ejecutivo1@portiumgroup.com",
            destinatario=correo_original.remitente_correo,
            destinatario_cc=destinatarios_cc,
            asunto=f"RE: {correo_original.asunto.replace('RE: ', '')}",
            mensaje=cuerpo,
            tipo='ENVIADO',
            message_id=correo_original.message_id  # Mantiene el hilo
        )

        # Manejo de múltiples adjuntos en la respuesta
        archivos = request.FILES.getlist('archivo_respuesta')
        for archivo in archivos:
            CorreoAdjunto.objects.create(
                mensaje=nuevo_correo,
                archivo=archivo,
                nombre_archivo=archivo.name
            )

        messages.success(request, "¡Respuesta enviada exitosamente!")

        # REDIRECCIONAR A LA BANDEJA PRINCIPAL (Para recargar la vista completa con CSS)
        return redirect('bandeja_correos')