# -*- coding: utf-8 -*-
# Create your views here.
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from boolean_app.models import Bancos, Condicion_venta, Articulo, Linea,\
    Rubro, Proveedor, Venta, Recibo, Detalle_cobro, Detalle_venta,\
    Cobranza_a_cuenta, Cobranza_credito_anterior, Valores, Compra, Detalle_pago,\
    ChequeTercero, Dinero, TransferenciaBancariaEntrante, ChequePropio,\
    TransferenciaBancariaSaliente, OrdenPago, Periodo, Cliente
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseRedirect, HttpResponse
from datetime import date, datetime, timedelta
from django.forms.formsets import BaseFormSet, formset_factory
from boolean_app.forms import DetalleVentaForm, FacturaForm,\
    SubdiarioIVAPeriodoFecha, DetalleCobroForm, ValoresForm, ReciboForm,\
    ActualizarPrecioRubrosForm, DetalleArticulosCompuestosForm,\
    VentasTotalesForm, ResumenCuentaForm, ComposicionSaldoForm,\
    DetalleCompraForm, ComprobanteCompraForm, DetallePagoForm, OrdenPagoForm,\
    ValoresOPForm, ValoresReciboForm, ProveedoresResumenCuentaForm,\
    ReciboContadoForm, DetalleCobroContadoForm, DetallePagoContadoForm,\
    OrdenPagoContadoForm, ProveedoresComposicionSaldoForm
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from boolean.settings import PUNTO_VENTA_FAA, PUNTO_VENTA_FAB, PUNTO_VENTA_NCA,\
    PUNTO_VENTA_NCB, PUNTO_VENTA_NDA, PUNTO_VENTA_NDB, PRIVATE_KEY_FILE,\
    CERT_FILE_PROD, RAZON_SOCIAL_EMPRESA, PRODUCCION
from pdb import set_trace
from decimal import Decimal
from boolean_app import utils
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from boolean_app.reports import IVAVentas, ResumenCuenta, ComposicionSaldo,\
    IVACompras, OrdenPagoReport, ResumenCuentaProveedores,\
    ComposicionSaldoProveedores
from geraldo.generators.pdf import PDFGenerator
from django.core import serializers
from django.db.models.aggregates import Sum
from boolean_app.utils import get_num_recibo, get_num_orden_pago
from django.db.models import Q
from operator import itemgetter
from afip_ws.wsaa import obtener_o_crear_permiso
from afip_ws.wsfev1 import WSFEV1
from StringIO import StringIO
import json


class Home(TemplateView):
    template_name = "home.html"
    
class ClientesList(ListView):
    template_name = "clientes/list.html"
    
    def get_queryset(self):
        return Cliente.objects.all().order_by("razon_social")
    
class ClientesNuevo(CreateView):
    model = Cliente
    template_name = "clientes/form.html"
    success_url = reverse_lazy("listaClientes")
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.modificado_por = self.request.user
        obj.save()
        return HttpResponseRedirect(reverse_lazy('listaClientes'))
    
class ClientesModificar(UpdateView):
    model = Cliente
    template_name = "clientes/form.html"
    success_url = reverse_lazy("listaClientes")
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.modificado_por = self.request.user
        obj.save()
        return HttpResponseRedirect(reverse_lazy('listaClientes'))
    
class ClientesBorrar(DeleteView):
    model = Cliente
    template_name = 'clientes/confirm_borrar.html'
    success_url = reverse_lazy('listaClientes')
    
class BancosList(ListView):
    template_name = "bancos/list.html"
    
    def get_queryset(self):
        return Bancos.objects.all().order_by("nombre")
    
class BancosNuevo(CreateView):
    model = Bancos
    template_name = "bancos/form.html"
    success_url = reverse_lazy("listaBancos")
    
class BancosModificar(UpdateView):
    model = Bancos
    template_name = "bancos/form.html"
    success_url = reverse_lazy("listaBancos")
    
class BancosBorrar(DeleteView):
    model = Bancos
    template_name = 'bancos/confirm_borrar.html'
    success_url = reverse_lazy('listaBancos')
    
class CondPagoList(ListView):
    template_name = "cond_pago/list.html"
    
    def get_queryset(self):
        return Condicion_venta.objects.all().order_by("descripcion")
    
class CondPagoNuevo(CreateView):
    model = Condicion_venta
    template_name = "cond_pago/form.html"
    success_url = reverse_lazy("listaCondPago")
    
class CondPagoModificar(UpdateView):
    model = Condicion_venta
    template_name = "cond_pago/form.html"
    success_url = reverse_lazy("listaCondPago")
    
class CondPagoBorrar(DeleteView):
    model = Condicion_venta
    template_name = 'cond_pago/confirm_borrar.html'
    success_url = reverse_lazy('listaCondPago')

class LineaList(ListView):
    template_name = "lineas/list.html"
    
    def get_queryset(self):
        return Linea.objects.all().order_by("nombre")
    
class LineaNuevo(CreateView):
    model = Linea
    template_name = "lineas/form.html"
    success_url = reverse_lazy("listaLineas")
    
class LineaModificar(UpdateView):
    model = Linea
    template_name = "lineas/form.html"
    success_url = reverse_lazy("listaLineas")
    
class LineaBorrar(DeleteView):
    model = Linea
    template_name = 'lineas/confirm_borrar.html'
    success_url = reverse_lazy('listaLineas')
    
class RubroList(ListView):
    template_name = "rubros/list.html"
    queryset = Rubro.objects.all().order_by("nombre")
    
class RubroNuevo(CreateView):
    model = Rubro
    template_name = "rubros/form.html"
    success_url = reverse_lazy("listaRubros")
    
class RubroModificar(UpdateView):
    model = Rubro
    template_name = "rubros/form.html"
    success_url = reverse_lazy("listaRubros")
    
class RubroBorrar(DeleteView):
    model = Rubro
    template_name = 'rubros/confirm_borrar.html'
    success_url = reverse_lazy('listaRubros')

class ArticuloList(ListView):
    template_name = "articulos/list.html"
    queryset = Articulo.objects.all().order_by("denominacion")
    
class ArticuloNuevo(CreateView):
    model = Articulo
    template_name = "articulos/form.html"
    success_url = reverse_lazy("listaArticulos")
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.fecha_ultima_compra = date.today()
        obj.ultima_actualizacion_precio = date.today()
        obj.modificado_por = self.request.user
        obj.save()
        return HttpResponseRedirect(reverse_lazy('listaArticulos'))
    
class ArticuloModificar(UpdateView):
    model = Articulo
    template_name = "articulos/form.html"
    success_url = reverse_lazy("listaArticulos")
    
class ArticuloBorrar(DeleteView):
    model = Condicion_venta
    template_name = 'cond_pago/confirm_borrar.html'
    success_url = reverse_lazy('listaCondPago')
    
class ProveedoresList(TemplateView):
    template_name = "proveedores/list.html"
    #queryset = Proveedor.objects.all().order_by("razon_social")
    
class ProveedoresNuevo(CreateView):
    model = Proveedor
    template_name = "proveedores/form.html"
    success_url = reverse_lazy("listaProveedores")
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.modificado_por = self.request.user
        obj.save()
        return HttpResponseRedirect(reverse_lazy('listaProveedores'))
    
class ProveedoresModificar(UpdateView):
    model = Proveedor
    template_name = "proveedores/form.html"
    success_url = reverse_lazy("listaProveedores")
    
class ProveedoresBorrar(DeleteView):
    model = Proveedor
    template_name = 'proveedores/confirm_borrar.html'
    success_url = reverse_lazy('listaProveedores')
    
class FacturasNuevo(CreateView):
    model = Venta
    template_name = "ventas/form_n.html"
    success_url = reverse_lazy('home')
    
def facturar(request):
    # This class is used to make empty formset forms required
    # See http://stackoverflow.com/questions/2406537/django-formsets-make-first-required/4951032#4951032
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False
                    
    DetalleArticuloCompuestoFormset = formset_factory(DetalleArticulosCompuestosForm)
    DetalleFormSet = formset_factory(DetalleVentaForm, formset=RequiredFormSet, extra=0)
    if request.method == 'POST': # If the form has been submitted...
        #Paso todos los campos en POST de cantidad que esten en tiempo a decimal
        CPOST = request.POST.copy()
        for k,v in CPOST.iteritems():
            if "cantidad" in k and ":" in v:
                entero = int(CPOST[k].split(":")[0])
                decimal = float(CPOST[k].split(":")[1])/60
                decimal = Decimal("%.3f" %decimal)
                CPOST[k]="%s" %(entero+decimal)
        articuloCompuestoFormset = DetalleArticuloCompuestoFormset(CPOST, prefix = 'art_comp')
        facturaForm = FacturaForm(CPOST) # A form bound to the POST data
        # Create a formset from the submitted data
        detalleFormset = DetalleFormSet(CPOST, prefix = 'det_venta')
        if facturaForm.is_valid() and detalleFormset.is_valid() and articuloCompuestoFormset.is_valid():
            factura = facturaForm.save(commit=False)
            periodo=Periodo.objects.filter(mes=factura.fecha.month,ano=factura.fecha.year)[0]
            factura.periodo=periodo
            #set_trace()
            factura.save()
            subtotal = 0
            for form in detalleFormset.forms:
                detalleItem = form.save(commit=False)
                if factura.tipo.endswith('A'):
                    sub = detalleItem.cantidad * detalleItem.precio_unitario
                    subtotal += sub - (sub*detalleItem.descuento/Decimal(100))
                elif factura.tipo.endswith('B'):    
                    sub= detalleItem.cantidad * (detalleItem.precio_unitario/Decimal(1.21))
                    subtotal += sub - (sub*detalleItem.descuento/Decimal(100))
            factura.subtotal = subtotal
            factura.neto = subtotal - (subtotal*factura.descuento/Decimal(100))
            factura.iva21 = factura.neto * Decimal("0.21")
            factura.iva105 = 0
            factura.total = factura.saldo = factura.neto + factura.iva21
            factura.save()
            #set_trace()
            if factura.tipo.startswith("FA") or factura.tipo.startswith("ND"):
                print "ESTO ES:  %s" %factura.tipo
                print "SALDO DEL CLIENTE: %s" %factura.cliente.saldo
                saldo_temp = factura.saldo
                if factura.cliente.saldo < 0:#Esto significa que hay NC con saldos a descontar
                    otros_comp=Venta.objects.filter(Q(cliente=factura.cliente), Q(tipo__startswith="NC"), ~Q(saldo=0)).order_by('fecha','numero')
                    #print "Otros comprob:  " %otros_comp
                    if otros_comp:
                        for comp in otros_comp:
                            if factura.saldo == 0:
                                break
                            if factura.saldo >= comp.saldo:
                                factura.saldo -= comp.saldo
                                comp.saldo = 0
                                comp.save()
                            else:
                                comp.saldo -= factura.saldo
                                factura.saldo = 0
                                comp.save()
                factura.save()
                factura.cliente.saldo += saldo_temp
                factura.cliente.save()
            if factura.tipo.startswith("NC"):
                print "ESTO ES:  %s" %factura.tipo
                saldo_temp = factura.saldo
                factura.pagado=True
                if factura.comprobante_relacionado.total-Decimal('0.009') < factura.total < factura.comprobante_relacionado.total+Decimal('0.009'):
                    factura.comprobante_relacionado.pagado = True
                    factura.comprobante_relacionado.save()
                #Resto de los saldos de otros comprobantes
                print factura.cliente.saldo
                print factura.cliente.saldo > 0
                if factura.cliente.saldo > 0:#Esto significa que hay FA o ND con saldos a descontar
                    print "SI HAY SALDO"
                    otros_comp=Venta.objects.filter(Q(cliente=factura.cliente), Q(tipo__startswith="FA") | Q(tipo__startswith="ND"), ~Q(saldo=0)).order_by('fecha','numero')
                    print otros_comp
                    if otros_comp:
                        for comp in otros_comp:
                            print "COMP %s" %comp.numero
                            if factura.saldo == 0:
                                break
                            if factura.saldo >= comp.saldo:
                                print "SIIIIIII"
                                factura.saldo -= comp.saldo
                                comp.saldo = 0
                                comp.pagado = True
                                comp.save()
                            else:
                                comp.saldo -= factura.saldo
                                factura.saldo = 0
                                comp.save()
                factura.save()
                factura.cliente.saldo -= saldo_temp
                factura.cliente.save()
            #factura.comprobante_relacionado.save()
            dict_forms={}
            i = 0
            for form in detalleFormset.forms:
                detalleItem = form.save(commit=False)
                if factura.tipo.endswith('B'):
                    detalleItem.precio_unitario = detalleItem.precio_unitario/Decimal(1.21)
                detalleItem.venta = factura
                if detalleItem.articulo_personalizado != "":
                    detalleItem.articulo = None
                detalleItem.save()
                dict_forms[i]=detalleItem
                i+=1
            for form in articuloCompuestoFormset.forms:
                if len(form.cleaned_data) > 0:
                    id_deta = form.cleaned_data['id_detalle_venta']
                    articuloCompuesto = form.save(commit=False)
                    #Si es factura B, quito el iva.
                    articuloCompuesto.detalle_venta = dict_forms[int(id_deta)]
                    articuloCompuesto.precio_unitario = articuloCompuesto.precio_unitario/Decimal('1.21') if \
                    articuloCompuesto.detalle_venta.venta.tipo[-1:]=='B' else articuloCompuesto.precio_unitario
                    articuloCompuesto.descuento = dict_forms[int(id_deta)].descuento
                    articuloCompuesto.save()
            #set_trace()
            return HttpResponseRedirect(reverse_lazy('listarPendientes'))
            
    else:
        facturaForm = FacturaForm()
        detalleFormset = DetalleFormSet(initial=[{'descuento':'0.00',}], prefix = 'det_venta')
        articuloCompuestoFormset = DetalleArticuloCompuestoFormset(prefix = 'art_comp')
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    #set_trace()
    c = {'facturaForm': facturaForm,
         'detalleFormset': detalleFormset,
         'articuloCompuestoFormset': articuloCompuestoFormset,
        }
    c.update(csrf(request))

    return render_to_response('ventas/fact.html', c)

