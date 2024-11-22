from django import forms
from .models import EspacioTrabajo, Tablero, Lista, Tarjeta
from django.contrib.auth.models import User

class EspacioTrabajoForm(forms.ModelForm):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
 
    def __init__(self, *args, **kwargs):
        usuario_actual = kwargs.pop('usuario_actual', None)
        super(EspacioTrabajoForm, self).__init__(*args, **kwargs)
        if usuario_actual:
            self.fields['usuarios'].queryset = User.objects.exclude(id=usuario_actual.id)

    class Meta:
        model = EspacioTrabajo
        fields = ['nombre', 'usuarios']

class AgregarUsuarioForm(forms.Form):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Selecciona los usuarios para agregar"
    )

    def __init__(self, *args, **kwargs):
        espacio = kwargs.pop('espacio', None)
        super(AgregarUsuarioForm, self).__init__(*args, **kwargs)
        if espacio:
            self.fields['usuarios'].queryset = User.objects.exclude(id__in=espacio.usuarios.all())

class EliminarUsuarioForm(forms.Form):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Selecciona los usuarios para eliminar"
    )

    def __init__(self, *args, **kwargs):
        espacio = kwargs.pop('espacio', None)
        super(EliminarUsuarioForm, self).__init__(*args, **kwargs)
        if espacio:
            self.fields['usuarios'].queryset = espacio.usuarios.exclude(id=espacio.propietario.id)

class TableroForm(forms.ModelForm):
    class Meta:
        model = Tablero
        fields = ['nombre', 'descripcion']

class ListaForm(forms.ModelForm):
    class Meta:
        model = Lista
        fields = ['nombre', 'max_wip']

class TarjetaForm(forms.ModelForm):
    class Meta:
        model = Tarjeta
        fields = ['nombre', 'descripcion', 'fecha_vencimiento', 'usuario_asignado', 'etiqueta']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        espacio_trabajo = kwargs.pop('espacio_trabajo', None)
        super(TarjetaForm, self).__init__(*args, **kwargs)
        if espacio_trabajo:
            self.fields['usuario_asignado'].queryset = espacio_trabajo.usuarios.all()
