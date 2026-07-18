from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    es_admin = forms.BooleanField(label="¿Es administrador?", required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'es_admin']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
        help_texts = {
            'username': '',
            'first_name': '',
            'last_name': '',
            'email': '',
            'password1': '',
            'password2': '',
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.is_staff = self.cleaned_data['es_admin']
        if commit:
            usuario.save()
        return usuario

class EditarUsuarioForm(UserChangeForm):
    password = None 
    es_admin = forms.BooleanField(label="¿Es administrador?", required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'es_admin']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['es_admin'].initial = self.instance.is_staff

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.is_staff = self.cleaned_data['es_admin']
        if commit:
            usuario.save()
        return usuario