def get_punto_venta(request, tipo_comprobante):
    if tipo_comprobante == "FAA":
        return HttpResponse(PUNTO_VENTA_FAA, content_type='text/plain')
    elif tipo_comprobante == "FAB":
        return HttpResponse(PUNTO_VENTA_FAB, content_type='text/plain')
    elif tipo_comprobante == "NCA":
        return HttpResponse(PUNTO_VENTA_NCA, content_type='text/plain')
    elif tipo_comprobante == "NCB":
        return HttpResponse(PUNTO_VENTA_NCB, content_type='text/plain')
    elif tipo_comprobante == "NDA":
        return HttpResponse(PUNTO_VENTA_NDA, content_type='text/plain')
    elif tipo_comprobante == "NDB":
        return HttpResponse(PUNTO_VENTA_NDB, content_type='text/plain')
    
def get_num_prox_comprobante(request, tipo_comprobante):
    list_comprob = Venta.objects.filter(tipo__exact=tipo_comprobante,aprobado__exact=True).order_by('-numero')
    #list_comprob = Venta.objects.filter(tipo__endswith=tipo_comprobante[-1:],aprobado__exact=True).order_by('-numero')
    if len(list_comprob) != 0:
        return HttpResponse(list_comprob[0].numero+1, content_type='text/plain')
    else:
        return HttpResponse(1, content_type='text/plain')
    
def get_precio_unitario(request, pk):
    art = Articulo.objects.get(pk=pk)
    return HttpResponse(art.precio_venta, content_type='text/plain')

def get_precio_unitario_iva_inc(request, pk):
    art = Articulo.objects.get(pk=pk)
    return HttpResponse(art.precio_venta_iva_inc, content_type='text/plain')
    
class ListarComprobantesPendientesDeAprobacion(ListView):
    queryset = Venta.objects.filter(aprobado=False)
    template_name = "ventas/ap_comp.html" 
    
class AprobarComprobante(TemplateView):
    template_name = "ventas/aprobar_comp.html"
    
    def get_context_data(self, **kwargs):
        context = super(AprobarComprobante, self).get_context_data(**kwargs)
    
def afip_aprob(request,pk):
    venta = Venta.objects.get(pk=pk)
    if venta.aprobado:
        print "Comprobante ya aprobado"
        err=['Este comprobante ya ha sido aprobado.']
        print "Len de err: "+ str(len(err))
        return render_to_response('ventas/rechazado.html',{'err':err})
    #set_trace()
    wsaa = obtener_o_crear_permiso(produccion=PRODUCCION)
    print "Obtenido permiso: " 
    print wsaa
    #tra = wsaa.CreateTRA(service="wsfe")
    #cms = wsaa.SignTRA(tra, CERT_FILE_PROD, PRIVATE_KEY_FILE)
    #wsaa.Conectar()
    #wsaa.LoginCMS(cms)
    #token = wsaa.get_token()
    #sign = wsaa.get_sign()
    
    tc = utils.get_tipo_comp_afip(venta)
    pv = str(utils.get_pto_vta(venta))
    cd = ch = utils.get_num_comp(venta)
    imt = "%.2f" %venta.total
    imn = "%.2f" %venta.neto
    imi = "%.2f" %venta.iva21
    fec = venta.fecha.strftime('%Y%m%d')
    ndo = venta.cliente.cuit.replace('-','')
    #set_trace()    
    fact = WSFEV1(wsaa)
    fact.nuevaSolicitudAprobacion(concepto=1, tipo_doc=80, nro_doc=ndo, tipo_cbte=tc,\
                                  punto_vta=pv, cbt_desde=cd, cbt_hasta=ch, imp_total=imt,\
                                  imp_tot_conc=0.00, imp_neto=imn, imp_iva=imi,\
                                  fecha_cbte=fec, fecha_venc_pago="", fecha_serv_hasta=None,\
                                  moneda_id="PES", moneda_ctz="1.0000")
    print "Nuevo comprobante"
    iva_id = 5 # 21%
    base_imp = imn
    importe = imi
    fact.agregarIva(iva_id, base_imp, importe)
    print "Agregado IVA"
    #fact.SetParametros(cuit="20149443984", token=token, sign=sign)
    # Asociar comprobantes!! 
    if venta.comprobante_relacionado:
        tcca = utils.get_tipo_comp_afip(venta.comprobante_relacionado)
        pvca = str(utils.get_pto_vta(venta.comprobante_relacionado))
        fact.agregarCmpAsoc(tcca, pvca, venta.comprobante_relacionado.numero)
    #fact.Conectar(wsdl=WSFEV1)
    #print fact.CompUltimoAutorizado(3, 3)
    print "Solicitando CAE"
    if fact.CAESolicitar():
        print "Obtenido CAE"
        cae = fact.CAE
        cae_venc = fact.CAE_VENC
        print cae_venc
        venta.punto_venta = utils.get_pto_vta(venta)
        venta.numero = utils.get_num_comp(venta)
        venta.aprobado = True
        venta.cae = cae
        venta.fvto_cae = cae_venc
        venta.save()
        obs=[]
        if fact.OBS:
            obs=fact.OBS
        return render_to_response('ventas/aprobado.html',{'comprobante':venta,'obs':obs})
    else:
        print "No se ha obtenido el CAE"
        err=fact.ERRORS_SOLICITUD
        print "Len de err: "+ str(len(err))
        obs=fact.OBS
        return render_to_response('ventas/rechazado.html',{'obs':obs,'err':err})

def iva_periodo_fecha(request):
    if request.method == 'POST':
        subdiario = SubdiarioIVAPeriodoFecha(request.POST)
        if subdiario.is_valid():
            per = subdiario.cleaned_data['periodo']
            fd = subdiario.cleaned_data['fecha_desde']
            fh = subdiario.cleaned_data['fecha_hasta']
            fi = subdiario.cleaned_data['folio_inicial']            
            resp = HttpResponse(mimetype='application/pdf')
            if per:
                ventas = Venta.objects.filter(periodo=per, aprobado=True).order_by('fecha','tipo','numero')
                #set_trace()
                #ivav = IVAVentas(queryset=ventas,periodo=per,folio_inicial=fi)
                ivav = IVAVentas(queryset=ventas,fpn=fi)
                #ivav.first_page_number = fi
                ivav.generate_by(PDFGenerator, filename=resp, variables={'periodo': per.periodo_full()})
                return resp
            else:
                if fh and fd:
                    ventas = Venta.objects.filter(fecha__range=(fd, fh), aprobado=True).order_by('fecha','tipo','numero')
                    ivav = IVAVentas(queryset=ventas,fpn=fi)
                    ivav.generate_by(PDFGenerator, filename=resp, variables={'periodo': 'N/A'})
                    return resp
    else:
        subdiario = SubdiarioIVAPeriodoFecha()
        
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'subdiario': subdiario,
        }
    c.update(csrf(request))

    return render_to_response('informes/sub_iva_params.html', c)

