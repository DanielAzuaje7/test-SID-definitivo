from django.urls import path
from .controllers import CrearFacturaController, FacturaCreadaController, VerFacturaEmitidaController , SeleccionarFacturaEmitidaController , FacturaDashboardController, GestionarFacturaController, FacturaBorradaController, ConfirmarBorrarFactura, EditarFacturaController, SeleccionarFacturaController, FacturaEditadaController, ConfirmarEmisionFactura, FacturaEmitidaController, DescargarFacturaPDFController

urlpatterns = [
    path('factura-dashboard/', FacturaDashboardController.as_view(), name='factura-dashboard'),
    path('crear-factura/', CrearFacturaController.as_view(), name='crear-factura'),
    path('factura-creada/<int:factura_id>/', FacturaCreadaController.as_view(), name='factura-creada'),
    path('editar-factura/<int:factura_id>/', EditarFacturaController.as_view(), name='editar-factura'),
    path('editar-facturas/', SeleccionarFacturaController.as_view(), name='seleccionar-factura'),
    path('factura-editada/<int:factura_id>/', FacturaEditadaController.as_view(), name='factura-editada'),
    path('emitir/<int:factura_id>/', ConfirmarEmisionFactura.as_view(), name='confirmar-emitir-factura'),
    path('factura-emitida/', FacturaEmitidaController.as_view(), name='factura-emitida'),
    path('descargar/<int:factura_id>/', DescargarFacturaPDFController.as_view(), name='descargar-factura-pdf'),
    path('gestionar-factura/<int:factura_id>/', GestionarFacturaController.as_view(), name='gestionar-factura'),
    path('borrar-factura/<int:factura_id>/', ConfirmarBorrarFactura.as_view(), name='confirmar-borrar-factura'),
    path('factura-borrada/', FacturaBorradaController.as_view(), name='factura-borrada'),
    path('ver-factura/<int:factura_id>/', VerFacturaEmitidaController.as_view(), name='ver-factura-emitida'),
    path('seleccionar-factura-emitida/', SeleccionarFacturaEmitidaController.as_view(), name='seleccionar-factura-emitida'),
]