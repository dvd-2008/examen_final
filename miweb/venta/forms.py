from django import forms
from django.core.exceptions import ValidationError
from .models import Cliente, Producto, VentaSimple

class ClienteCreateForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['id_cliente', 'ape_nombre', 'fec_registro']
        labels = {
            'id_cliente': 'DNI',
            'ape_nombre': 'Apellidos y Nombres',
            'fec_registro': 'Fecha de Registro'
        }
        widgets = {
            'id_cliente': forms.TextInput(attrs={
                'maxlength': '8', 
                'placeholder': 'Ingrese DNI'
            }),
            'ape_nombre': forms.TextInput(attrs={
                'placeholder': 'Ingrese Apellidos y Nombres'
            }),
            'fec_registro': forms.DateInput(attrs={
                'type': 'date'
            }),
        }
        error_messages = {
            'id_cliente': {
                'max_length': 'El DNI debe tener 8 caracteres.',
                'required': 'El DNI es obligatorio.',
            },
            'ape_nombre': {
                'required': 'El nombre es obligatorio.',
            },
            'fec_registro': {
                'required': 'La fecha de registro es obligatoria.',
            },
        }

    def clean_id_cliente(self):
        id_cliente = self.cleaned_data.get('id_cliente')
        if id_cliente:
            if Cliente.objects.filter(id_cliente=id_cliente).exists():
                raise ValidationError("DNI_DUPLICADO")
            return id_cliente

class ClienteUpdateForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['id_cliente', 'ape_nombre', 'fec_registro']
        labels = {
            'id_cliente': 'DNI',
            'ape_nombre': 'Apellidos y Nombres',
            'fec_registro': 'Fecha de Registro'
        }
        widgets = {
            'id_cliente': forms.TextInput(attrs={
                'readonly': True,
                'class': 'readonly-field',
            }),
            'ape_nombre': forms.TextInput(attrs={
                'placeholder': 'Ingrese Apellidos y Nombres'
            }),
            'fec_registro': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.fec_registro:
            self.initial['fec_registro'] = self.instance.fec_registro.strftime('%Y-%m-%d')

class ProductoCreateForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nom_prod', 'des_prod', 'precio', 'cantidad', 'fec_vencimiento']
        labels = {
            'nom_prod': 'Nombre del Producto',
            'des_prod': 'Descripción',
            'precio': 'Precio',
            'cantidad': 'Cantidad',
            'fec_vencimiento': 'Fecha de Vencimiento'
        }
        widgets = {
            'nom_prod': forms.TextInput(attrs={'placeholder': 'Ingrese nombre del producto'}),
            'des_prod': forms.Textarea(attrs={'placeholder': 'Ingrese descripción del producto'}),
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
            'cantidad': forms.NumberInput(),
            'fec_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }
        error_messages = {
            'nom_prod': {
                'required': 'El nombre del producto es obligatorio.',
            },
            'des_prod': {
                'required': 'La descripción es obligatoria.',
            },
            'precio': {
                'required': 'El precio es obligatorio.',
                'invalid': 'Ingrese un precio válido.',
            },
            'cantidad': {
                'required': 'La cantidad es obligatoria.',
                'invalid': 'Ingrese una cantidad válida.',
            },
            'fec_vencimiento': {
                'required': 'La fecha de vencimiento es obligatoria.',
            },
        }

class ProductoUpdateForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nom_prod', 'des_prod', 'precio', 'cantidad', 'fec_vencimiento']
        labels = {
            'nom_prod': 'Nombre del Producto',
            'des_prod': 'Descripción',
            'precio': 'Precio',
            'cantidad': 'Cantidad',
            'fec_vencimiento': 'Fecha de Vencimiento'
        }
        widgets = {
            'nom_prod': forms.TextInput(attrs={
                'placeholder': 'Ingrese nombre del producto',
                'class': 'form-control'
            }),
            'des_prod': forms.Textarea(attrs={
                'placeholder': 'Ingrese descripción del producto',
                'class': 'form-control',
                'rows': 3
            }),
            'precio': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'fec_vencimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.fec_vencimiento:
            self.initial['fec_vencimiento'] = self.instance.fec_vencimiento.strftime('%Y-%m-%d')

class VentaSimpleForm(forms.ModelForm):
    class Meta:
        model = VentaSimple
        fields = ['cliente', 'producto', 'cantidad']
        labels = {
            'cliente': 'Cliente',
            'producto': 'Producto',
            'cantidad': 'Cantidad'
        }
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        error_messages = {
            'cliente': {
                'required': 'El cliente es obligatorio.',
            },
            'producto': {
                'required': 'El producto es obligatorio.',
            },
            'cantidad': {
                'required': 'La cantidad es obligatoria.',
                'min_value': 'La cantidad debe ser al menos 1.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(estado=True, cantidad__gt=0)