def recibo(request):
    # This class is used to make empty formset forms required
    # See http://stackoverflow.com/questions/2406537/django-formsets-make-first-required/4951032#4951032
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False
                    
    DetalleCobroFormSet = formset_factory(DetalleCobroForm, formset=RequiredFormSet)
    #ValoresFormSet = formset_factory(ValoresReciboForm, formset=RequiredFormSet)
    ValoresFormSet = formset_factory(ValoresReciboForm)
    if request.method == 'POST': # If the form has been submitted...
        reciboForm = ReciboForm(request.POST) # A form bound to the POST data
        # Create a formset from the submitted data
        cobroFormset = DetalleCobroFormSet(request.POST, prefix='cobros')
        valoresFormset = ValoresFormSet(request.POST, prefix='valores')
        #set_trace()
        print reciboForm.is_valid()
        print reciboForm.errors 
        print cobroFormset.is_valid() 
        print valoresFormset.is_valid()
        if reciboForm.is_valid() and cobroFormset.is_valid() and valoresFormset.is_valid():
            #Inicializo variables de trabajo
            total_comprobantes=0#Suma de comprobantes cancelados, se usa en para calculo de credito a favor o vuelto
            recibo = reciboForm.save(commit=False)
            recibo.numero = get_num_recibo()#Obtengo numero de recibo, el ultimo mas 1            
            #Veo que dinero de este cliente es el que tiene el saldo a favor, de encontrarlo lo dejo en 0
            try:
                cheq=Dinero.objects.filter(Q(recibo__cliente=recibo.cliente), ~Q(pendiente_para_recibo=0))[0]
                cred_ant = cheq.pendiente_para_recibo
                cheq.pendiente_para_recibo=0
                cheq.save()
            except IndexError:
                pass
            
            #cred_ant=recibo.cliente.saldo#Obtengo el credito del cliente, que quedaria pendiente del recibo anterior
            print "Credito anterior: %s" %cred_ant
            recibo.credito_anterior=cred_ant
            recibo.save()
            
            '''
            Para cada uno de los detalles de cobro ingresados, creo el registro y verifico si el comprobante esta
            pagado, para ello busco todos los detalles de este comprobante y los sumo.
            '''
            for detalle_cobro in cobroFormset.forms:
                if detalle_cobro.cleaned_data['pagar']:
                    if Decimal(detalle_cobro.cleaned_data['pagar'])>0:
                        total_comprobantes+=detalle_cobro.cleaned_data['pagar']
                        ve = Venta.objects.get(pk=detalle_cobro.cleaned_data['id_factura'])
                        Detalle_cobro.objects.create(recibo=recibo, venta=ve, monto=detalle_cobro.cleaned_data['pagar'])
                        #Ya estan creados todos detalle de cobro de esta factura. Reviso si la factura esta completamente pagada.
                        cobrado_total = Detalle_cobro.objects.filter(venta=ve).aggregate(Sum('monto'))
                        print cobrado_total
                        nc_total = Venta.objects.filter(comprobante_relacionado=ve).aggregate(Sum('total'))
                        print nc_total
                        todo_f = cobrado_total['monto__sum'] if cobrado_total['monto__sum'] else Decimal('0.00')
                        todo_nc =  nc_total['total__sum'] if nc_total['total__sum'] else Decimal('0.00')
                        todo = todo_f + todo_nc
                        print todo
                        print ve.total-Decimal('0.009')
                        print ve.total+Decimal('0.009')
                        if (ve.total-Decimal('0.009') <= todo <= ve.total+Decimal('0.009')):
                            ve.pagado=True
                            ve.save()
            total_comp = total_comprobantes
            #Cubro los comprobantes con el credito
            '''if total_comprobantes <= cred_ant + Decimal(0.009):
                #Descuento de o cancelo el saldo de cliente
                recibo.cliente.saldo-=total_comprobantes
                recibo.cliente.save()
                recibo.credito_anterior=total_comprobantes
                val=ChequeTercero.objects.filter(recibo__cliente=recibo.cliente, pendiente_para_recibo__gt=0)[0]
                val.pendiente_para_recibo-=total_comprobantes
                val.save()
                obj = {'id':recibo.id}
                s = StringIO()
                json.dump(obj,s)
                s.seek(0)
                return HttpResponse(s.read())'''
            #recibo.cliente.saldo=0#Dejo el saldo del cliente en 0
            recibo.cliente.saldo -= total_comp
            recibo.cliente.save()
            '''#Quito el pendiente del ultimo cheque
            lala=ChequeTercero.objects.filter(recibo__cliente=recibo.cliente).order_by('-pendiente_para_recibo')[0]
            lala.pendiente_para_recibo=0
            lala.save()'''
            total_val=0
            for valor in valoresFormset.forms:
                total_val+=valor.cleaned_data['monto']
                #set_trace()
                if valor.cleaned_data['monto'] <= total_comprobantes+Decimal(0.009)-cred_ant:
                    total_comprobantes-=valor.cleaned_data['monto']
                    if valor.cleaned_data['tipo']=='CHT':
                        ChequeTercero.objects.create(recibo=recibo,\
                                                     numero=valor.cleaned_data['cheque_numero'],\
                                                     fecha=valor.cleaned_data['cheque_fecha'],\
                                                     cobro=valor.cleaned_data['cheque_cobro'],\
                                                     paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                     titular=valor.cleaned_data['cheque_titular'],\
                                                     cuit_titular=valor.cleaned_data['cheque_cuit_titular'],\
                                                     banco=valor.cleaned_data['cheque_banco'],\
                                                     en_cartera=True,\
                                                     domicilio_de_pago=valor.cleaned_data['cheque_domicilio_de_pago'],\
                                                     pendiente_para_recibo=0,\
                                                     pendiente_para_orden_pago=0,\
                                                     monto=valor.cleaned_data['monto'])
                    elif valor.cleaned_data['tipo']=='EFE':
                        Dinero.objects.create(monto=valor.cleaned_data['monto'], recibo=recibo,\
                                              pendiente_para_recibo=0,\
                                              pendiente_para_orden_pago=0)
                    elif valor.cleaned_data['tipo']=='TRB':
                        TransferenciaBancariaEntrante.objects.create(recibo=recibo,\
                                                                     banco_origen=valor.cleaned_data['transferencia_banco_origen'],\
                                                                     cuenta_origen=valor.cleaned_data['transferencia_cuenta_origen'],\
                                                                     numero_operacion=valor.cleaned_data['transferencia_numero_operacion'],\
                                                                     cuenta_destino=valor.cleaned_data['transferencia_cuenta_destino'],\
                                                                     monto=valor.cleaned_data['monto'],\
                                                                     pendiente_para_recibo=0,\
                                                                     pendiente_para_orden_pago=0)
                else:
                    total_comprobantes-=cred_ant
                    if reciboForm.cleaned_data['que_hago_con_diferencia']=='vuelto':
                        if valor.cleaned_data['tipo']=='CHT':
                            ChequeTercero.objects.create(recibo=recibo,\
                                                     numero=valor.cleaned_data['cheque_numero'],\
                                                     fecha=valor.cleaned_data['cheque_fecha'],\
                                                     cobro=valor.cleaned_data['cheque_cobro'],\
                                                     paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                     titular=valor.cleaned_data['cheque_titular'],\
                                                     cuit_titular=valor.cleaned_data['cheque_cuit_titular'],\
                                                     banco=valor.cleaned_data['cheque_banco'],\
                                                     en_cartera=True,\
                                                     domicilio_de_pago=valor.cleaned_data['cheque_domicilio_de_pago'],\
                                                     pendiente_para_recibo=0,\
                                                     pendiente_para_orden_pago=0,\
                                                     monto=valor.cleaned_data['monto'])
                        elif valor.cleaned_data['tipo']=='EFE':
                            Dinero.objects.create(monto=valor.cleaned_data['monto'], recibo=recibo,\
                                                  pendiente_para_recibo=0,\
                                                  pendiente_para_orden_pago=0)
                        elif valor.cleaned_data['tipo']=='TRB':
                            TransferenciaBancariaEntrante.objects.create(recibo=recibo,\
                                                                     banco_origen=valor.cleaned_data['transferencia_banco_origen'],\
                                                                     cuenta_origen=valor.cleaned_data['transferencia_cuenta_origen'],\
                                                                     numero_operacion=valor.cleaned_data['transferencia_numero_operacion'],\
                                                                     cuenta_destino=valor.cleaned_data['transferencia_cuenta_destino'],\
                                                                     monto=valor.cleaned_data['monto'],\
                                                                     pendiente_para_recibo=0,\
                                                                     pendiente_para_orden_pago=0)
                        Dinero.objects.create(recibo=recibo, monto=(valor.cleaned_data['monto']-total_comprobantes)*-1)
                    elif reciboForm.cleaned_data['que_hago_con_diferencia']=='credito':
                        if valor.cleaned_data['tipo']=='CHT':
                            ChequeTercero.objects.create(recibo=recibo,\
                                                         numero=valor.cleaned_data['cheque_numero'],\
                                                         fecha=valor.cleaned_data['cheque_fecha'],\
                                                         cobro=valor.cleaned_data['cheque_cobro'],\
                                                         paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                         titular=valor.cleaned_data['cheque_titular'],\
                                                         cuit_titular=valor.cleaned_data['cheque_cuit_titular'],\
                                                         banco=valor.cleaned_data['cheque_banco'],\
                                                         en_cartera=True,\
                                                         domicilio_de_pago=valor.cleaned_data['cheque_domicilio_de_pago'],\
                                                         pendiente_para_recibo=valor.cleaned_data['monto']-total_comprobantes,\
                                                         pendiente_para_orden_pago=0,\
                                                         monto=valor.cleaned_data['monto'])
                        elif valor.cleaned_data['tipo']=='EFE':
                            Dinero.objects.create(monto=valor.cleaned_data['monto'], recibo=recibo,\
                                                  pendiente_para_recibo=valor.cleaned_data['monto']-total_comprobantes,\
                                                  pendiente_para_orden_pago=0)
                        elif valor.cleaned_data['tipo']=='TRB':
                            TransferenciaBancariaEntrante.objects.create(recibo=recibo,\
                                                                     banco_origen=valor.cleaned_data['transferencia_banco_origen'],\
                                                                     cuenta_origen=valor.cleaned_data['transferencia_cuenta_origen'],\
                                                                     numero_operacion=valor.cleaned_data['transferencia_numero_operacion'],\
                                                                     cuenta_destino=valor.cleaned_data['transferencia_cuenta_destino'],\
                                                                     monto=valor.cleaned_data['monto'],\
                                                                     pendiente_para_recibo=valor.cleaned_data['monto']-total_comprobantes,\
                                                                     pendiente_para_orden_pago=0)
                        recibo.cliente.saldo=valor.cleaned_data['monto']-total_comprobantes
                        recibo.cliente.save()
                        recibo.a_cuenta=total_val-total_comp-cred_ant
                        recibo.save()                    
            obj = {'id':recibo.id}
            s = StringIO()
            json.dump(obj,s)
            s.seek(0)
            return HttpResponse(s.read())
            
    else:
        reciboForm = ReciboForm()
        cobroFormset = DetalleCobroFormSet(prefix='cobros')
        valoresFormset = ValoresFormSet(prefix='valores')
        
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    #set_trace()
    c = {'reciboForm': reciboForm,
         'cobroFormset': cobroFormset,
         'valoresFormset': valoresFormset,
        }
    c.update(csrf(request))

    return render_to_response('ventas/recibo_new.html', c)

