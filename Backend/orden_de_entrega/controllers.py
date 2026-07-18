from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import OrdenDeEntrega, ProductoEntrega
from .forms import OrdenDeEntregaForm, ProductoEntregaForm
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from Backend.facturas.models import Factura


class VerOrdenesEntregaController(LoginRequiredMixin, View):
    plantilla = 'listar-ordenes.html'
    def get(self, request):
        ordenes = OrdenDeEntrega.objects.filter(usuario=request.user, emitida=False)
        return render(request, self.plantilla, {'ordenes': ordenes, 'usuario': request.user.username})

class VerOrdenesEmitidasController(LoginRequiredMixin, View):
    plantilla = 'ordenes-emitidas.html'
    def get(self, request):
        ordenes = OrdenDeEntrega.objects.filter(usuario=request.user, emitida=True)
        return render(request, self.plantilla, {'ordenes': ordenes, 'usuario': request.user.username})

class CrearOrdenDeEntregaController(LoginRequiredMixin, View):
    plantilla = 'crear-orden.html'

    def get(self, request):
        ProductoEntregaFormSet = inlineformset_factory(
            OrdenDeEntrega, ProductoEntrega, form=ProductoEntregaForm, extra=1, can_delete=True
        )
        form = OrdenDeEntregaForm()
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ProductoEntregaFormSet()
        return render(request, self.plantilla, {
            'form': form,
            'formset': formset,
            'orden': None,
        })

    def post(self, request):
        ProductoEntregaFormSet = inlineformset_factory(
            OrdenDeEntrega, ProductoEntrega, form=ProductoEntregaForm, extra=1, can_delete=True
        )
        form = OrdenDeEntregaForm(request.POST)
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ProductoEntregaFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            orden = form.save(commit=False)
            orden.usuario = request.user
            orden.subtotal = 0
            orden.iva = 0
            orden.total = 0
            orden.save()
            productos = formset.save(commit=False)
            for producto in productos:
                producto.orden = orden
                producto.save()
            # Recalcular totales
            orden.subtotal = orden.calcular_subtotal()
            orden.iva = orden.calcular_iva()
            orden.total = orden.calcular_total()
            orden.save(update_fields=['subtotal', 'iva', 'total'])
            return redirect('orden_entrega')
        return render(request, self.plantilla, {
            'form': form,
            'formset': formset,
            'orden': None,
        })

class EditarOrdenDeEntregaController(LoginRequiredMixin, View):
    plantilla = 'editar-orden.html'
    def get(self, request, orden_id):
        orden = get_object_or_404(OrdenDeEntrega, id=orden_id, usuario=request.user, emitida=False)
        ProductoEntregaFormSet = inlineformset_factory(
            OrdenDeEntrega, ProductoEntrega, form=ProductoEntregaForm, extra=1, can_delete=True
        )
        form = OrdenDeEntregaForm(instance=orden)
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ProductoEntregaFormSet(instance=orden)
        return render(request, self.plantilla, {
            'form': form,
            'formset': formset,
            'orden': orden,
        })

    def post(self, request, orden_id):
        orden = get_object_or_404(OrdenDeEntrega, id=orden_id, usuario=request.user, emitida=False)
        ProductoEntregaFormSet = inlineformset_factory(
            OrdenDeEntrega, ProductoEntrega, form=ProductoEntregaForm, extra=1, can_delete=True
        )
        form = OrdenDeEntregaForm(request.POST, instance=orden)
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ProductoEntregaFormSet(request.POST, instance=orden)
        if form.is_valid() and formset.is_valid():
            orden = form.save(commit=False)
            orden.usuario = request.user
            orden.save()
            productos = formset.save(commit=False)
            for producto in productos:
                producto.orden = orden
                producto.save()
            for producto in formset.deleted_objects:
                producto.delete()
            # Recalcular totales
            orden.subtotal = orden.calcular_subtotal()
            orden.iva = orden.calcular_iva()
            orden.total = orden.calcular_total()
            orden.save(update_fields=['subtotal', 'iva', 'total'])
            return redirect('orden_entrega')
        # Agrega esto para depurar
        print("Form errors:", form.errors)
        print("Formset errors:", formset.errors)
        return render(request, self.plantilla, {
            'form': form,
            'formset': formset,
            'orden': orden,
        })

class EmitirOrdenEntregaController(LoginRequiredMixin, View):
    def post(self, request, orden_id):
        orden = get_object_or_404(OrdenDeEntrega, id=orden_id, usuario=request.user, emitida=False)
        orden.emitida = True
        orden.save()
        return redirect('orden_entrega')

class ConfirmarEmisionOrdenEntregaController(LoginRequiredMixin, View):
    plantilla = 'confirmar-emision-orden-entrega.html'
    def get(self, request, orden_id):
        orden = get_object_or_404(OrdenDeEntrega, id=orden_id, usuario=request.user, emitida=False)
        return render(request, self.plantilla, {'orden': orden})

    def post(self, request, orden_id):
        orden = get_object_or_404(OrdenDeEntrega, id=orden_id, usuario=request.user, emitida=False)
        orden.emitida = True
        orden.save()
        return redirect('ordenes_emitidas')

class EliminarOrdenEntregaController(LoginRequiredMixin, View):
    plantilla = 'confirmar-eliminar-orden-entrega.html'
    def get(self, request, orden_id):
        orden = get_object_or_404(OrdenDeEntrega, id=orden_id, usuario=request.user, emitida=False)
        return render(request, self.plantilla, {'orden': orden})

    def post(self, request, orden_id):
        orden = get_object_or_404(OrdenDeEntrega, id=orden_id, usuario=request.user, emitida=False)
        orden.delete()
        return redirect('orden_entrega')

class ConsultarOrdenEntregaController(LoginRequiredMixin, View):
    plantilla = 'consultar-orden-entrega.html'
    def get(self, request, orden_id):
        orden = get_object_or_404(OrdenDeEntrega, id=orden_id, usuario=request.user)
        return render(request, self.plantilla, {'orden': orden})

class DescargarOrdenEntregaPDFController(LoginRequiredMixin, View):
    def get(self, request, orden_id):
        orden = get_object_or_404(OrdenDeEntrega, id=orden_id, usuario=request.user, emitida=True)
        template = get_template('orden-entrega-pdf.html')
        html = template.render({'orden': orden})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="OrdenEntrega_{orden.numero_orden_entrega}.pdf"'
        pisa.CreatePDF(html, dest=response)
        return response

class OrdenesDashboardController(LoginRequiredMixin, View):
    plantilla = 'ordenes-dashboard.html'
    def get(self, request):
        return render(request, self.plantilla)