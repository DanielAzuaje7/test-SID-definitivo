from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.forms import inlineformset_factory
from .forms import NotaDebitoForm, NotaCreditoForm, ConceptoForm
from .models import Nota, Concepto
from Backend.facturas.models import Factura
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

class NotasDebitoCreditoController(LoginRequiredMixin, View):
    plantilla = 'notas-dashboard.html'
    def get(self, request):
        return render(request, self.plantilla)

class VerNotasDebitoController(LoginRequiredMixin, View):
    plantilla = 'notas-debito.html'
    def get(self, request):
        notas_debito = Nota.objects.filter(usuario=request.user, es_debito=True)
        return render(request, self.plantilla, {
            'notas_debito': notas_debito,  
            'usuario': request.user.username,
        })

class VerNotasCreditoController(LoginRequiredMixin, View):
    plantilla = 'notas-credito.html'
    def get(self, request):
        notas_credito = Nota.objects.filter(usuario=request.user, es_debito=False)
        return render(request, self.plantilla, {
            'notas_credito': notas_credito,
            'usuario': request.user.username,
        })

class CrearNotaDebitoController(LoginRequiredMixin, View):
    plantilla = 'crear-nota-debito.html'
    def get(self, request):
        ConceptoFormSet = inlineformset_factory(Nota, Concepto, form=ConceptoForm, extra=1, can_delete=True)
        form = NotaDebitoForm()
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ConceptoFormSet()
        return render(request, self.plantilla, {'form': form, 'formset': formset})

    def post(self, request):
        ConceptoFormSet = inlineformset_factory(Nota, Concepto, form=ConceptoForm, extra=1, can_delete=True)
        form = NotaDebitoForm(request.POST)
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ConceptoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            nota = form.save(commit=False)
            nota.usuario = request.user
            nota.subtotal = 0
            nota.iva = 0
            nota.total = 0
            nota.save()
            conceptos = formset.save(commit=False)
            for concepto in conceptos:
                concepto.nota = nota
                concepto.save()
            nota.subtotal = nota.calcular_subtotal()
            nota.iva = nota.calcular_iva()
            nota.total = nota.calcular_total()
            nota.save()
            return redirect('nota_debito')
        return render(request, self.plantilla, {'form': form, 'formset': formset})

class EditarNotaDebitoController(LoginRequiredMixin, View):
    plantilla = 'editar-nota-debito.html'
    def get(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=True)
        if nota.emitida:
            return redirect('nota_debito')
        ConceptoFormSet = inlineformset_factory(Nota, Concepto, form=ConceptoForm, extra=1, can_delete=True)
        form = NotaDebitoForm(instance=nota)
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ConceptoFormSet(instance=nota)
        return render(request, self.plantilla, {'form': form, 'formset': formset, 'nota_debito': nota})

    def post(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=True)
        if nota.emitida:
            return redirect('nota_debito')
        ConceptoFormSet = inlineformset_factory(Nota, Concepto, form=ConceptoForm, extra=1, can_delete=True)
        form = NotaDebitoForm(request.POST, instance=nota)
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ConceptoFormSet(request.POST, instance=nota)
        if form.is_valid() and formset.is_valid():
            nota = form.save(commit=False)
            nota.usuario = request.user
            nota.save()
            conceptos = formset.save(commit=False)
            for concepto in conceptos:
                concepto.nota = nota
                concepto.save()
            for concepto in formset.deleted_objects:
                concepto.delete()
            nota.subtotal = nota.calcular_subtotal()
            nota.iva = nota.calcular_iva()
            nota.total = nota.calcular_total()
            nota.save()
            return redirect('nota_debito')
        return render(request, self.plantilla, {'form': form, 'formset': formset, 'nota_debito': nota})

class CrearNotaCreditoController(LoginRequiredMixin, View):
    plantilla = 'crear-nota-credito.html'
    def get(self, request):
        ConceptoFormSet = inlineformset_factory(Nota, Concepto, form=ConceptoForm, extra=1, can_delete=True)
        form = NotaCreditoForm()
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ConceptoFormSet()
        return render(request, self.plantilla, {'form': form, 'formset': formset})

    def post(self, request):
        ConceptoFormSet = inlineformset_factory(Nota, Concepto, form=ConceptoForm, extra=1, can_delete=True)
        form = NotaCreditoForm(request.POST)
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ConceptoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            nota = form.save(commit=False)
            nota.usuario = request.user
            nota.subtotal = 0
            nota.iva = 0
            nota.total = 0
            nota.save()
            conceptos = formset.save(commit=False)
            for concepto in conceptos:
                concepto.nota = nota
                concepto.save()
            nota.subtotal = nota.calcular_subtotal()
            nota.iva = nota.calcular_iva()
            nota.total = nota.calcular_total()
            nota.save()
            return redirect('nota_credito')
        return render(request, self.plantilla, {'form': form, 'formset': formset})