def recibo_contado(request,venta):
    # This class is used to make empty formset forms required
    # See http://stackoverflow.com/questions/2406537/django-formsets-make-first-required/4951032#4951032
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False
                    
    DetalleCobroFormSet = formset_factory(DetalleCobroContadoForm, extra=0)
    #ValoresFormSet = formset_factory(ValoresReciboForm, formset=RequiredFormSet)
    ValoresFormSet = formset_factory(ValoresReciboForm)
    if request.method == 'POST': # If the form has been submitted...
        reciboForm = ReciboContadoForm(request.POST) # A form bound to the POST data
        # Create a formset from the submitted data
        cobroFormset = DetalleCobroFormSet(request.POST, prefix='cobros')
        valoresFormset = ValoresFormSet(request.POST, prefix='valores')
        #set_trace()
        if reciboForm.is_valid() and cobroFormset.is_valid() and valoresFormset.is_valid():
            recibo = reciboForm.save(commit=False)
            #recibo.cliente=Cliente.objects.get(pk=reciboForm.cleaned_data['id_cliente'])
            recibo.numero = get_num_recibo()
            #if Decimal(reciboForm.cleaned_data['credito_anterior']) > 0:
                #Lo uso en la impresion de los recibos, NO lo voy a hacer con un metodo.
            #    Cobranza_credito_anterior.objects.create(recibo=recibo,monto=reciboForm.cleaned_data['credito_anterior'])
            try:
                cheq=Dinero.objects.filter(Q(recibo__cliente=recibo.cliente), ~Q(pendiente_para_recibo=0))[0]
                cred_ant = cheq.pendiente_para_recibo
                cheq.pendiente_para_recibo=0
                cheq.save()
            except IndexError:
                pass
            #cred_ant=recibo.cliente.saldo#Obtengo el credito del cliente, que quedaria pendiente del recibo anterior
            print "Credito anterior: %s" %cred_ant
            recibo.credito_anterior=cred_ant
            recibo.save()
            for detalle_cobro in cobroFormset.forms:
                ve = Venta.objects.get(pk=detalle_cobro.cleaned_data['id_factura'])
                Detalle_cobro.objects.create(recibo=recibo, venta=ve, monto=ve.total)
                total_comprobantes=ve.total
                ve.pagado=True
                ve.save()
            print total_comprobantes
            if total_comprobantes <= cred_ant + Decimal(0.009):#Cubro los comprobantes con el credito
                #Descuento de o cancelo el saldo de cliente
                recibo.cliente.saldo-=total_comprobantes
                recibo.cliente.save()
                recibo.credito_anterior=total_comprobantes
                val=ChequeTercero.objects.filter(recibo__cliente=recibo.cliente, pendiente_para_recibo__gt=0)[0]
                val.pendiente_para_recibo-=total_comprobantes
                val.save()
                obj = {'id':recibo.id}
                s = StringIO()
                json.dump(obj,s)
                s.seek(0)
                return HttpResponse(s.read())
            else:
                #Dejo el saldo del cliente en 0
                recibo.cliente.saldo -= total_comprobantes
                recibo.cliente.save()
                for valor in valoresFormset.forms:
                    #set_trace()
                    if valor.cleaned_data['monto'] <= total_comprobantes+Decimal(0.009)-cred_ant:
                        total_comprobantes-=valor.cleaned_data['monto']
                        if valor.cleaned_data['tipo']=='CHT':
                            ChequeTercero.objects.create(recibo=recibo,\
                                                         numero=valor.cleaned_data['cheque_numero'],\
                                                         fecha=valor.cleaned_data['cheque_fecha'],\
                                                         cobro=valor.cleaned_data['cheque_cobro'],\
                                                         paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                         titular=valor.cleaned_data['cheque_titular'],\
                                                         cuit_titular=valor.cleaned_data['cheque_cuit_titular'],\
                                                         banco=valor.cleaned_data['cheque_banco'],\
                                                         en_cartera=True,\
                                                         domicilio_de_pago=valor.cleaned_data['cheque_domicilio_de_pago'],\
                                                         pendiente_para_recibo=0,\
                                                         pendiente_para_orden_pago=0,\
                                                         monto=valor.cleaned_data['monto'])
                        elif valor.cleaned_data['tipo']=='EFE':
                            Dinero.objects.create(monto=valor.cleaned_data['monto'], recibo=recibo)
                        elif valor.cleaned_data['tipo']=='TRB':
                            TransferenciaBancariaEntrante.objects.create(recibo=recibo,\
                                                                         banco_origen=valor.cleaned_data['transferencia_banco_origen'],\
                                                                         cuenta_origen=valor.cleaned_data['transferencia_cuenta_origen'],\
                                                                         numero_operacion=valor.cleaned_data['transferencia_numero_operacion'],\
                                                                         cuenta_destino=valor.cleaned_data['transferencia_cuenta_destino'],\
                                                                         monto=valor.cleaned_data['monto'])
                    else:
                        total_comprobantes-=cred_ant
                        if reciboForm.cleaned_data['que_hago_con_diferencia']=='vuelto':
                            if valor.cleaned_data['tipo']=='CHT':
                                ChequeTercero.objects.create(recibo=recibo,\
                                                         numero=valor.cleaned_data['cheque_numero'],\
                                                         fecha=valor.cleaned_data['cheque_fecha'],\
                                                         cobro=valor.cleaned_data['cheque_cobro'],\
                                                         paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                         titular=valor.cleaned_data['cheque_titular'],\
                                                         cuit_titular=valor.cleaned_data['cheque_cuit_titular'],\
                                                         banco=valor.cleaned_data['cheque_banco'],\
                                                         en_cartera=True,\
                                                         domicilio_de_pago=valor.cleaned_data['cheque_domicilio_de_pago'],\
                                                         pendiente_para_recibo=0,\
                                                         pendiente_para_orden_pago=0,\
                                                         monto=valor.cleaned_data['monto'])
                                Dinero.objects.create(recibo=recibo, monto=(valor.cleaned_data['monto']-total_comprobantes)*-1)
                        elif reciboForm.cleaned_data['que_hago_con_diferencia']=='credito':
                            ChequeTercero.objects.create(recibo=recibo,\
                                                         numero=valor.cleaned_data['cheque_numero'],\
                                                         fecha=valor.cleaned_data['cheque_fecha'],\
                                                         cobro=valor.cleaned_data['cheque_cobro'],\
                                                         paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                         titular=valor.cleaned_data['cheque_titular'],\
                                                         cuit_titular=valor.cleaned_data['cheque_cuit_titular'],\
                                                         banco=valor.cleaned_data['cheque_banco'],\
                                                         en_cartera=True,\
                                                         domicilio_de_pago=valor.cleaned_data['cheque_domicilio_de_pago'],\
                                                         pendiente_para_recibo=valor.cleaned_data['monto']-total_comprobantes,\
                                                         pendiente_para_orden_pago=0,\
                                                         monto=valor.cleaned_data['monto'])
                            recibo.cliente.saldo=valor.cleaned_data['monto']-total_comprobantes
                            recibo.cliente.save()
                obj = {'id':recibo.id}
                s = StringIO()
                json.dump(obj,s)
                s.seek(0)
                return HttpResponse(s.read())
            
    else:
        venta=Venta.objects.get(pk=venta)
        reciboForm = ReciboContadoForm(initial={'cliente':venta.cliente})
        cobroFormset = DetalleCobroFormSet(prefix='cobros', initial=[{'id_factura':venta.pk,'pagar':venta.total}])
        valoresFormset = ValoresFormSet(prefix='valores')
        
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    #set_trace()
    c = {'reciboForm': reciboForm,
         'cobroFormset': cobroFormset,
         'valoresFormset': valoresFormset,
         'venta':venta,
        }
    c.update(csrf(request))

    return render_to_response('ventas/recibo_contado_new.html', c)
        
def get_num_prox_recibo(request):
    #list_recibo = Venta.objects.filter(tipo__exact=tipo_comprobante,aprobado__exact=True).order_by('-numero')
    list_recibo = Recibo.objects.all().order_by('-numero')
    if len(list_recibo) != 0:
        return HttpResponse(list_recibo[0].numero+1, content_type='text/plain')
    else:
        return HttpResponse(1, content_type='text/plain') 

def get_num_prox_orden_pago(request):
    return HttpResponse(get_num_orden_pago(), content_type='text/plain')   
    
def get_facturas_pendiente_pago(request, cliente):
    cli = Cliente.objects.get(pk=cliente)
    vtas = Venta.objects.filter(cliente=cli, pagado=False)
    data = serializers.serialize("json", vtas, fields=('fecha','total', 'punto_venta', 'numero'), extras=('saldo',))
    return HttpResponse(data, content_type="text/plain")

def get_facturas_pendiente_pago_prov(request, proveedor):
    pro = Proveedor.objects.get(pk=proveedor)
    cpras = Compra.objects.filter(Q(proveedor=pro), ~Q(saldo=0), ~Q(tipo__startswith='NC'))
    data = serializers.serialize("json", cpras, fields=('fecha', 'punto_venta', 'numero','tipo'), extras=('saldo','total'))
    return HttpResponse(data, content_type="text/plain")

def actualizarPreciosRubro(request, rubro):
    if request.method == 'POST':
        actualizador = ActualizarPrecioRubrosForm(request.POST)
        if actualizador.is_valid():
            rub = Rubro.objects.get(pk=actualizador.cleaned_data['rubro'])
            porc = actualizador.cleaned_data['porcentaje']
            arts = Articulo.objects.filter(rubro=rub)
            for art in arts:
                nuevo_precio = art.costo_compra+(art.costo_compra*Decimal(porc)/Decimal(100))
                art.ultima_actualizacion_precio = datetime.today().date()
                art.costo_compra = nuevo_precio
                art.save()
            return HttpResponseRedirect(reverse_lazy('home'))
    
    else:
        actualizador = ActualizarPrecioRubrosForm(initial={'rubro':rubro})
        nombre_rubro=Rubro.objects.get(pk=rubro).nombre
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'actualizador': actualizador,
         'nombre_rubro': nombre_rubro
        }
    c.update(csrf(request))

    return render_to_response('articulos/actualizar_precio.html', c)
    
class ComprobantesList(TemplateView):
    template_name = "ventas/list.html"
    
class CobrosList(TemplateView):
    template_name = "cobranza/list.html"
    
