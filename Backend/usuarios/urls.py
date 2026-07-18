from django.urls import path
from .controllers import RegistrarUsuarioController,GestionarUsuarioController, ConfirmarBorrarUsuario, UsuarioBorradoController , EditarUsuarioController, UsuariosDashboardController, UsuarioCreadoController, SeleccionarUsuarioEditarController, UsuarioEditadoController

urlpatterns = [
    path('usuario-dashboard/', UsuariosDashboardController.as_view(), name='usuario-dashboard'),
    path('crear-usuario/', RegistrarUsuarioController.as_view(), name='crear-usuario'),
    path('usuario-creado/', UsuarioCreadoController.as_view(), name='usuario-creado'),
    path('usuario-editado/', UsuarioEditadoController.as_view(), name='usuario-editado'),
    path('editar-usuario/<int:user_id>/', EditarUsuarioController.as_view(), name='editar-usuario'),
    path('editar-usuario/', SeleccionarUsuarioEditarController.as_view(), name='seleccionar-usuario'),
    path('gestionar-usuario/<int:user_id>/', GestionarUsuarioController.as_view(), name='gestionar-usuario'),
    path('borrar-usuario/<int:user_id>/', ConfirmarBorrarUsuario.as_view(), name='confirmar-borrar-usuario'),
    path('usuario-borrado/', UsuarioBorradoController.as_view(), name='usuario-borrado'),
]