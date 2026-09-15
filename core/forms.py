from django import forms
from .models import (
    DetalleBusquedaFabrica,
    DetalleAsesoriaCompras,
    DetalleLogistica,
    DetalleNacionalizacion,
    DetalleInspeccion,
    DetalleTransporteLocal,
    DetalleRepresentacion,
    AliadoEstrategico
)

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class BusquedaFabricaForm(forms.ModelForm):
    class Meta:
        model = DetalleBusquedaFabrica
        fields = [
            'producto', 'marca_referencia', 'nombre_contacto',
            'telefono', 'ha_importado_antes', 'link_producto',
            'archivo_adjunto', 'cantidad_estimada', 'especificaciones'
        ]
        widgets = {
            'producto': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Autopartes, maquinaria, ropa...', 'style': 'width: 100%;'}),
            'marca_referencia': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Chevrolet, Toyota, Genérico (Opcional)', 'style': 'width: 100%;'}),
            'nombre_contacto': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Juan Pérez', 'style': 'width: 100%;'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: +593 99 123 4567', 'style': 'width: 100%;'}),
            'ha_importado_antes': forms.Select(choices=[
                ('', 'Seleccione una opción'),
                ('Primera vez', 'Es mi primera vez importando'),
                ('Regular', 'Importo de manera regular'),
                ('Frecuente', 'Soy importador frecuente')
            ], attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
            'link_producto': forms.URLInput(attrs={'class': 'form-control mb-3', 'placeholder': 'https://...', 'style': 'width: 100%;'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
            'cantidad_estimada': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: 500 unidades / 1 contenedor', 'style': 'width: 100%;'}),
            'especificaciones': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 3, 'placeholder': 'Detalles técnicos o requerimientos adicionales...', 'style': 'width: 100%;'}),
        }