def ventas_totales_fecha(request):
    lineas_neto = {}
    lineas_iva = {}
    lineas_total = {}
    if request.method == 'POST':
        ventast = VentasTotalesForm(request.POST)
        if ventast.is_valid():
            fd = ventast.cleaned_data['fecha_desde']
            fh = ventast.cleaned_data['fecha_hasta']
            response = HttpResponse(mimetype='application/pdf')
            if fh and fd:
                lineas = Linea.objects.all()
                for linea in lineas:
                    lineas_neto[linea.nombre]=0
                    lineas_iva[linea.nombre]=0
                    lineas_total[linea.nombre]=0
                print lineas_neto
                detalle_venta = Detalle_venta.objects.filter(venta__fecha__range=(fd, fh))
                print "CANTIDAD DE DETALLES DE VENTA: %s" %len(detalle_venta)
                id=0
                for detalle in detalle_venta:
                    desc=detalle.venta.descuento/100
                    print "Iteracion %s" %id
                    
                    print "Tipo Articulo --> %s" %detalle.tipo_articulo
                    if detalle.tipo_articulo=='AA':
                        if detalle.articulo is not None:
                            if detalle.venta.tipo.startswith("NC"):
                                print "Resto %s" %detalle.total_con_descuento_factura
                                lineas_neto[detalle.articulo.linea.nombre]-=detalle.total_con_descuento_factura
                                lineas_iva[detalle.articulo.linea.nombre]-=detalle.iva_con_descuento_factura
                            else:
                                print "Sumo %s" %detalle.total_con_descuento_factura
                                lineas_neto[detalle.articulo.linea.nombre]+=detalle.total_con_descuento_factura
                                lineas_iva[detalle.articulo.linea.nombre]+=detalle.iva_con_descuento_factura  
                    elif detalle.tipo_articulo=='AP':
                        if detalle.linea_articulo_personalizado is not None:
                            if detalle.venta.tipo.startswith("NC"):
                                print "Resto %s" %detalle.total_con_descuento_factura
                                lineas_neto[detalle.linea_articulo_personalizado.nombre]-=detalle.total_con_descuento_factura
                                lineas_iva[detalle.linea_articulo_personalizado.nombre]-=detalle.iva_con_descuento_factura 
                            else:
                                print "Sumo %s" %detalle.total_con_descuento_factura
                                lineas_neto[detalle.linea_articulo_personalizado.nombre]+=detalle.total_con_descuento_factura
                                lineas_iva[detalle.linea_articulo_personalizado.nombre]+=detalle.iva_con_descuento_factura
                    elif detalle.tipo_articulo=='AC':
                        if detalle.venta.tipo.startswith("NC"):
                            print "Resto %s" %detalle.total_con_descuento_factura
                            lineas_neto[u'Prestación de Servicios']-=detalle.total_con_descuento_factura
                            lineas_iva[u'Prestación de Servicios']-=detalle.iva_con_descuento_factura 
                        else:
                            print "Sumo %s" %detalle.total_con_descuento_factura
                            lineas_neto[u'Prestación de Servicios']+=detalle.total_con_descuento_factura
                            lineas_iva[u'Prestación de Servicios']+=detalle.iva_con_descuento_factura
                        '''isu=0
                        cant=detalle.cantidad
                        for artcomp in detalle.detallearticulocompuesto_set.all():
                            print "    -> Subiteracion %s de %s" %(isu,len(detalle.detallearticulocompuesto_set.all()))
                            if artcomp.detalle_venta.venta.tipo.startswith("NC"):
                                if artcomp.articulo:
                                    print "Resto %s" %artcomp.total_con_descuento_factura_e_item
                                    lineas_neto[artcomp.articulo.linea.nombre]-=artcomp.total_con_descuento_factura_e_item
                                    lineas_iva[artcomp.articulo.linea.nombre]-=artcomp.iva*cant
                                elif artcomp.linea_articulo_personalizado:
                                    print "Resto %s" %(artcomp.neto*cant)
                                    lineas_neto[artcomp.linea_articulo_personalizado.nombre]-=artcomp.total_con_descuento_factura_e_item
                                    lineas_iva[artcomp.linea_articulo_personalizado.nombre]-=artcomp.iva*cant
                                else:
                                    print "Resto %s" %artcomp.total_con_descuento_factura_e_item
                                    lineas_neto[u'Prestación de Servicios']-=artcomp.neto*cant
                                    lineas_iva[u'Prestación de Servicios']-=artcomp.iva*cant
                            else:
                                if artcomp.articulo:
                                    print "Sumo %s" %artcomp.total_con_descuento_factura_e_item
                                    lineas_neto[artcomp.articulo.linea.nombre]+=artcomp.total_con_descuento_factura_e_item
                                    lineas_iva[artcomp.articulo.linea.nombre]+=artcomp.iva*cant
                                elif artcomp.linea_articulo_personalizado:
                                    print "Sumo %s" %artcomp.total_con_descuento_factura_e_item
                                    lineas_neto[artcomp.linea_articulo_personalizado.nombre]+=artcomp.total_con_descuento_factura_e_item
                                    lineas_iva[artcomp.linea_articulo_personalizado.nombre]+=artcomp.iva*cant
                                else:
                                    print "Sumo %s" %artcomp.total_con_descuento_factura_e_item
                                    lineas_neto[u'Prestación de Servicios']+=artcomp.total_con_descuento_factura_e_item
                                    lineas_iva[u'Prestación de Servicios']+=artcomp.iva*cant
                            print "B Uso        Fab        P.Serv.        Productos"
                            print "%s            %s        %s             %s"\
                            %(lineas_neto['Bienes de Uso'],lineas_neto[u'Fabricación'],lineas_neto[u'Prestación de Servicios'],lineas_neto['Productos'])
                            isu+=1'''
                        lineas_neto
                    else:
                        if detalle.venta.tipo.startswith("NC"):
                                print "Resto %s" %detalle.total_con_descuento_factura
                                lineas_neto[u'Prestación de Servicios']-=detalle.total_con_descuento_factura
                                lineas_iva[u'Prestación de Servicios']-=detalle.iva_con_descuento_factura
                        else:
                            print "Sumo %s" %detalle.total_con_descuento_factura
                            lineas_neto[u'Prestación de Servicios']+=detalle.total_con_descuento_factura
                            lineas_iva[u'Prestación de Servicios']+=detalle.iva_con_descuento_factura  
                    print "B Uso        Fab        P.Serv.        Productos"
                    print "%s            %s        %s             %s"\
                    %(lineas_neto['Bienes de Uso'],lineas_neto[u'Fabricación'],lineas_neto[u'Prestación de Servicios'],lineas_neto['Productos'])
                    id+=1
                    #print lineas_neto.values()
                #//////////VENTAS TOTALES//////////////
                response['Content-Disposition'] = 'filename="ventas_totales.pdf"'
                p = Canvas(response, pagesize=A4)
                p.setFont('Helvetica', 11)
                p.drawString(19*cm, 28.2*cm, datetime.today().strftime("%d/%m/%Y"))
                p.setFont('Helvetica-Bold', 15)
                p.drawString(2*cm, 27.5*cm, RAZON_SOCIAL_EMPRESA)
                p.drawString(7*cm, 26.2*cm, "VENTAS TOTALES")
                p.drawString(6*cm, 25.5*cm, "Desde %s hasta %s" %(datetime.strftime(fd,"%d/%m/%Y"),datetime.strftime(fh,"%d/%m/%Y")))
                p.line(0, 24.8*cm, 21*cm, 24.8*cm)
                p.setFont('Helvetica-Bold', 14)
                p.drawString(3*cm, 24.2*cm, "Linea")
                p.drawString(11*cm, 24.2*cm, "Neto")
                p.drawString(15*cm, 24.2*cm, "IVA")
                p.drawString(17.5*cm, 24.2*cm, "Total")
                p.line(0, 24*cm, 21*cm, 24*cm)
                inicio_y = 22
                alto_item = 0.7
                i=0
                for linea in lineas:
                    p.setFont('Helvetica', 12)
                    p.drawString(2.8*cm, (inicio_y-alto_item*i)*cm, linea.nombre)
                    p.drawString(11*cm, (inicio_y-alto_item*i)*cm, "%.2f" %lineas_neto[linea.nombre])
                    p.drawString(15*cm, (inicio_y-alto_item*i)*cm, "%.2f" %lineas_iva[linea.nombre])
                    p.drawString(17.5*cm, (inicio_y-alto_item*i)*cm, "%.2f" %(lineas_neto[linea.nombre]+lineas_iva[linea.nombre]))
                    i=i+1
                total_neto = 0
                for v in lineas_neto.values():
                    total_neto = total_neto+v
                total_iva=0
                for v in lineas_iva.values():
                    total_iva = total_iva+v 
                p.setFont('Helvetica-Bold', 12)
                p.drawString(2.8*cm, ((inicio_y-alto_item*i)-0.5)*cm, "TOTAL")
                p.drawString(11*cm, ((inicio_y-alto_item*i)-0.5)*cm, "%.2f" %total_neto)
                p.drawString(15*cm, ((inicio_y-alto_item*i)-0.5)*cm, "%.2f" %total_iva)
                p.drawString(17.5*cm, ((inicio_y-alto_item*i)-0.5)*cm, "%.2f" %(total_neto+total_iva))
                p.showPage()
                p.save()
                return response
    else:
        ventast = VentasTotalesForm()
        
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'ventast': ventast,
        }
    c.update(csrf(request))

    return render_to_response('informes/ventas_totales.html', c)

def resumen_cuenta(request):
    if request.method == 'POST':
        resumen = ResumenCuentaForm(request.POST)
        if resumen.is_valid():
            lis = resumen.cleaned_data['listar']
            if lis == "UNO":
                cli = resumen.cleaned_data['cliente'] 
            fd = resumen.cleaned_data['desde']
            fh = resumen.cleaned_data['hasta']           
            resp = HttpResponse(mimetype='application/pdf')
            #detalle=[{'id':cli.id,'razon_social':cli.razon_social,'detalle_comprobantes':[]}]
            detalle=[]
            #Defino las consultas Q
            fact=Q(tipo__startswith="FA")
            nd=Q(tipo__startswith="ND")
            apr=Q(aprobado=True)
            fe=Q(fecha__range=(fd,fh))
            nc=Q(tipo__startswith="NC")
            if lis=="UNO":
                cliq=Q(cliente=cli)
                factynd = Venta.objects.filter(cliq, apr, fe, fact | nd)               
                ncrs = Venta.objects.filter(cliq, apr, fe, nc)
                recibos = Recibo.objects.filter(cliq, fe)
            elif lis=="TODOS":
                factynd = Venta.objects.filter(apr, fe, fact | nd).order_by('cliente__razon_social')                  
                ncrs = Venta.objects.filter(apr, fe, nc)
                recibos = Recibo.objects.filter(fe)
            array_clientes = []
            for el in factynd.values():
                if not el['cliente_id'] in array_clientes:
                    array_clientes.append(el['cliente_id'])
            for cliente in array_clientes:
                deta_comp=[]
                factynd_c=factynd.filter(cliente__id=cliente)
                ncrs_c=ncrs.filter(cliente__id=cliente)
                recibos_c=recibos.filter(cliente__id=cliente)
                for jorge in factynd_c:
                    deta_comp.append({'cliente_id':cliente,'razon_social':Cliente.objects.get(id=cliente).razon_social,\
                                      'fecha':jorge.fecha,'tipo':jorge.tipo,'numero':jorge.pto_vta_num_full,\
                                      'debe':jorge.total,'haber':Decimal("0.00"),"saldo":Decimal("0.00")})
                for jorge in ncrs_c:
                    deta_comp.append({'cliente_id':cliente,'razon_social':Cliente.objects.get(id=cliente).razon_social,\
                                      'fecha':jorge.fecha,'tipo':jorge.tipo,'numero':jorge.pto_vta_num_full,\
                                      'debe':Decimal("0.00"),'haber':jorge.total,"saldo":Decimal("0.00")})
                for rec in recibos_c:
                    deta_comp.append({'cliente_id':cliente,'razon_social':Cliente.objects.get(id=cliente).razon_social,\
                                      'fecha':rec.fecha,'tipo':'REC','numero':rec.numero_full,\
                                      'debe':Decimal("0.00"),'haber':rec.total,"saldo":Decimal("0.00")})
                deta_comp=sorted(deta_comp,key=itemgetter('fecha'))               
                deta_comp.insert(0,{'cliente_id':cliente,'razon_social':Cliente.objects.get(id=cliente).razon_social,'fecha':'Saldo anterior','tipo':'','numero':'','debe':'','haber':'','saldo':Cliente.objects.get(id=cliente).saldo_anterior(fd)})  
                for i,v in enumerate(deta_comp):
                    if i==0:
                        saldo_ant=v['saldo']
                    else:
                        if v['tipo'].startswith("FA") or v['tipo'].startswith("ND"):
                            saldo_ant+=v['debe']
                            v['saldo']=saldo_ant
                        else:
                            saldo_ant-=v['haber']
                            v['saldo']=saldo_ant
                detalle.extend(deta_comp)
            print detalle
            resumen_cuenta = ResumenCuenta(queryset=detalle)
                #ivav.first_page_number = fi
            resumen_cuenta.generate_by(PDFGenerator, filename=resp)
            return resp
    else:
        resumen = ResumenCuentaForm()
        
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'resumen': resumen,
        }
    c.update(csrf(request))

    return render_to_response('informes/resumen_cuenta.html', c)



