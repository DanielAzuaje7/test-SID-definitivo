from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views import View
from .forms import RegistroUsuarioForm, EditarUsuarioForm
from django.urls import reverse

class RegistrarUsuarioController(View):
    plantilla = 'registrar_usuario.html'

    def get(self, request):
        form = RegistroUsuarioForm()
        return render(request, self.plantilla, {'form': form})

    def post(self, request):
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario-creado')
        return render(request, self.plantilla, {'form': form})

class EditarUsuarioController(View):
    plantilla = 'editar_usuario.html'

    def get(self, request, user_id):
        usuario = get_object_or_404(User, pk=user_id)
        form = EditarUsuarioForm(instance=usuario)
        return render(request, self.plantilla, {'form': form, 'usuario': usuario})

    def post(self, request, user_id):
        usuario = get_object_or_404(User, pk=user_id)
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('usuario-editado')
        return render(request, self.plantilla, {'form': form, 'usuario': usuario})

class UsuariosDashboardController(View):
    plantilla = 'usuarios_dashboard.html'
    
    def get(self, request):
        datos = {
            'is_admin': request.user.is_staff or request.user.is_superuser,
            'username': request.user.username,
        }
        return render(request, self.plantilla, datos)

class UsuarioCreadoController(View):
    plantilla = 'usuario_creado.html'

    def get(self, request):
        return render(request, self.plantilla)
    
class UsuarioEditadoController(View):
    plantilla = 'usuario_editado.html'

    def get(self, request):
        return render(request, self.plantilla)

class SeleccionarUsuarioEditarController(View):
    plantilla = 'seleccionar_usuario_editar.html'

    def get(self, request):
        usuarios = User.objects.exclude(id=request.user.id)
        return render(request, self.plantilla, {'usuarios': usuarios})
    
class GestionarUsuarioController(View):
    plantilla = "gestionar_usuario.html"

    def get(self, request, user_id):
        usuario = get_object_or_404(User, id=user_id)
        return render(request, self.plantilla, {
            'user': usuario,
        })
    
class ConfirmarBorrarUsuario(View):
    plantilla = "confirmar_borrar_usuario.html"

    def get(self, request, user_id):
        usuario = get_object_or_404(User, id=user_id)
        if request.GET.get('borrar') == '1':
            usuario_id = usuario.id
            usuario.delete()
            return redirect(f"{reverse('usuario-borrado')}?user_id={usuario_id}")
        return render(request, self.plantilla, {'user': usuario})

class UsuarioBorradoController(View):
    plantilla = "usuario_borrado.html"

    def get(self, request):
        return render(request, self.plantilla)

