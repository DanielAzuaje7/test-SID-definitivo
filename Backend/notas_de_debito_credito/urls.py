from django.urls import path
from .controllers import (
    DescargarNotaCreditoPDFController,
    DescargarNotaDebitoPDFController,
    NotasDebitoCreditoController,
    VerNotasDebitoController,
    VerNotasCreditoController,
    CrearNotaDebitoController,
    EditarNotaDebitoController,
    CrearNotaCreditoController,
    EditarNotaCreditoController,
    EmitirNotaDebitoController,
    EmitirNotaCreditoController,  
    ConfirmarEmisionNotaDebitoController,
    ConfirmarEmisionNotaCreditoController,  
    VerNotasDebitoEmitidasController,  
    VerNotasCreditoEmitidasController,
    EliminarNotaCreditoController,
    EliminarNotaDebitoController,
    ConsultarNotaCreditoController,
    ConsultarNotaDebitoController,
      
)

urlpatterns = [
    path('notas/', NotasDebitoCreditoController.as_view(), name='notas-dashboard'),

    # Notas de Débito
    path('notas/debito/', VerNotasDebitoController.as_view(), name='nota_debito'),
    path('notas/debito/crear/', CrearNotaDebitoController.as_view(), name='crear-nota-debito'),
    path('notas/debito/<int:nota_id>/editar/', EditarNotaDebitoController.as_view(), name='editar-nota-debito'),
    path('notas/debito/<int:nota_id>/emitir/', EmitirNotaDebitoController.as_view(), name='emitir-nota-debito'),
    path('notas/debito/<int:nota_id>/confirmar-emision/', ConfirmarEmisionNotaDebitoController.as_view(), name='confirmar-emision-nota-debito'),
    path('notas/debito/emitidas/', VerNotasDebitoEmitidasController.as_view(), name='notas-debito-emitidas'),
    path('notas/debito/<int:nota_id>/eliminar/', EliminarNotaDebitoController.as_view(), name='eliminar-nota-debito'),
    path('notas/debito/<int:nota_id>/consultar/', ConsultarNotaDebitoController.as_view(), name='consultar-nota-debito'),
    path('notas/debito/<int:nota_id>/pdf/', DescargarNotaDebitoPDFController.as_view(), name='descargar-nota-debito-pdf'),

    # Notas de Crédito
    path('notas/credito/', VerNotasCreditoController.as_view(), name='nota_credito'),
    path('notas/credito/crear/', CrearNotaCreditoController.as_view(), name='crear-nota-credito'),
    path('notas/credito/<int:nota_id>/editar/', EditarNotaCreditoController.as_view(), name='editar-nota-credito'),
    path('notas/credito/<int:nota_id>/emitir/', EmitirNotaCreditoController.as_view(), name='emitir-nota-credito'),
    path('notas/credito/<int:nota_id>/confirmar-emision/', ConfirmarEmisionNotaCreditoController.as_view(), name='confirmar-emision-nota-credito'),
    path('notas/credito/emitidas/', VerNotasCreditoEmitidasController.as_view(), name='notas-credito-emitidas'),
    path('notas/credito/<int:nota_id>/eliminar/', EliminarNotaCreditoController.as_view(), name='eliminar-nota-credito'),
    path('notas/credito/<int:nota_id>/consultar/', ConsultarNotaCreditoController.as_view(), name='consultar-nota-credito'),
    path('notas/credito/<int:nota_id>/pdf/', DescargarNotaCreditoPDFController.as_view(), name='descargar-nota-credito-pdf'),
]