def comp_saldo(request):
    if request.method == 'POST':
        comp = ComposicionSaldoForm(request.POST)
        if comp.is_valid():
            lis = comp.cleaned_data['listar']
            tip = comp.cleaned_data['tipo']
            if lis == "UNO":
                cli = comp.cleaned_data['cliente']            
            resp = HttpResponse(mimetype='application/pdf')
            #detalle=[{'id':cli.id,'razon_social':cli.razon_social,'detalle_comprobantes':[]}]
            detalle=[]
            #Defino las consultas Q
            fact=Q(tipo__startswith="FA")
            nd=Q(tipo__startswith="ND")
            apr=Q(aprobado=True)
            npag=Q(pagado=False)
            if lis=="UNO":
                cliq=Q(cliente=cli)
                factynd = Venta.objects.filter(cliq, apr, npag, fact | nd)               
            elif lis=="TODOS":
                factynd = Venta.objects.filter(apr, npag, fact | nd).order_by('cliente__razon_social')                  
            array_clientes = []
            for el in factynd.values():
                if not el['cliente_id'] in array_clientes:
                    array_clientes.append(el['cliente_id'])
            for cliente in array_clientes:
                deta_comp=[]
                factynd_c=factynd.filter(cliente__id=cliente)
                saldo_t=0
                for jorge in factynd_c:
                    saldo_t+=jorge.saldo()
                    deta_comp.append({'cliente_id':cliente,'razon_social':Cliente.objects.get(id=cliente).razon_social,\
                                      'fecha':jorge.fecha,'tipo':jorge.tipo,'numero':jorge.pto_vta_num_full,\
                                      'total_c':jorge.total,'saldo_c':jorge.saldo(),"saldo_t":saldo_t})
                    deta_comp[len(deta_comp)-1]['detalle_venta']=[]
                    if tip=="DETALLADO":
                        for det in jorge.detalle_venta_set.all():
                            dv={'cantidad':det.cantidad,'articulo':det.articulo.denominacion if det.articulo else det.articulo_personalizado,'total':det.total_con_descuento+det.iva}
                            deta_comp[len(deta_comp)-1]['detalle_venta'].append(dv)               
                detalle.extend(deta_comp)
            print detalle
            comp_saldo = ComposicionSaldo(queryset=detalle)
                #ivav.first_page_number = fi
            comp_saldo.generate_by(PDFGenerator, filename=resp)
            return resp
    else:
        comp = ComposicionSaldoForm()
        
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'comp': comp,
        }
    c.update(csrf(request))

    return render_to_response('informes/comp_saldo.html', c)


def compra_new(request):
    # This class is used to make empty formset forms required
    # See http://stackoverflow.com/questions/2406537/django-formsets-make-first-required/4951032#4951032
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False
                    
    DetalleFormSet = formset_factory(DetalleCompraForm, formset=RequiredFormSet)
    if request.method == 'POST': # If the form has been submitted...
        facturaForm = ComprobanteCompraForm(request.POST) # A form bound to the POST data
        # Create a formset from the submitted data
        detalleCompraFormset = DetalleFormSet(request.POST)
        #set_trace()
        if facturaForm.is_valid() and detalleCompraFormset.is_valid():
            #factura = facturaForm.save(commit=False)
            #set_trace()
            factura = facturaForm.save(commit=False)
            subtotal = 0
            iva={0:0,10.5:0,21:0,27:0}
            for form in detalleCompraFormset.forms:
                detalleItem = form.save(commit=False)
                sub = detalleItem.cantidad * detalleItem.precio_unitario
                subtotal += sub
                iva[detalleItem.iva]+=detalleItem.iva_valor
            factura.neto = subtotal
            factura.iva21 = iva[21]
            factura.iva105 = iva[10.5]
            factura.iva27 = iva[27]
            saldo = factura.neto+factura.iva21+factura.iva105+factura.iva27+\
                    factura.percepcion_iva+factura.exento+factura.ingresos_brutos+\
                    factura.impuesto_interno+factura.redondeo
            #set_trace()
            if factura.tipo.startswith("NC"):
                factura.neto = factura.neto*-1
                factura.iva105 = factura.iva105*-1
                factura.iva21 = factura.iva21*-1
                factura.iva27 = factura.iva27*-1
                factura.percepcion_iva = factura.percepcion_iva*-1
                factura.exento = factura.exento*-1
                factura.ingresos_brutos = factura.ingresos_brutos*-1
                factura.impuesto_interno = factura.impuesto_interno*-1
                factura.redondeo = factura.redondeo*-1
                subtotal = subtotal*-1
                saldo = saldo*-1
            #Resto de los saldos de otros comprobantes
            otros_comp=Compra.objects.filter(Q(proveedor=factura.proveedor), ~Q(saldo=0)).order_by('fecha','numero')
            print "Otros comprob:  " %otros_comp
            if otros_comp:
                if (otros_comp[0].tipo.startswith('NC') and factura.tipo.startswith('NC')) or\
                    (not otros_comp[0].tipo.startswith('NC') and not factura.tipo.startswith('NC')):
                    factura.saldo = saldo
                else:
                    for comp in otros_comp:
                        if saldo == 0:
                            break
                        if abs(saldo) >= abs(comp.saldo):
                            saldo += comp.saldo
                            comp.saldo = 0
                        else:
                            comp.saldo += saldo
                            saldo = 0
                        comp.save()
                    factura.saldo = saldo
            else:
                factura.saldo = saldo
            factura.save()
            for form in detalleCompraFormset.forms:
                detalleItem = form.save(commit=False)
                detalleItem.compra = factura
                detalleItem.save()
            #set_trace()
            if factura.condicion_compra.descripcion=="Contado" and factura.tipo.startswith("FA"):
                print "Contado"
                return HttpResponseRedirect(reverse_lazy('nuevaOrdenPagoContado',kwargs={'compra':factura.pk}))
            else:
                print "NO Contado"
                return HttpResponseRedirect(reverse_lazy('nuevaCompra'))
       
    else:
        facturaForm = ComprobanteCompraForm()
        detalleCompraFormset = DetalleFormSet()
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    #set_trace()
    c = {'compraForm': facturaForm,
         'detalleCompraFormset': detalleCompraFormset,
        }
    c.update(csrf(request))

    return render_to_response('compras/new.html', c)

class comprasList(TemplateView):
    template_name="compras/list.html"
    
class chequesList(TemplateView):
    template_name="cheques/list.html"
    
def subdiario_iva_compras(request):
    if request.method == 'POST':
        subdiario = SubdiarioIVAPeriodoFecha(request.POST)
        if subdiario.is_valid():
            per = subdiario.cleaned_data['periodo']
            fd = subdiario.cleaned_data['fecha_desde']
            fh = subdiario.cleaned_data['fecha_hasta']
            fi = subdiario.cleaned_data['folio_inicial']            
            resp = HttpResponse(mimetype='application/pdf')
            if per:
                compras = Compra.objects.filter(periodo=per).order_by('fecha')
                #set_trace()
                #ivav = IVAVentas(queryset=ventas,periodo=per,folio_inicial=fi)
                ivac = IVACompras(queryset=compras)
                #ivav.first_page_number = fi
                ivac.generate_by(PDFGenerator, filename=resp, variables={'periodo': per.periodo_full()})
                return resp
            else:
                if fh and fd:
                    compras = Compra.objects.filter(fecha__range=(fd, fh)).order_by('fecha')
                    ivac = IVACompras(queryset=compras)
                    ivac.generate_by(PDFGenerator, filename=resp, variables={'periodo': 'N/A'})
                    return resp
    else:
        subdiario = SubdiarioIVAPeriodoFecha()
        
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'subdiario': subdiario,
        }
    c.update(csrf(request))

    return render_to_response('informes/sub_iva_form.html', c)

