from django.shortcuts import render, redirect, get_object_or_404
from .forms import FacturaForm, ProductoFacturaFormSet, FacturaEditarForm
from .models import Factura
from django.views import View
from xhtml2pdf import pisa
from django.urls import reverse
from django.template.loader import render_to_string
from django.http import HttpResponse

class CrearFacturaController(View):
    plantilla_crear_factura = "crear_factura.html"

    def get(self, request):
        factura_form = FacturaForm(initial={'usuario': request.user})
        formset = ProductoFacturaFormSet()
        return render(request, self.plantilla_crear_factura, {
            'factura_form': factura_form,
            'formset': formset,
        })

    def post(self, request):
        factura_form = FacturaForm(request.POST)
        formset = ProductoFacturaFormSet(request.POST)
        if factura_form.is_valid() and formset.is_valid():
            factura = factura_form.save(commit=False)
            factura.usuario = request.user
            factura.save()
            # Aqqui está el cambio importante: pasa la instancia de factura al formset
            formset.instance = factura
            formset.save()
            # Calcula y guarda los totales después de guardar los productos
            factura.calcular_totales()
            factura.save(update_fields=['subtotal', 'iva', 'total'])
            return redirect('factura-creada', factura_id=factura.id)
        return render(request, self.plantilla_crear_factura, {
            'factura_form': factura_form,
            'formset': formset,
        })

class FacturaCreadaController(View):
    plantilla_factura_creada = "factura_creada.html"

    def get(self, request, factura_id):
        factura = get_object_or_404(Factura, id=factura_id)
        productos = factura.productos.all()
        return render(request, self.plantilla_factura_creada, {
            'factura': factura,
            'productos': productos,
        })
    
class GestionarFacturaController(View):
    plantilla_factura_creada = "gestionar_factura.html"

    def get(self, request, factura_id):
        factura = get_object_or_404(Factura, id=factura_id)
        productos = factura.productos.all()
        return render(request, self.plantilla_factura_creada, {
            'factura': factura,
            'productos': productos,
        })
    
class ConfirmarEmisionFactura(View):
    plantilla_factura_creada = "confirmar_emitir_factura.html"

    def get(self, request, factura_id):
        factura = get_object_or_404(Factura, id=factura_id)
        productos = factura.productos.all()
        if request.GET.get('emitir') == '1':
            factura.emitida = True
            factura.save(update_fields=['emitida'])
            return redirect(f"{reverse('factura-emitida')}?factura_id={factura.id}")
        return render(request, self.plantilla_factura_creada, {
            'factura': factura,
            'productos': productos,
        })
    
class FacturaEmitidaController(View):
    plantilla = "factura_emitida.html"

    def get(self, request):
        factura_id = request.GET.get('factura_id')
        factura = get_object_or_404(Factura, id=factura_id)
        return render(request, self.plantilla, {'factura': factura})
    
class ConfirmarBorrarFactura(View):
    plantilla_factura_creada = "confirmar_borrar_factura.html"

    def get(self, request, factura_id):
        factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
        productos = factura.productos.all()
        if request.GET.get('borrar') == '1':
            factura.delete()
            return redirect(f"{reverse('factura-borrada')}?factura_id={factura.id}")
        return render(request, self.plantilla_factura_creada, {
            'factura': factura,
            'productos': productos,
        })

class FacturaBorradaController(View):
    plantilla = "factura_borrada.html"

    def get(self, request):
        return render(request, self.plantilla)

class FacturaDashboardController(View):
    plantilla_factura_dashboard = "factura_dashboard.html"

    def get(self, request):
        facturas = Factura.objects.filter(usuario=request.user)
        return render(request, self.plantilla_factura_dashboard, {'facturas': facturas})
    
class EditarFacturaController(View):
    plantilla_editar_factura = "editar_factura.html"

    def get(self, request, factura_id):
        factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
        form = FacturaEditarForm(instance=factura)
        return render(request, self.plantilla_editar_factura, {'form': form, 'factura': factura})

    def post(self, request, factura_id):
        factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
        form = FacturaEditarForm(request.POST, instance=factura)
        if form.is_valid():
            form.save()
            return redirect('factura-editada', factura_id=factura.id)
        return render(request, self.plantilla_editar_factura, {'form': form, 'factura': factura})
    
class SeleccionarFacturaController(View):
    plantilla_seleccionar_factura = "seleccionar_factura_para_editar.html"

    def get(self, request):
        facturas = Factura.objects.filter(usuario=request.user, emitida=False)
        return render(request, self.plantilla_seleccionar_factura, {'facturas': facturas})
    
class SeleccionarFacturaEmitidaController(View):
    plantilla_seleccionar_factura = "seleccionar_factura_emitida.html"

    def get(self, request):
        facturas = Factura.objects.filter(usuario=request.user, emitida=True)
        return render(request, self.plantilla_seleccionar_factura, {'facturas': facturas})
    
class VerFacturaEmitidaController(View):
    plantilla = "ver_factura_emitida.html"

    def get(self, request, factura_id):
        factura = get_object_or_404(Factura, id=factura_id, usuario=request.user, emitida=True)
        productos = factura.productos.all()
        return render(request, self.plantilla, {
            'factura': factura,
            'productos': productos,
        })
    
class FacturaEditadaController(View):
    plantilla = 'facturas_editada.html'

    def get(self, request, factura_id):
        factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
        productos = factura.productos.all()
        return render(request, self.plantilla, {
            'factura': factura,
            'productos': productos,
        })
    
class DescargarFacturaPDFController(View):
    def get(self, request, factura_id):
        factura = get_object_or_404(Factura, id=factura_id)
        productos = factura.productos.all()
        html_string = render_to_string('factura_pdf.html', {
            'factura': factura,
            'productos': productos,
        })
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{factura.numero_factura or factura.id}_{factura.nombre_cliente}.pdf"'
        pisa_status = pisa.CreatePDF(html_string, dest=response)
        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=500)
        return response