class EditarNotaCreditoController(LoginRequiredMixin, View):
    plantilla = 'editar-nota-credito.html'
    def get(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=False)
        ConceptoFormSet = inlineformset_factory(Nota, Concepto, form=ConceptoForm, extra=1, can_delete=True)
        form = NotaCreditoForm(instance=nota)
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ConceptoFormSet(instance=nota)
        return render(request, self.plantilla, {'form': form, 'formset': formset, 'nota_credito': nota})

    def post(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=False)
        if 'emitir' in request.POST:
            nota.emitida = True
            nota.save()
            return redirect('editar-nota-credito', nota_id=nota.id)
        ConceptoFormSet = inlineformset_factory(Nota, Concepto, form=ConceptoForm, extra=1, can_delete=True)
        form = NotaCreditoForm(request.POST, instance=nota)
        form.fields['factura_afectada'].queryset = Factura.objects.filter(usuario=request.user)
        formset = ConceptoFormSet(request.POST, instance=nota)
        if form.is_valid() and formset.is_valid():
            nota = form.save(commit=False)
            nota.usuario = request.user
            nota.save()
            conceptos = formset.save(commit=False)
            for concepto in conceptos:
                concepto.nota = nota
                concepto.save()
            for concepto in formset.deleted_objects:
                concepto.delete()
            nota.subtotal = nota.calcular_subtotal()
            nota.iva = nota.calcular_iva()
            nota.total = nota.calcular_total()
            nota.save()
            return redirect('nota_credito')
        return render(request, self.plantilla, {'form': form, 'formset': formset, 'nota_credito': nota})

class EmitirNotaDebitoController(LoginRequiredMixin, View):
    def post(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=True)
        if not nota.emitida:
            nota.emitida = True
            nota.save()
        return redirect('nota_debito')

class EmitirNotaCreditoController(LoginRequiredMixin, View):
    def post(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=False)
        if not nota.emitida:
            nota.emitida = True
            nota.save()
        return redirect('nota_credito')

class ConfirmarEmisionNotaDebitoController(LoginRequiredMixin, View):
    plantilla = 'confirmar-emision-nota-debito.html'
    def get(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=True)
        if nota.emitida:
            return redirect('nota_debito')
        return render(request, self.plantilla, {'nota': nota})

    def post(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=True)
        if not nota.emitida:
            nota.emitida = True
            nota.save()
        return redirect('nota_debito')

class ConfirmarEmisionNotaCreditoController(LoginRequiredMixin, View):
    plantilla = 'confirmar-emision-nota-credito.html'
    def get(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=False)
        if nota.emitida:
            return redirect('nota_credito')
        return render(request, self.plantilla, {'nota': nota})

    def post(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=False)
        if not nota.emitida:
            nota.emitida = True
            nota.save()
        return redirect('nota_credito')

class VerNotasDebitoEmitidasController(LoginRequiredMixin, View):
    plantilla = 'notas-debito-emitidas.html'
    def get(self, request):
        notas_emitidas = Nota.objects.filter(usuario=request.user, es_debito=True, emitida=True)
        return render(request, self.plantilla, {
            'notas_emitidas': notas_emitidas,
            'usuario': request.user.username,
        })

class VerNotasCreditoEmitidasController(LoginRequiredMixin, View):
    plantilla = 'notas-credito-emitidas.html'
    def get(self, request):
        notas_emitidas = Nota.objects.filter(usuario=request.user, es_debito=False, emitida=True)
        return render(request, self.plantilla, {
            'notas_emitidas': notas_emitidas,
            'usuario': request.user.username,
        })

class EliminarNotaDebitoController(LoginRequiredMixin, View):
    plantilla = 'confirmar-eliminar-nota-debito.html'
    def get(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=True, emitida=False)
        return render(request, self.plantilla, {'nota': nota})

    def post(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=True, emitida=False)
        nota.delete()
        return redirect('nota_debito')

class EliminarNotaCreditoController(LoginRequiredMixin, View):
    plantilla = 'confirmar-eliminar-nota-credito.html'
    def get(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=False, emitida=False)
        return render(request, self.plantilla, {'nota': nota})

    def post(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=False, emitida=False)
        nota.delete()
        return redirect('nota_credito')

class ConsultarNotaDebitoController(LoginRequiredMixin, View):
    plantilla = 'consultar-nota-debito.html'
    def get(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=True)
        return render(request, self.plantilla, {'nota': nota})

class ConsultarNotaCreditoController(LoginRequiredMixin, View):
    plantilla = 'consultar-nota-credito.html'
    def get(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=False)
        return render(request, self.plantilla, {'nota': nota})

class DescargarNotaDebitoPDFController(LoginRequiredMixin, View):
    def get(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=True, emitida=True)
        template = get_template('nota-debito-pdf.html')
        html = template.render({'nota': nota})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="NotaDebito_{nota.numero_nota}.pdf"'
        pisa.CreatePDF(html, dest=response)
        return response

class DescargarNotaCreditoPDFController(LoginRequiredMixin, View):
    def get(self, request, nota_id):
        nota = get_object_or_404(Nota, id=nota_id, usuario=request.user, es_debito=False, emitida=True)
        template = get_template('nota-credito-pdf.html')
        html = template.render({'nota': nota})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="NotaCredito_{nota.numero_nota}.pdf"'
        pisa.CreatePDF(html, dest=response)
        return response