def orden_pago_new(request):
    # This class is used to make empty formset forms required
    # See http://stackoverflow.com/questions/2406537/django-formsets-make-first-required/4951032#4951032
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False
                    
    DetallePagoFormSet = formset_factory(DetallePagoForm, formset=RequiredFormSet)
    ValoresFormSet = formset_factory(ValoresOPForm, formset=RequiredFormSet)
    if request.method == 'POST': # If the form has been submitted...
        ordenPagoForm = OrdenPagoForm(request.POST) # A form bound to the POST data
        # Create a formset from the submitted data
        pagoFormset = DetallePagoFormSet(request.POST, prefix='pagos')
        valoresFormset = ValoresFormSet(request.POST, prefix='valores')
        #set_trace()
        if ordenPagoForm.is_valid() and pagoFormset.is_valid() and valoresFormset.is_valid():
            orden_pago = ordenPagoForm.save(commit=False)
            orden_pago.numero = get_num_orden_pago()
            #cred_ant=orden_pago.proveedor.saldo
            #Dejo en 0 el cheque del credito, si hubiera:
            try:
                cheq=ChequeTercero.objects.filter(orden_pago__proveedor=orden_pago.proveedor,pendiente_para_orden_pago__gt=0)[0]
                cred_ant = cheq.pendiente_para_orden_pago
                cheq.pendiente_para_orden_pago=0
                cheq.save()
            except IndexError:
                pass
                cred_ant=0
            
            print "CREDITO ANTERIOR: %s" %cred_ant
            orden_pago.credito_anterior=cred_ant
            orden_pago.save()
            #if Decimal(ordenPagoForm.cleaned_data['credito_anterior']) > 0:
            #    Cobranza_credito_anterior.objects.create(orden_pago=orden_pago,monto=ordenPagoForm.cleaned_data['credito_anterior'])
            total_comprobantes=0
            for detalle_pago in pagoFormset.forms:
                if detalle_pago.cleaned_data['pagar']:
                    if Decimal(detalle_pago.cleaned_data['pagar'])!=0:
                        total_comprobantes+=detalle_pago.cleaned_data['pagar']
                        co = Compra.objects.get(pk=detalle_pago.cleaned_data['id_factura_compra'])
                        Detalle_pago.objects.create(orden_pago=orden_pago, compra=co, monto=detalle_pago.cleaned_data['pagar'])        
                        co.saldo -= detalle_pago.cleaned_data['pagar']
                        co.save()
                        #pagado_total = Detalle_pago.objects.filter(compra=co).aggregate(Sum('monto'))['monto__sum']
                        #nc_total = Venta.objects.filter(comprobante_relacionado=co).aggregate(Sum('total'))
                        #todo = pagado_total['monto__sum'] if pagado_total['monto__sum'] else 0.00 +nc_total['total__sum'] if nc_total['total__sum'] else 0.00
                        #if (co.total-Decimal(0.009) <= todo <= co.total+Decimal(0.009)):
                        #set_trace()
                        #if co.tipo.startswith("NC"):
                        #    co.pagado=True
                        #    co.save()
                        #elif co.total-Decimal(0.009) <= pagado_total <= co.total+Decimal(0.009):
                        #    co.pagado=True
                        #    co.save()
            print total_comprobantes
            for valor in valoresFormset.forms:
                    #set_trace()
                    if valor.cleaned_data['monto'] <= total_comprobantes+Decimal(0.009)-cred_ant:
                        total_comprobantes-=valor.cleaned_data['monto']
                        if valor.cleaned_data['tipo']=='CHT':
                            cheque3=ChequeTercero.objects.get(pk=valor.cleaned_data['id_cheque_tercero'])
                            cheque3.pendiente_para_orden_pago=0
                            cheque3.en_cartera=False
                            cheque3.orden_pago=orden_pago
                            cheque3.save()
                        elif valor.cleaned_data['tipo']=='CHP':
                            ChequePropio.objects.create(orden_pago=orden_pago,\
                                                        numero=valor.cleaned_data['cheque_numero'],\
                                                        fecha=valor.cleaned_data['cheque_fecha'],\
                                                        cobro=valor.cleaned_data['cheque_cobro'],\
                                                        paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                        pendiente_para_orden_pago=0,\
                                                        monto=valor.cleaned_data['monto'])
                        elif valor.cleaned_data['tipo']=='EFE':
                            Dinero.objects.create(monto=valor.cleaned_data['monto'], orden_pago=orden_pago)
                        elif valor.cleaned_data['tipo']=='TRB':
                            TransferenciaBancariaSaliente.objects.create(orden_pago=orden_pago,\
                                                                         cuenta_origen=valor.cleaned_data['transferencia_cuenta_origen'],\
                                                                         numero_operacion=valor.cleaned_data['transferencia_numero_operacion'],\
                                                                         cuenta_destino=valor.cleaned_data['transferencia_cuenta_destino'],\
                                                                         monto=valor.cleaned_data['monto'])
                    else:
                        total_comprobantes-=cred_ant
                        print "TOTAL COMPROBANTES ULTIMO COMP: %s" %total_comprobantes
                        print "DIF: %s" %(valor.cleaned_data['monto']-total_comprobantes)
                        if ordenPagoForm.cleaned_data['que_hago_con_diferencia']=='credito':
                            if valor.cleaned_data['tipo']=="CHT":
                                cheque3=ChequeTercero.objects.get(pk=valor.cleaned_data['id_cheque_tercero'])
                                cheque3.pendiente_para_orden_pago=valor.cleaned_data['monto']-total_comprobantes
                                cheque3.en_cartera=False
                                cheque3.orden_pago=orden_pago
                                cheque3.save()
                            elif valor.cleaned_data['tipo']=="CHP":
                                ChequePropio.objects.create(orden_pago=orden_pago,\
                                                            numero=valor.cleaned_data['cheque_numero'],\
                                                            fecha=valor.cleaned_data['cheque_fecha'],\
                                                            cobro=valor.cleaned_data['cheque_cobro'],\
                                                            paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                            pendiente_para_orden_pago=valor.cleaned_data['monto']-total_comprobantes,\
                                                            monto=valor.cleaned_data['monto'])                    
                            #orden_pago.proveedor.saldo=valor.cleaned_data['monto']-total_comprobantes
                            #orden_pago.proveedor.save()
                        elif ordenPagoForm.cleaned_data['que_hago_con_diferencia']=='vuelto':
                            if valor.cleaned_data['tipo']=="CHT":
                                cheque3=ChequeTercero.objects.get(pk=valor.cleaned_data['id_cheque_tercero'])
                                cheque3.pendiente_para_orden_pago=valor.cleaned_data['monto']-total_comprobantes
                                cheque3.en_cartera=False
                                cheque3.orden_pago=orden_pago
                                cheque3.save()
                            elif valor.cleaned_data['tipo']=="CHP":
                                ChequePropio.objects.create(orden_pago=orden_pago,\
                                                            numero=valor.cleaned_data['cheque_numero'],\
                                                            fecha=valor.cleaned_data['cheque_fecha'],\
                                                            cobro=valor.cleaned_data['cheque_cobro'],\
                                                            paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                            pendiente_para_orden_pago=valor.cleaned_data['monto']-total_comprobantes,\
                                                            monto=valor.cleaned_data['monto'])                    
                            Dinero.objects.create(orden_pago=orden_pago, monto=(valor.cleaned_data['monto']-total_comprobantes)*-1)
                            #orden_pago.proveedor.saldo=0
                            #orden_pago.proveedor.save()
            obj = {'id':orden_pago.id}
            s = StringIO()
            json.dump(obj,s)
            s.seek(0)
            return HttpResponse(s.read())
            
    else:
        ordenPagoForm = OrdenPagoForm()
        pagoFormset = DetallePagoFormSet(prefix='pagos')
        valoresFormset = ValoresFormSet(prefix='valores')
        
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    #set_trace()
    c = {'ordenPagoForm': ordenPagoForm,
         'pagoFormset': pagoFormset,
         'valoresFormset': valoresFormset,
        }
    c.update(csrf(request))

    return render_to_response('compras/orden_pago_new.html', c)

def orden_pago_contado_new(request, compra):
    # This class is used to make empty formset forms required
    # See http://stackoverflow.com/questions/2406537/django-formsets-make-first-required/4951032#4951032
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False
                    
    DetallePagoFormSet = formset_factory(DetallePagoContadoForm, extra=0)
    ValoresFormSet = formset_factory(ValoresOPForm, formset=RequiredFormSet)
    if request.method == 'POST': # If the form has been submitted...
        ordenPagoForm = OrdenPagoForm(request.POST) # A form bound to the POST data
        # Create a formset from the submitted data
        pagoFormset = DetallePagoFormSet(request.POST, prefix='pagos')
        valoresFormset = ValoresFormSet(request.POST, prefix='valores')
        #set_trace()
        if ordenPagoForm.is_valid() and pagoFormset.is_valid() and valoresFormset.is_valid():
            orden_pago = ordenPagoForm.save(commit=False)
            orden_pago.numero = get_num_orden_pago()
            #Dejo en 0 el cheque del credito, si hubiera:
            try:
                cheq=ChequeTercero.objects.filter(orden_pago__proveedor=orden_pago.proveedor,pendiente_para_orden_pago__gt=0)[0]
                cred_ant = cheq.pendiente_para_orden_pago
                cheq.pendiente_para_orden_pago=0
                cheq.save()
            except IndexError:
                pass
                cred_ant=0
            #cred_ant=orden_pago.proveedor.saldo
            print "CREDITO ANTERIOR: %s" %cred_ant
            orden_pago.credito_anterior=cred_ant
            orden_pago.save()
            
            #if Decimal(ordenPagoForm.cleaned_data['credito_anterior']) > 0:
            #    Cobranza_credito_anterior.objects.create(orden_pago=orden_pago,monto=ordenPagoForm.cleaned_data['credito_anterior'])
            total_comprobantes=0
            for detalle_pago in pagoFormset.forms:
                co = Compra.objects.get(pk=detalle_pago.cleaned_data['id_factura_compra'])
                Detalle_pago.objects.create(orden_pago=orden_pago, compra=co, monto=co.total)        
                #co.pagado=True
                co.saldo=0
                total_comprobantes=co.total
                co.save()
            print total_comprobantes
            for valor in valoresFormset.forms:
                    #set_trace()
                    if valor.cleaned_data['monto'] <= total_comprobantes+Decimal(0.009)-cred_ant:
                        total_comprobantes-=valor.cleaned_data['monto']
                        if valor.cleaned_data['tipo']=='CHT':
                            cheque3=ChequeTercero.objects.get(pk=valor.cleaned_data['id_cheque_tercero'])
                            cheque3.pendiente_para_orden_pago=0
                            cheque3.en_cartera=False
                            cheque3.orden_pago=orden_pago
                            cheque3.save()
                        elif valor.cleaned_data['tipo']=='CHP':
                            ChequePropio.objects.create(orden_pago=orden_pago,\
                                                        numero=valor.cleaned_data['cheque_numero'],\
                                                        fecha=valor.cleaned_data['cheque_fecha'],\
                                                        cobro=valor.cleaned_data['cheque_cobro'],\
                                                        paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                        pendiente_para_orden_pago=0,\
                                                        monto=valor.cleaned_data['monto'])
                        elif valor.cleaned_data['tipo']=='EFE':
                            Dinero.objects.create(monto=valor.cleaned_data['monto'], orden_pago=orden_pago)
                        elif valor.cleaned_data['tipo']=='TRB':
                            TransferenciaBancariaSaliente.objects.create(orden_pago=orden_pago,\
                                                                         cuenta_origen=valor.cleaned_data['transferencia_cuenta_origen'],\
                                                                         numero_operacion=valor.cleaned_data['transferencia_numero_operacion'],\
                                                                         cuenta_destino=valor.cleaned_data['transferencia_cuenta_destino'],\
                                                                         monto=valor.cleaned_data['monto'])
                    else:
                        print "-----------------------------SOBRANTE------------------------"
                        total_comprobantes-=cred_ant
                        print "TOTAL COMPROBANTES ULTIMO COMP: %s" %total_comprobantes
                        print "DIF: %s" %(valor.cleaned_data['monto']-total_comprobantes)
                        if ordenPagoForm.cleaned_data['que_hago_con_diferencia']=='credito':
                            print "---------------------!!!---!!!------A CREDITO-------------------"
                            if valor.cleaned_data['tipo']=="CHT":
                                cheque3=ChequeTercero.objects.get(pk=valor.cleaned_data['id_cheque_tercero'])
                                cheque3.pendiente_para_orden_pago=valor.cleaned_data['monto']-total_comprobantes
                                cheque3.en_cartera=False
                                cheque3.orden_pago=orden_pago
                                cheque3.save()
                            elif valor.cleaned_data['tipo']=="CHP":
                                ChequePropio.objects.create(orden_pago=orden_pago,\
                                                            numero=valor.cleaned_data['cheque_numero'],\
                                                            fecha=valor.cleaned_data['cheque_fecha'],\
                                                            cobro=valor.cleaned_data['cheque_cobro'],\
                                                            paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                            pendiente_para_orden_pago=valor.cleaned_data['monto']-total_comprobantes,\
                                                            monto=valor.cleaned_data['monto'])                    
                            #orden_pago.proveedor.saldo=valor.cleaned_data['monto']-total_comprobantes
                            #orden_pago.proveedor.save()
                        elif ordenPagoForm.cleaned_data['que_hago_con_diferencia']=='vuelto':
                            if valor.cleaned_data['tipo']=="CHT":
                                cheque3=ChequeTercero.objects.get(pk=valor.cleaned_data['id_cheque_tercero'])
                                cheque3.pendiente_para_orden_pago=valor.cleaned_data['monto']-total_comprobantes
                                cheque3.en_cartera=False
                                cheque3.orden_pago=orden_pago
                                cheque3.save()
                            elif valor.cleaned_data['tipo']=="CHP":
                                ChequePropio.objects.create(orden_pago=orden_pago,\
                                                            numero=valor.cleaned_data['cheque_numero'],\
                                                            fecha=valor.cleaned_data['cheque_fecha'],\
                                                            cobro=valor.cleaned_data['cheque_cobro'],\
                                                            paguese_a=valor.cleaned_data['cheque_paguese_a'],\
                                                            pendiente_para_orden_pago=valor.cleaned_data['monto']-total_comprobantes,\
                                                            monto=valor.cleaned_data['monto'])                    
                            Dinero.objects.create(orden_pago=orden_pago, monto=(valor.cleaned_data['monto']-total_comprobantes)*-1)
                            #orden_pago.proveedor.saldo=0
                            #orden_pago.proveedor.save()
            obj = {'id':orden_pago.id}
            s = StringIO()
            json.dump(obj,s)
            s.seek(0)
            return HttpResponse(s.read())
            
    else:
        cp=Compra.objects.get(pk=compra)
        ordenPagoForm = OrdenPagoContadoForm(initial={'proveedor':cp.proveedor})
        pagoFormset = DetallePagoFormSet(prefix='pagos', initial=[{'id_factura_compra':cp.pk}])
        valoresFormset = ValoresFormSet(prefix='valores')
        
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    #set_trace()
    c = {'ordenPagoForm': ordenPagoForm,
         'pagoFormset': pagoFormset,
         'valoresFormset': valoresFormset,
         'compra':cp,
        }
    c.update(csrf(request))

    return render_to_response('compras/orden_pago_contado_new.html', c)