class AsesoriaComprasForm(forms.ModelForm):
    class Meta:
        model = DetalleAsesoriaCompras
        fields = [
            'nombre_contacto', 'telefono', 'donde_encontro_proveedor',
            'estado_negociacion', 'monto_aproximado',
            'tipo_asesoria_urgencia', 'archivo_adjunto'
        ]
        widgets = {
            'nombre_contacto': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: María Gómez', 'style': 'width: 100%;'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: +593 99 123 4567', 'style': 'width: 100%;'}),
            'donde_encontro_proveedor': forms.Select(choices=[
                ('', 'Seleccione una opción'),
                ('Alibaba', 'Alibaba'),
                ('Feria', 'Feria de Cantón u otra feria'),
                ('Redes Sociales', 'Redes Sociales'),
                ('Contacto Directo', 'Contacto Directo / Otro')
            ], attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
            'estado_negociacion': forms.Select(choices=[
                ('', 'Seleccione el estado'),
                ('Cotizacion', 'Solo cotización inicial'),
                ('Negociacion', 'En negociaciones de precios'),
                ('Cerrado', 'Proveedor seleccionado por cerrar trato')
            ], attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
            'monto_aproximado': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: 5000 USD', 'style': 'width: 100%;'}),
            'tipo_asesoria_urgencia': forms.Select(choices=[
                ('', 'Seleccione la urgencia'),
                ('Normal', 'Normal'),
                ('Urgente', 'Urgente / Requiere validación inmediata')
            ], attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
        }

class LogisticaForm(forms.ModelForm):
    class Meta:
        model = DetalleLogistica
        fields = [
            'tipo_carga', 'incoterm', 'puerto_origen',
            'puerto_destino', 'archivo_adjunto'
        ]
        widgets = {
            'tipo_carga': forms.Select(choices=[
                ('', 'Seleccione tipo de carga'),
                ('FCL', 'Contenedor Completo (FCL)'),
                ('LCL', 'Carga Consolidada / Suelta (LCL)'),
                ('Aereo', 'Carga Aérea')
            ], attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
            'incoterm': forms.Select(choices=[
                ('', 'Seleccione Incoterm'),
                ('FOB', 'FOB'),
                ('EXW', 'EXW'),
                ('CIF', 'CIF'),
                ('DDP', 'DDP')
            ], attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
            'puerto_origen': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Ningbo, Shanghai, Shenzhen', 'style': 'width: 100%;'}),
            'puerto_destino': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Guayaquil, Ecuador', 'style': 'width: 100%;'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
        }

class NacionalizacionForm(forms.ModelForm):
    class Meta:
        model = DetalleNacionalizacion
        fields = [
            'descripcion_comercial', 'uso_aplicacion', 'valor_fob',
            'certificado_origen', 'entidad_control', 'tipo_regimen',
            'archivo_adjunto'
        ]
        widgets = {
            'descripcion_comercial': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 3, 'placeholder': 'Ej: Partes y piezas para maquinaria industrial...', 'style': 'width: 100%;'}),
            'uso_aplicacion': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Uso industrial / comercial', 'style': 'width: 100%;'}),
            'valor_fob': forms.NumberInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: 12500', 'style': 'width: 100%;'}),
            'certificado_origen': forms.Select(choices=[
                ('', '¿Posee certificado?'),
                ('Si', 'Sí'),
                ('No', 'No')
            ], attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
            'entidad_control': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: ARCSA, Agrocalidad, INEN', 'style': 'width: 100%;'}),
            'tipo_regimen': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Importación a consumo', 'style': 'width: 100%;'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
        }

class InspeccionForm(forms.ModelForm):
    class Meta:
        model = DetalleInspeccion
        fields = [
            'nombre_proveedor', 'ciudad_china', 'cantidad_unidades',
            'tipo_control', 'archivo_adjunto'
        ]
        widgets = {
            'nombre_proveedor': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Zhejiang Manufacturing Co.', 'style': 'width: 100%;'}),
            'ciudad_china': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Yiwu, Guangzhou, Ningbo', 'style': 'width: 100%;'}),
            'cantidad_unidades': forms.NumberInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: 1000', 'style': 'width: 100%;'}),
            'tipo_control': forms.Select(choices=[
                ('', 'Seleccione tipo de control'),
                ('Pre-embarque', 'Inspección Pre-embarque (PSI)'),
                ('Durante produccion', 'Durante la Producción (DUPRO)'),
                ('Carga', 'Supervisión de Carga')
            ], attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
        }

class TransporteLocalForm(forms.ModelForm):
    class Meta:
        model = DetalleTransporteLocal
        fields = [
            'cuenta_con_levante', 'punto_partida', 'ciudad_destino',
            'tipo_vehiculo', 'peso_estimado', 'archivo_adjunto'
        ]
        widgets = {
            'cuenta_con_levante': forms.Select(choices=[
                ('', 'Seleccione una opción'),
                ('Si', 'Sí, cuenta con pase/levante aduanero'),
                ('No', 'No')
            ], attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
            'punto_partida': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Puerto Marítimo de Guayaquil', 'style': 'width: 100%;'}),
            'ciudad_destino': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Quito, Bodega Principal', 'style': 'width: 100%;'}),
            'tipo_vehiculo': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Camión 3.5t, Furgón', 'style': 'width: 100%;'}),
            'peso_estimado': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: 1.2 Toneladas', 'style': 'width: 100%;'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
        }

class RepresentacionForm(forms.ModelForm):
    class Meta:
        model = DetalleRepresentacion
        fields = [
            'nombre_empresa', 'telefono', 'canales_distribucion',
            'nombre_fabrica_china', 'alcance_representacion',
            'proyeccion_anual', 'archivo_adjunto'
        ]
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Portium Group S.A.', 'style': 'width: 100%;'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: +593 99 123 4567', 'style': 'width: 100%;'}),
            'canales_distribucion': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Mayorista y Retail', 'style': 'width: 100%;'}),
            'nombre_fabrica_china': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Guangdong Tech Ltd.', 'style': 'width: 100%;'}),
            'alcance_representacion': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Exclusividad para Ecuador', 'style': 'width: 100%;'}),
            'proyeccion_anual': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: 50,000 USD', 'style': 'width: 100%;'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control mb-3', 'style': 'width: 100%;'}),
        }


class AliadoEstrategicoForm(forms.ModelForm):
    servicios_ofrecidos = forms.MultipleChoiceField(
        choices=AliadoEstrategico.TIPO_SERVICIO_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Servicios que ofrece el Aliado"
    )

    class Meta:
        model = AliadoEstrategico
        fields = ['nombre_empresa', 'contacto', 'email', 'telefono', 'servicios_ofrecidos', 'activo']
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Si-Comex', 'style': 'width: 100%;'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: Adrian Gomez', 'style': 'width: 100%;'}),
            'email': forms.EmailInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: contacto@sicomex.com', 'style': 'width: 100%;'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Ej: +593 99 123 4567', 'style': 'width: 100%;'}),
        }