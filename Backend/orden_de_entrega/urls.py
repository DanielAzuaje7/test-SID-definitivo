from django.urls import path
from .controllers import (
    VerOrdenesEntregaController,
    CrearOrdenDeEntregaController,
    EditarOrdenDeEntregaController,
    EmitirOrdenEntregaController,
    ConfirmarEmisionOrdenEntregaController,
    EliminarOrdenEntregaController,
    ConsultarOrdenEntregaController,
    VerOrdenesEmitidasController,
    DescargarOrdenEntregaPDFController,
    OrdenesDashboardController,
)  

urlpatterns = [
    path('ordenes/', VerOrdenesEntregaController.as_view(), name='orden_entrega'),
    path('ordenes/crear/', CrearOrdenDeEntregaController.as_view(), name='crear_orden_entrega'),
    path('ordenes/<int:orden_id>/editar/', EditarOrdenDeEntregaController.as_view(), name='editar_orden_entrega'),
    path('ordenes/<int:orden_id>/emitir/', EmitirOrdenEntregaController.as_view(), name='emitir_orden_entrega'),
    path('ordenes/<int:orden_id>/confirmar-emision/', ConfirmarEmisionOrdenEntregaController.as_view(), name='confirmar_emision_orden_entrega'),
    path('ordenes/<int:orden_id>/eliminar/', EliminarOrdenEntregaController.as_view(), name='eliminar_orden_entrega'),
    path('ordenes/<int:orden_id>/consultar/', ConsultarOrdenEntregaController.as_view(), name='consultar_orden_entrega'),
    path('ordenes/emitidas/', VerOrdenesEmitidasController.as_view(), name='ordenes_emitidas'),
    path('ordenes/<int:orden_id>/pdf/', DescargarOrdenEntregaPDFController.as_view(), name='descargar_orden_entrega_pdf'),
    path('ordenes/dashboard/', OrdenesDashboardController.as_view(), name='ordenes-dashboard'),  # <-- Nueva ruta para el dashboard
]