class PagosList(TemplateView):
    template_name = "pagos/list.html"
    
def imprimirOrdenPago(request,pk):
    ops=OrdenPago.objects.get(pk=pk)
    qs=[]
    orp={'numero_full':ops.numero_full,'fecha_dd_mm_aaaa':ops.fecha_dd_mm_aaaa,'proveedor_razon_social':ops.proveedor.razon_social,\
         'proveedor_direccion':ops.proveedor.direccion,'proveedor_localidad':ops.proveedor.localidad,\
         'proveedor_condicion_iva':ops.proveedor.get_condicion_iva_display(),'proveedor_cuit':ops.proveedor.cuit,\
         'proveedor_codigo_ingresos_brutos':ops.proveedor.codigo_ingresos_brutos,'detalle_pago_set':[],\
         'dinero_set':[]}
    for deta in ops.detalle_pago_set.all():
        orp['detalle_pago_set'].append({'compra_fecha_dd_mm_aaaa':deta.compra.fecha_dd_mm_aaaa,\
                                        'compra_identificador_completo':deta.compra.identificador_completo,\
                                        'monto':round(deta.monto,2)})
    if ops.saldo_a_cuenta>0:
        orp['detalle_pago_set'].insert(0,{'compra_fecha_dd_mm_aaaa':"",\
                                        'compra_identificador_completo':"    A CUENTA",\
                                        'monto':round(ops.saldo_a_cuenta,2)})
    if ops.credito_anterior>0:
        orp['detalle_pago_set'].insert(0,{'compra_fecha_dd_mm_aaaa':"",\
                                        'compra_identificador_completo':"CREDITO ANTERIOR",\
                                        'monto':-round(ops.credito_anterior,2)})
    for dine in ops.dinero_set.all():
        orp['dinero_set'].append({'tipo_valor':dine.tipo_valor,'entidad':dine.entidad,'num_comprobante':dine.num_comprobante,\
                                   'CUIT':dine.CUIT,'FECHA':dine.FECHA,'monto':round(dine.monto,2)})
    qs.append(orp)
    print qs
    resp = HttpResponse(mimetype='application/pdf')
    op=OrdenPagoReport(queryset=qs)
    op.generate_by(PDFGenerator, filename=resp)
    return resp

def proveedores_resumen_cuenta(request):
    if request.method == 'POST':
        resumen = ProveedoresResumenCuentaForm(request.POST)
        if resumen.is_valid():
            lis = resumen.cleaned_data['listar']
            if lis == "UNO":
                pro = resumen.cleaned_data['proveedor'] 
            fd = resumen.cleaned_data['desde']
            fh = resumen.cleaned_data['hasta']           
            resp = HttpResponse(mimetype='application/pdf')
            #detalle=[{'id':pro.id,'razon_social':pro.razon_social,'detalle_comprobantes':[]}]
            detalle=[]
            #Defino las consultas Q
            fact=Q(tipo__startswith="FA")
            nd=Q(tipo__startswith="ND")
            #apr=Q(aprobado=True)
            fe=Q(fecha__range=(fd,fh))
            nc=Q(tipo__startswith="NC")
            if lis=="UNO":
                proq=Q(proveedor=pro)
                factynd = Compra.objects.filter(proq, fe, fact | nd)               
                ncrs = Compra.objects.filter(proq, fe, nc)
                ops = OrdenPago.objects.filter(proq, fe)
            elif lis=="TODOS":
                factynd = Compra.objects.filter(fe, fact | nd).order_by('proveedor__razon_social')                  
                ncrs = Compra.objects.filter(fe, nc)
                ops = OrdenPago.objects.filter(fe)
            array_proveedores = []
            for el in factynd.values():
                if not el['proveedor_id'] in array_proveedores:
                    array_proveedores.append(el['proveedor_id'])
            for proveedor in array_proveedores:
                deta_comp=[]
                factynd_c=factynd.filter(proveedor__id=proveedor)
                ncrs_c=ncrs.filter(proveedor__id=proveedor)
                ops_c=ops.filter(proveedor__id=proveedor)
                for jorge in factynd_c:
                    deta_comp.append({'proveedor_id':proveedor,'razon_social':Proveedor.objects.get(id=proveedor).razon_social,\
                                      'fecha':jorge.fecha,'tipo':jorge.tipo,'numero':jorge.identificador,\
                                      'debe':jorge.total,'haber':Decimal("0.00"),"saldo":Decimal("0.00")})
                for jorge in ncrs_c:
                    deta_comp.append({'proveedor_id':proveedor,'razon_social':Proveedor.objects.get(id=proveedor).razon_social,\
                                      'fecha':jorge.fecha,'tipo':jorge.tipo,'numero':jorge.identificador,\
                                      'debe':Decimal("0.00"),'haber':jorge.total*-1,"saldo":Decimal("0.00")})
                for op in ops_c:
                    deta_comp.append({'proveedor_id':proveedor,'razon_social':Proveedor.objects.get(id=proveedor).razon_social,\
                                      'fecha':op.fecha,'tipo':'REC','numero':op.numero_full,\
                                      'debe':Decimal("0.00"),'haber':op.total,"saldo":Decimal("0.00")})
                deta_comp=sorted(deta_comp,key=itemgetter('fecha'))               
                deta_comp.insert(0,{'proveedor_id':proveedor,'razon_social':Proveedor.objects.get(id=proveedor).razon_social,\
                                    'fecha':'Saldo anterior','tipo':'','numero':'','debe':'','haber':'',\
                                    'saldo':Proveedor.objects.get(id=proveedor).saldo_anterior(fd)})  
                for i,v in enumerate(deta_comp):
                    if i==0:
                        saldo_ant=v['saldo']
                    else:
                        if v['tipo'].startswith("FA") or v['tipo'].startswith("ND"):
                            saldo_ant+=v['debe']
                            v['saldo']=saldo_ant
                        else:
                            saldo_ant-=v['haber']
                            v['saldo']=saldo_ant
                detalle.extend(deta_comp)
            print detalle
            resumen_cuenta = ResumenCuentaProveedores(queryset=detalle)
                #ivav.first_page_number = fi
            resumen_cuenta.generate_by(PDFGenerator, filename=resp)
            return resp
    else:
        resumen = ProveedoresResumenCuentaForm()
        
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'resumen': resumen,
        }
    c.update(csrf(request))

    return render_to_response('informes/proveedores_resumen_cuenta.html', c)

def proveedores_comp_saldo(request):
    if request.method == 'POST':
        comp = ProveedoresComposicionSaldoForm(request.POST)
        if comp.is_valid():
            lis = comp.cleaned_data['listar']
            tip = comp.cleaned_data['tipo']
            if lis == "UNO":
                pro = comp.cleaned_data['proveedor']            
            resp = HttpResponse(mimetype='application/pdf')
            #detalle=[{'id':pro.id,'razon_social':pro.razon_social,'detalle_comprobantes':[]}]
            detalle=[]
            #Defino las consultas Q
            #fact=Q(tipo__startswith="FA")
            #nd=Q(tipo__startswith="ND")
            npag=Q(pagado=False)
            if lis=="UNO":
                proq=Q(proveedor=pro)
                factynd = Compra.objects.filter(proq, npag)               
            elif lis=="TODOS":
                factynd = Compra.objects.filter(npag).order_by('proveedor__razon_social')                  
            array_proveedores = []
            for el in factynd.values():
                if not el['proveedor_id'] in array_proveedores:
                    array_proveedores.append(el['proveedor_id'])
            for proveedor in array_proveedores:
                deta_comp=[]
                factynd_c=factynd.filter(proveedor__id=proveedor)
                saldo_t=0
                for jorge in factynd_c:
                    saldo_t+=jorge.saldo
                    deta_comp.append({'proveedor_id':proveedor,'razon_social':Proveedor.objects.get(id=proveedor).razon_social,\
                                      'fecha':jorge.fecha,'tipo':jorge.tipo,'numero':jorge.identificador,\
                                      'total_c':jorge.total,'saldo_c':jorge.saldo,"saldo_t":saldo_t})
                    deta_comp[len(deta_comp)-1]['detalle_compra']=[]
                    if tip=="DETALLADO":
                        for det in jorge.detalle_compra_set.all():
                            dc={'cantidad':det.cantidad,'articulo':det.detalle,'total':det.total}
                            deta_comp[len(deta_comp)-1]['detalle_venta'].append(dc)               
                detalle.extend(deta_comp)
            print detalle
            comp_saldo = ComposicionSaldoProveedores(queryset=detalle)
                #ivav.first_page_number = fi
            comp_saldo.generate_by(PDFGenerator, filename=resp)
            return resp
    else:
        comp = ProveedoresComposicionSaldoForm()
        
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    c = {'comp': comp,
        }
    c.update(csrf(request))

    return render_to_response('informes/proveedores_comp_saldo.html', c)