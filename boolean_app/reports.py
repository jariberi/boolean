# -*- coding: utf-8 -*-

from geraldo import Report, ReportBand, Label, DetailBand

from geraldo.widgets import ObjectValue, SystemField
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from geraldo.utils import cm, landscape, BAND_WIDTH, FIELD_ACTION_SUM,\
    FIELD_ACTION_COUNT
from geraldo.base import SubReport, ReportBand, ReportGroup
from boolean.settings import RAZON_SOCIAL_EMPRESA, CUIT, DOMICILIO_COMERCIAL,\
    CIUDAD
from pdb import set_trace
from geraldo.graphics import Line, RoundRect
from reportlab.lib.colors import yellow, grey, black
from boolean_app.models import Venta, Recibo, Dinero
from django.http.response import HttpResponse
from reportlab.pdfgen.canvas import Canvas
from decimal import Decimal
from datetime import datetime, date
from boolean_app.utils import to_word
from reportlab.lib.units import mm


class IVAVentas(Report):
    title = 'LIBRO IVA VENTAS - RESOLUCION GENERAL AFIP 3419'
    page_size = landscape(A4)
    #first_page_number=7
    
    def __init__(self, queryset=None, fpn=1):
        print "INIT DE REPORTE"
        Report.__init__(self, queryset=queryset)
        self.first_page_number=fpn
        print self.first_page_number
    
    class band_page_header(ReportBand):    
        height = 4*cm
        elements = [SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH, 
                                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
                    Label(text="RAZON SOCIAL: %s" %RAZON_SOCIAL_EMPRESA, top=0.8*cm, width=BAND_WIDTH, 
                          style={'fontName':'Helvetica','fontSize':10}),
                    Label(text="CUIT: %s" %CUIT, top=1.2*cm, width=BAND_WIDTH, 
                          style={'fontName':'Helvetica','fontSize':10}),
                    Label(text="DOMICILIO COMERCIAL: %s" %DOMICILIO_COMERCIAL, top=1.5*cm, width=BAND_WIDTH, 
                          style={'fontName':'Helvetica','fontSize':10}),
                    SystemField(expression='Periodo: %(var:periodo)s', top=1.5*cm, left=23*cm, 
                          style={'fontName':'Helvetica','fontSize':10}), 
                    SystemField(expression='Fecha emisión: %(now:%d/%m/%Y)s', top=2*cm, width=8*cm),
                    SystemField(expression='Folio N°: %(page_number)s', top=2*cm, left=23*cm, 
                          style={'fontName':'Helvetica','fontSize':10}),
                    Line(left=0, top=2.7*cm, right = 29.7*cm, bottom = 2.7*cm),
                    #Encabezado de tabla
                    Label(text="Fecha", top=2.9*cm, left=0, width=2*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="Comprobante", top=2.9*cm, left=2.1*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="Razón Social", top=2.9*cm, left=5.7*cm, width=7*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="CUIT", top=2.9*cm, left=13.7*cm, width=2.5*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="Imp. Neto", top=2.9*cm, left=17.2*cm, width=2*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="IVA(10.5%)", top=2.9*cm, left=20.2*cm, width=2*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="IVA(21%)", top=2.9*cm, left=22.2*cm, width=2*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="Exento", top=2.9*cm, left=23.7*cm,width=2*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="Imp. Total", top=2.9*cm, left=26*cm, width=2*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Line(left=0, top=3.5*cm, right = 29.7*cm, bottom = 3.5*cm),]
    
    class band_page_footer(ReportBand):
        height = 1*cm
        elements=[SystemField(expression='Pagina N°: %(page_number)s', top=0.1*cm, left=0, width=BAND_WIDTH,
                              style={'fontName':'Helvetica','fontSize':10, 'alignment':TA_CENTER}),]
    
        
    class band_detail(DetailBand):
        height = 0.4*cm
        elements = [ObjectValue(attribute_name='fecha_dd_mm_aaaa', top=0, left=0, width=2*cm),
                    ObjectValue(attribute_name='comp_completo_informe', top=0, left=2.1*cm, width=3.5*cm),
                    ObjectValue(attribute_name='cliente.razon_social', top=0, left=5.7*cm, width=7*cm, height=0.4*cm, truncate_overflow=True),
                    ObjectValue(attribute_name='cliente.cuit', top=0, left=13.7*cm, width=2.5*cm),
                    ObjectValue(attribute_name='neto',get_value=lambda instance: "%.2f" %(instance.neto*-1) if instance.tipo.startswith("NC") else "%.2f" %instance.neto,\
                                top=0, left=16.9*cm, width=2*cm,\
                                style={'alignment':TA_RIGHT}),
                    Label(text="0.00", top=0*cm, left=19.7*cm, width=2*cm, style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='iva21',get_value=lambda instance: "%.2f" %(instance.iva21*-1) if instance.tipo.startswith("NC") else "%.2f" %instance.iva21,\
                                top=0, left=21.4*cm,width=2*cm, style={'alignment':TA_RIGHT}),
                    Label(text="0.00", top=0*cm, left=23.7*cm,width=2*cm, style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='total',get_value=lambda instance: "%.2f" %(instance.total*-1) if instance.tipo.startswith("NC") else "%.2f" %instance.total,\
                                top=0, left=26*cm, width=2*cm, style={'alignment':TA_RIGHT}),
                    ]
        
    class band_summary(ReportBand):
        margin_top = 3*cm
        height = 0.5*cm
        elements = [
            ObjectValue(attribute_name='neto', top=0.1*cm, left=16.9*cm, width=2*cm,\
                action=FIELD_ACTION_SUM, get_value=lambda instance: float("%.2f" %(instance.neto*-1) if instance.tipo.startswith("NC") else "%.2f" %instance.neto), style={'alignment':TA_RIGHT}),
            ObjectValue(attribute_name='iva21', top=0.1*cm, left=21.4*cm,width=2*cm,\
                action=FIELD_ACTION_SUM, get_value=lambda instance: float("%.2f" %(instance.iva21*-1) if instance.tipo.startswith("NC") else "%.2f" %instance.iva21), style={'alignment':TA_RIGHT}),
            ObjectValue(attribute_name='total', top=0.1*cm, left=26*cm, width=2*cm,\
                action=FIELD_ACTION_SUM, get_value=lambda instance: float("%.2f" %(instance.total*-1) if instance.tipo.startswith("NC") else "%.2f" %instance.total), style={'alignment':TA_RIGHT}),]
        borders = {'all': RoundRect(radius=5, fill_color=grey, fill=True)}   

class IVACompras(Report):
    title = 'LIBRO IVA COMPRAS - RESOLUCION GENERAL AFIP 3419'
    page_size = landscape(A4)
        
    
    class band_page_header(ReportBand):    
        height = 4*cm
        elements = [SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH, 
                                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
                    Label(text="RAZON SOCIAL: %s" %RAZON_SOCIAL_EMPRESA, top=0.8*cm, width=BAND_WIDTH, 
                          style={'fontName':'Helvetica','fontSize':10}),
                    Label(text="CUIT: %s" %CUIT, top=1.2*cm, width=BAND_WIDTH, 
                          style={'fontName':'Helvetica','fontSize':10}),
                    Label(text="DOMICILIO COMERCIAL: %s" %DOMICILIO_COMERCIAL, top=1.5*cm, width=BAND_WIDTH, 
                          style={'fontName':'Helvetica','fontSize':10}),
                    SystemField(expression='Periodo: %(var:periodo)s', top=1.5*cm, left=23*cm, 
                          style={'fontName':'Helvetica','fontSize':10}), 
                    SystemField(expression='Fecha emisión: %(now:%d/%m/%Y)s', top=2*cm, width=8*cm),
                    SystemField(expression='Folio N°: %(page_number)s', top=2*cm, left=23*cm, 
                          style={'fontName':'Helvetica','fontSize':10}),
                    Line(left=0, top=2.7*cm, right = 29.7*cm, bottom = 2.7*cm),
                    #Encabezado de tabla
                    Label(text="Fecha", top=2.9*cm, left=0, width=2*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="Comprobante", top=2.9*cm, left=2*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="Razón Social", top=2.9*cm, left=5.5*cm, width=4.7*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="CUIT", top=2.9*cm, left=9.8*cm, width=2.3*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="Neto", top=2.9*cm, left=12.5*cm, width=2.2*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="Exento", top=2.9*cm, left=14.7*cm, width=1.8*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="IVA(10.5%)", top=2.9*cm, left=16.5*cm, width=1.9*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="IVA(21%)", top=2.9*cm, left=18.4*cm, width=1.7*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="IVA(27%)", top=2.9*cm, left=20.1*cm, width=1.8*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="Total", top=2.9*cm, left=21.9*cm, width=2.2*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="P. IVA", top=2.9*cm, left=24.1*cm, width=1.8*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Label(text="IIBB", top=2.9*cm, left=25.9*cm, width=1.8*cm, style={'fontName':'Helvetica-Bold','fontSize':10,'alignment':TA_CENTER}),
                    Line(left=0, top=3.5*cm, right = 29.7*cm, bottom = 3.5*cm),]
    
    class band_page_footer(ReportBand):
        height = 1*cm
        elements=[SystemField(expression='Pagina N°: %(page_number)s', top=0.1*cm, left=0, width=BAND_WIDTH,
                              style={'fontName':'Helvetica','fontSize':10, 'alignment':TA_CENTER}),]
        
    class band_detail(DetailBand):
        height = 0.4*cm
        elements = [ObjectValue(attribute_name='fecha_dd_mm_aaaa', top=0, left=0, width=2*cm),
                    ObjectValue(attribute_name='identificador_completo', top=0, left=2*cm, width=3.55*cm),
                    ObjectValue(attribute_name='proveedor.razon_social', top=0, left=5.5*cm, width=4.4*cm, height=0.4*cm, truncate_overflow=True),
                    ObjectValue(attribute_name='proveedor.cuit', top=0, left=9.8*cm, width=2.5*cm),
                    ObjectValue(attribute_name='neto', get_value=lambda instance: "%.2f" %instance.neto, top=0, left=12.5*cm, width=2.2*cm, style={'alignment':TA_RIGHT,'fontSize':9}),
                    ObjectValue(attribute_name='exento', get_value=lambda instance: "%.2f" %instance.exento, top=0, left=14.7*cm, width=1.8*cm, style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='iva105', get_value=lambda instance: "%.2f" %instance.iva105, top=0, left=16.5*cm, width=1.8*cm, style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='iva21', get_value=lambda instance: "%.2f" %instance.iva21, top=0, left=18.3*cm, width=1.8*cm, style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='iva27', get_value=lambda instance: "%.2f" %instance.iva27, top=0, left=20.1*cm, width=1.8*cm, style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='total',  get_value=lambda instance: "%.2f" %instance.total, top=0, left=21.9*cm, width=2.2*cm, style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='percepcion_iva', get_value=lambda instance: "%.2f" %instance.percepcion_iva, top=0, left=24.1*cm, width=1.8*cm, style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='ingresos_brutos', get_value=lambda instance: "%.2f" %instance.ingresos_brutos, top=0, left=25.9*cm, width=1.8*cm, style={'alignment':TA_RIGHT}),
                    ]
        
    class band_summary(ReportBand):
        margin_top = 2*cm
        height = 0.5*cm
        elements = [
            ObjectValue(attribute_name='neto', top=0.1*cm, left=12.5*cm, width=2.2*cm, action=FIELD_ACTION_SUM, get_text=lambda val: val[:-1], style={'alignment':TA_RIGHT}),
            ObjectValue(attribute_name='exento', top=0.1*cm, left=14.7*cm, width=1.8*cm, action=FIELD_ACTION_SUM, style={'alignment':TA_RIGHT}),
            ObjectValue(attribute_name='iva105', top=0.1*cm, left=16.5*cm,width=1.8*cm, action=FIELD_ACTION_SUM, style={'alignment':TA_RIGHT}),
            ObjectValue(attribute_name='iva21', top=0.1*cm, left=18.3*cm,width=1.8*cm, action=FIELD_ACTION_SUM, style={'alignment':TA_RIGHT}),
            ObjectValue(attribute_name='iva27', top=0.1*cm, left=20.1*cm,width=1.8*cm, action=FIELD_ACTION_SUM, style={'alignment':TA_RIGHT}),
            ObjectValue(attribute_name='total', top=0.1*cm, left=21.9*cm, width=2.2*cm, action=FIELD_ACTION_SUM, style={'alignment':TA_RIGHT}),
            ObjectValue(attribute_name='percepcion_iva', top=0.1*cm, left=24.1*cm, width=1.8*cm, action=FIELD_ACTION_SUM, style={'alignment':TA_RIGHT}),
            ObjectValue(attribute_name='ingresos_brutos', top=0.1*cm, left=25.9*cm, width=1.8*cm, action=FIELD_ACTION_SUM, style={'alignment':TA_RIGHT}),
            ]
        borders = {'all': RoundRect(radius=4, fill_color=grey, fill=True)}   


def impr_comprobante(request, pk):
    venta = Venta.objects.get(pk=pk)
    if venta.aprobado:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="somefilename.pdf"'
        p = Canvas(response, pagesize=A4)
        #p.translate(cm,cm)
        #set_trace()
        p.setFont('Helvetica-Bold', 16)
        if venta.tipo[-1:] == 'A':
            p.drawString(10.7*cm, 28.2*cm, 'A')
        elif venta.tipo[-1:] == 'B':
            p.drawString(10.7*cm, 28.2*cm, 'B')
        p.setFont('Helvetica', 13)
        if venta.tipo[:2] == 'FA':
            p.drawString(12.7*cm, 26.8*cm, 'FACTURA')
        elif venta.tipo[:2] == 'NC':
            p.drawString(12.7*cm, 26.8*cm, 'NOTA DE CREDITO')
        elif venta.tipo[:2] == 'ND':
            p.drawString(12.7*cm, 26.8*cm, 'NOTA DE DEBITO')
        p.drawString(12.1*cm, 27.7*cm, "N° %s  -" %venta.pto_vta_full())
        p.drawString(14.5*cm, 27.7*cm, venta.num_comp_full())
        p.drawString(17.2*cm, 26*cm, venta.fecha_dd_mm_aaaa())
        p.setFont('Helvetica', 10)
        p.drawString(3.25*cm, 23.1*cm, "%s" %venta.cliente.id)
        p.drawString(4.5*cm, 23.1*cm, venta.cliente.razon_social)
        p.drawString(4.5*cm, 22.0*cm, venta.cliente.direccion)
        p.drawString(16*cm, 23*cm, venta.cliente.cuit)
        p.drawString(16*cm, 22.5*cm, venta.cliente.localidad)
        p.drawString(16*cm, 22*cm, venta.cliente.provincia)
        p.drawString(7*cm, 21.0*cm, venta.condicion_venta.descripcion)
        detalle = venta.detalle_venta_set.all()
        inicio_y = 19.5
        alto_item = 0.4
        i = 0
        p.setFont('Helvetica', 7)
        for item in detalle:
            p.drawString(4*cm, (inicio_y-i*alto_item)*cm, "" if str(item.get_cod()) == "0" else str(item.get_cod())+"    "+str(item.get_cod_fab()))
            p.drawString(8*cm, (inicio_y-i*alto_item)*cm, "%.2f" %item.cantidad)
            p.drawString(9*cm, (inicio_y-i*alto_item)*cm, item.get_articulo()[:45])
            p.drawRightString(16.3*cm, (inicio_y-i*alto_item)*cm, "%.2f" %(item.precio_unitario if venta.tipo[-1:] == 'A' else item.precio_unitario*Decimal(1.21)))
            p.setFont('Helvetica', 5)
            p.drawRightString(17.3*cm, (inicio_y-i*alto_item)*cm, "-%.2f%%" %(item.descuento))
            p.setFont('Helvetica', 7)
            p.drawRightString(18.8*cm, (inicio_y-i*alto_item)*cm, "%.2f" %(item.neto() if venta.tipo[-1:] == 'A' else item.neto()*Decimal(1.21)))
            i+=1
        p.setFont('Helvetica', 12)
        p.drawString(15*cm, 5.5*cm, "Subtotal")
        p.drawRightString(18.5*cm, 5.5*cm, "%.2f" %(venta.subtotal if venta.tipo[-1:] == 'A' else venta.total))
        p.drawString(15*cm, 5*cm, "Descuento")
        p.drawRightString(18.5*cm, 5*cm, "-%.2f" %venta.descuento_importe())
        p.drawString(15*cm, 4.5*cm, "Neto")
        p.drawRightString(18.5*cm, 4.5*cm, "%.2f" %(venta.neto if venta.tipo[-1:] == 'A' else venta.total))
        p.drawString(15*cm, 4*cm, "IVA 21%")
        p.drawRightString(18.5*cm, 4*cm, "%.2f" %(venta.iva21 if venta.tipo[-1:] == 'A' else 0.00))
        p.setFont('Helvetica-Bold', 12)
        p.drawString(15*cm, 3.3*cm, "Total")
        p.drawRightString(18.5*cm, 3.3*cm, "%.2f" %venta.total)
        p.setFont('Helvetica', 13)
        p.drawString(15*cm, 1.7*cm, "CAE: %s" %venta.cae)
        p.drawString(15*cm, 1.2*cm, "Fecha Vto: %s" %venta.vto_cae_dd_mm_aaaa())
        p.showPage()
        p.save()
        return response
    
def impr_recibo(request,pk):
    mitad = 14.8*cm
    mita = 14.8
    #Inicializo todos los comprobantes y valores
    recibo = Recibo.objects.get(pk=pk)
    a_cuenta = recibo.get_a_credito()
    #Datos de comprobantes
    comprobantes = recibo.detalle_cobro_set.all()
    #a_cuenta = recibo.cobranza_a_cuenta_set.all()
    #credito_anterior = recibo.cobranza_credito_anterior_set.all()
    #Datos de valores
    valores = recibo.dinero_set.all()
    #transferencia = recibo.transferenciabancariaentrante_set.all()
    #efectivo = recibo.dinero_set.all()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="somefilename.pdf"'
    p = Canvas(response, pagesize=A4)
    #Numero de recibo
    p.setFont('Helvetica-Bold', 16)
    p.drawString(15.7*cm, 13*cm, recibo.numero_full)
    #Fecha
    p.setFont('Helvetica', 13)
    p.drawString(17*cm, 12*cm, str(recibo.fecha.day))
    p.drawString(18*cm, 12*cm, str(recibo.fecha.month))
    p.drawString(19*cm, 12*cm, str(recibo.fecha.year))
    #Datos del cliente
    p.setFont('Helvetica', 13)
    p.drawString(12*cm, 11*cm, recibo.cliente.razon_social)
    p.drawString(12*cm, 10.3*cm, recibo.cliente.get_cond_iva_display())
    p.drawString(12*cm, 9.8*cm, "CUIT: %s" %recibo.cliente.cuit)
    p.drawString(12*cm, 9.3*cm, recibo.cliente.direccion)
    p.drawString(12*cm, 8.8*cm, "%s - %s" %(recibo.cliente.localidad, recibo.cliente.get_provincia_display()))
    inicio_y = 6.2
    alto_item = 0.4
    i = 0
    p.setFont('Helvetica', 7)
    if a_cuenta and a_cuenta>0:
        p.drawString(3.4*cm, (inicio_y-i*alto_item)*cm, "A cuenta")
        p.drawRightString(7.4*cm, (inicio_y-i*alto_item)*cm, "%.2f" %a_cuenta)
        i+=1
    if recibo.credito_anterior and recibo.credito_anterior>0:
        p.drawString(3.4*cm, (inicio_y-i*alto_item)*cm, "Credito anterior")
        p.drawRightString(7.4*cm, (inicio_y-i*alto_item)*cm, "-%.2f" %recibo.credito_anterior)
        i+=1
    for item in comprobantes:
        p.drawString(2*cm, (inicio_y-i*alto_item)*cm, item.venta.tipo)
        p.drawString(3.4*cm, (inicio_y-i*alto_item)*cm, item.venta.num_comp_full())
        p.drawString(5.1*cm, (inicio_y-i*alto_item)*cm, item.venta.fecha_dd_mm_aaaa())
        p.drawRightString(7.4*cm, (inicio_y-i*alto_item)*cm, item.monto_2d())
        i+=1
    #Cheques
    i=0
    for item in valores:
        try:
            p.drawString(10*cm, (inicio_y-i*alto_item)*cm, item.chequetercero.numero)
            p.drawString(11.7*cm, (inicio_y-i*alto_item)*cm, item.chequetercero.cuit_titular)
            p.drawString(13.8*cm, (inicio_y-i*alto_item)*cm, item.chequetercero.fecha_dd_mm_aaaa())
            p.drawString(15.4*cm, (inicio_y-i*alto_item)*cm, item.chequetercero.banco.nombre[:20])
            p.drawRightString(20*cm, (inicio_y-i*alto_item)*cm, "%.2f" %item.monto)
        except Dinero.DoesNotExist:
            try:
                item.transferenciabancariaentrante
                p.drawString(10*cm, (inicio_y-i*alto_item)*cm, "Transferencia Bancaria")
                p.drawRightString(20*cm, (inicio_y-i*alto_item)*cm, "%.2f" %item.monto)
            except Dinero.DoesNotExist:
                p.drawString(10*cm, (inicio_y-i*alto_item)*cm, "Efectivo" if item.monto >=0 else "Efectivo - SU VUELTO")
                p.drawRightString(20*cm, (inicio_y-i*alto_item)*cm, "%.2f" %item.monto)
        finally:
            i+=1
    #for item in transferencia:
    #    p.drawString(10*cm, (inicio_y-i*alto_item)*cm, "Transferencia Bancaria")
    #    p.drawRightString(20*cm, (inicio_y-i*alto_item)*cm, "%.2f" %item.monto)
    #    i+=1
    #for item in efectivo:
    #    p.drawString(10*cm, (inicio_y-i*alto_item)*cm, "Efectivo")
    #    p.drawRightString(20*cm, (inicio_y-i*alto_item)*cm, "%.2f" %item.monto)
    #    i+=1
    p.setFont('Helvetica-Bold', 12)
    p.drawString(7.5*cm, 2.3*cm, recibo.total_str)
    p.drawString(18*cm, 2.3*cm, recibo.total_str)
    try:
        letra=(to_word(int(recibo.total_str.split('.')[0].strip()))+"con "+to_word(int(recibo.total_str.split('.')[1].strip()))+"centavos").lower()
    except IndexError:
        letra=(to_word(int(recibo.total_str.split('.')[0].strip()))).lower()  
    p.setFont('Helvetica', 9)
    p.drawString(2*cm, 7.5*cm, letra)  
    ######################################################
    ##############RECIBO DUPLICADO########################
    ######################################################
    #Numero de recibo
    p.setFont('Helvetica-Bold', 16)
    p.drawString(15.7*cm, mitad+13*cm, recibo.numero_full)
    #Fecha
    p.setFont('Helvetica', 13)
    p.drawString(17*cm, mitad+12*cm, str(recibo.fecha.day))
    p.drawString(18*cm, mitad+12*cm, str(recibo.fecha.month))
    p.drawString(19*cm, mitad+12*cm, str(recibo.fecha.year))
    #Datos del cliente
    p.setFont('Helvetica', 13)
    p.drawString(12*cm, mitad+11*cm, recibo.cliente.razon_social)
    p.drawString(12*cm, mitad+10.3*cm, recibo.cliente.get_cond_iva_display())
    p.drawString(12*cm, mitad+9.8*cm, "CUIT: %s" %recibo.cliente.cuit)
    p.drawString(12*cm, mitad+9.3*cm, recibo.cliente.direccion)
    p.drawString(12*cm, mitad+8.8*cm, "%s - %s" %(recibo.cliente.localidad, recibo.cliente.get_provincia_display()))
    #Datos de comprobantes
    #comprobantes = recibo.detalle_cobro_set.all()
    inicio_y = mita+6.2
    alto_item = 0.4
    i = 0
    p.setFont('Helvetica', 7)
    if a_cuenta and a_cuenta>0:
        p.drawString(3.4*cm, (inicio_y-i*alto_item)*cm, "A cuenta")
        p.drawRightString(7.4*cm, (inicio_y-i*alto_item)*cm, "%.2f" %a_cuenta)
        i+=1
    if recibo.credito_anterior and recibo.credito_anterior>0:
        p.drawString(3.4*cm, (inicio_y-i*alto_item)*cm, "Credito anterior")
        p.drawRightString(7.4*cm, (inicio_y-i*alto_item)*cm, "-%.2f" %recibo.credito_anterior)
        i+=1
    for item in comprobantes:
        p.drawString(2*cm, (inicio_y-i*alto_item)*cm, item.venta.tipo)
        p.drawString(3.4*cm, (inicio_y-i*alto_item)*cm, item.venta.num_comp_full())
        p.drawString(5.1*cm, (inicio_y-i*alto_item)*cm, item.venta.fecha_dd_mm_aaaa())
        p.drawRightString(7.4*cm, (inicio_y-i*alto_item)*cm, item.monto_2d())
        i+=1
    i=0
    for item in valores:
        try:
            p.drawString(10*cm, (inicio_y-i*alto_item)*cm, item.chequetercero.numero)
            p.drawString(11.7*cm, (inicio_y-i*alto_item)*cm, item.chequetercero.cuit_titular)
            p.drawString(13.8*cm, (inicio_y-i*alto_item)*cm, item.chequetercero.fecha_dd_mm_aaaa())
            p.drawString(15.4*cm, (inicio_y-i*alto_item)*cm, item.chequetercero.banco.nombre[:20])
            p.drawRightString(20*cm, (inicio_y-i*alto_item)*cm, "%.2f" %item.monto)
        except Dinero.DoesNotExist:
            try:
                item.transferenciabancariaentrante
                p.drawString(10*cm, (inicio_y-i*alto_item)*cm, "Transferencia Bancaria")
                p.drawRightString(20*cm, (inicio_y-i*alto_item)*cm, "%.2f" %item.monto)
            except Dinero.DoesNotExist:
                p.drawString(10*cm, (inicio_y-i*alto_item)*cm, "Efectivo" if item.monto >=0 else "Efectivo - SU VUELTO")
                p.drawRightString(20*cm, (inicio_y-i*alto_item)*cm, "%.2f" %item.monto)
        finally:
            i+=1
    p.setFont('Helvetica-Bold', 12)
    p.drawString(7.5*cm, mitad+2.3*cm, recibo.total_str)
    p.drawString(18*cm, mitad+2.3*cm, recibo.total_str)
    try:
        letra=(to_word(int(recibo.total_str.split('.')[0].strip()))+"con "+to_word(int(recibo.total_str.split('.')[1].strip()))+"centavos").lower()
    except IndexError:
        letra=(to_word(int(recibo.total_str.split('.')[0].strip()))).lower()  
    p.setFont('Helvetica', 9)
    p.drawString(2*cm, mitad+7.5*cm, letra)
    p.showPage()
    p.save()
    return response

class ResumenCuenta(Report):
    title = 'RESUMEN DE CUENTA DE CLIENTES'
    page_size = A4
    margin_left = 1*cm
    margin_top = 1*cm
    margin_right = 1*cm
    margin_bottom = 1*cm
    
    class band_page_header(ReportBand):    
        height = 4*cm
        elements = [SystemField(expression='%(report_title)s', top=1.4*cm, left=0, width=BAND_WIDTH, 
                                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
                    Label(text=RAZON_SOCIAL_EMPRESA, top=0.5*cm, width=BAND_WIDTH, 
                          style={'fontName':'Helvetica-Bold','fontSize':12, 'alignment': TA_CENTER}),
                    SystemField(expression='Fecha emisión: %(now:%d/%m/%Y)s', top=0*cm, left=14.4*cm, width=8*cm),
                    Line(left=0, top=2.5*cm, right = 21*cm, bottom = 2.5*cm),
                    #Encabezado de tabla
                    Label(text="Datos", top=2.7*cm, left=1*cm, width=2*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Debe", top=2.7*cm, left=10*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Haber", top=2.7*cm, left=14*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Saldo", top=2.7*cm, left=17*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Line(left=0, top=3.2*cm, right = 29.7*cm, bottom = 3.2*cm),]
        
    class band_detail(DetailBand):
        height = 0.5*cm
        elements = [
                    ObjectValue(attribute="", get_value=lambda instance:"%s" %instance['fecha'] if not isinstance(instance['fecha'], date) else "%s -- %s / %s" %(instance['fecha'].strftime("%d/%m/%Y"),instance['tipo'],instance['numero']),left=1*cm, width=6.5*cm),                
                    ObjectValue(attribute_name='debe',get_value=lambda instance: "%.2f" %instance['debe'] if isinstance(instance['debe'],Decimal) else instance['debe'],left=10*cm, width=2.5*cm,style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='haber',get_value=lambda instance: "%.2f" %instance['haber'] if isinstance(instance['haber'],Decimal) else instance['haber'],left=14*cm,width=2.5*cm,style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='saldo',get_value=lambda instance: "%.2f" %instance['saldo'] if isinstance(instance['saldo'],Decimal) else instance['saldo'],left=16.6*cm,width=2.5*cm,style={'alignment':TA_RIGHT}),      
                    ]
    groups=[
            ReportGroup(attribute_name='cliente_id',
                        band_header=ReportBand(
                                               height = 0.7*cm,
                                               borders = {'bottom': Line(stroke_color=black)},
                                               elements=[Label(text="CLIENTE:", top=0.1*cm, left=1*cm, 
                                                               style={'fontName':'Helvetica','fontSize':12}),
                                                         ObjectValue(attribute_name='cliente_id', top=0.1*cm, left=3*cm, style={'fontName':'Helvetica-Bold','fontSize':10}),
                                                         ObjectValue(attribute_name='razon_social', top=0.1*cm, left=4.5*cm, width=15*cm, style={'fontName':'Helvetica-Bold','fontSize':10}),
                                                         ])
                        )
            ]
    
class ComposicionSaldo(Report):
    title = 'COMPOSICION DE SALDO'
    page_size = A4
    margin_left = 1*cm
    margin_top = 1*cm
    margin_right = 1*cm
    margin_bottom = 1*cm
    
    class band_page_header(ReportBand):    
        height = 4*cm
        elements = [SystemField(expression='%(report_title)s', top=1.4*cm, left=0, width=BAND_WIDTH, 
                                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
                    Label(text=RAZON_SOCIAL_EMPRESA, top=0.5*cm, width=BAND_WIDTH, 
                          style={'fontName':'Helvetica-Bold','fontSize':12, 'alignment': TA_CENTER}),
                    SystemField(expression='Fecha emisión: %(now:%d/%m/%Y)s', top=0*cm, left=14.4*cm, width=8*cm),
                    Line(left=0, top=2.5*cm, right = 21*cm, bottom = 2.5*cm),
                    #Encabezado de tabla
                    Label(text="Datos", top=2.7*cm, left=1*cm, width=2*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Total", top=2.7*cm, left=10*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Saldo", top=2.7*cm, left=14*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Saldo Total", top=2.7*cm, left=17*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Line(left=0, top=3.2*cm, right = 29.7*cm, bottom = 3.2*cm),]
        
    class band_detail(DetailBand):
        height = 0.7*cm
        elements = [
                    ObjectValue(attribute="", get_value=lambda instance:"%s" %instance['fecha'] if not isinstance(instance['fecha'], date) else "%s -- %s / %s" %(instance['fecha'].strftime("%d/%m/%Y"),instance['tipo'],instance['numero']),left=1*cm, width=7.5*cm, style={'fontName':'Helvetica','fontSize':11}),                
                    ObjectValue(attribute_name='total_c',get_value=lambda instance: "%.2f" %instance['total_c'] if isinstance(instance['total_c'],Decimal) else instance['debe'],left=10*cm, width=2.5*cm,style={'alignment':TA_RIGHT, 'fontName':'Helvetica','fontSize':11}),
                    ObjectValue(attribute_name='saldo_c',get_value=lambda instance: "%.2f" %instance['saldo_c'] if isinstance(instance['saldo_c'],Decimal) else instance['haber'],left=14*cm,width=2.5*cm,style={'alignment':TA_RIGHT, 'fontName':'Helvetica','fontSize':11}),
                    ObjectValue(attribute_name='saldo_t',get_value=lambda instance: "%.2f" %instance['saldo_t'] if isinstance(instance['saldo_t'],Decimal) else instance['saldo'],left=16.6*cm,width=2.5*cm,style={'alignment':TA_RIGHT, 'fontName':'Helvetica','fontSize':11}),      
                    ]
    groups=[
            ReportGroup(attribute_name='cliente_id',
                        band_header=ReportBand(
                                               height = 0.7*cm,
                                               borders = {'bottom': Line(stroke_color=black)},
                                               elements=[Label(text="CLIENTE:", top=0.1*cm, left=1*cm, 
                                                               style={'fontName':'Helvetica','fontSize':12}),
                                                         ObjectValue(attribute_name='cliente_id', top=0.1*cm, left=3*cm, style={'fontName':'Helvetica-Bold','fontSize':10}),
                                                         ObjectValue(attribute_name='razon_social', top=0.1*cm, left=4.5*cm, width=15*cm, style={'fontName':'Helvetica-Bold','fontSize':10}),
                                                         ])
                        )
            ]
    subreports=[
                SubReport(
                          queryset_string="%(object)s['detalle_venta']",
                          band_detail=ReportBand(
                                                 height=0.4*cm,
                                                 elements=[
                                                           ObjectValue(attribute_name='cantidad', get_value=lambda instance: "0.00" if instance['cantidad'].is_zero() else "%.2f" %instance['cantidad'], left=2.8*cm,style={'fontName':'Helvetica','fontSize':10}),
                                                           ObjectValue(attribute_name='articulo', truncate_overflow=True, height=0.4*cm, left=4*cm, width=10*cm, style={'fontName':'Helvetica','fontSize':10}),
                                                           ObjectValue(attribute_name='total', get_value=lambda instance: "0.00" if instance['total'].is_zero() else "%.2f" %instance['total'], left=15*cm, style={'fontName':'Helvetica','fontSize':10})]))]     
    

class ResumenCuentaProveedores(Report):
    title = 'RESUMEN DE CUENTA DE PROVEEDORES'
    page_size = A4
    margin_left = 1*cm
    margin_top = 1*cm
    margin_right = 1*cm
    margin_bottom = 1*cm
    
    class band_page_header(ReportBand):    
        height = 4*cm
        elements = [SystemField(expression='%(report_title)s', top=1.4*cm, left=0, width=BAND_WIDTH, 
                                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
                    Label(text=RAZON_SOCIAL_EMPRESA, top=0.5*cm, width=BAND_WIDTH, 
                          style={'fontName':'Helvetica-Bold','fontSize':12, 'alignment': TA_CENTER}),
                    SystemField(expression='Fecha emisión: %(now:%d/%m/%Y)s', top=0*cm, left=14.4*cm, width=8*cm),
                    Line(left=0, top=2.5*cm, right = 21*cm, bottom = 2.5*cm),
                    #Encabezado de tabla
                    Label(text="Datos", top=2.7*cm, left=1*cm, width=2*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Debe", top=2.7*cm, left=10*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Haber", top=2.7*cm, left=14*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Saldo", top=2.7*cm, left=17*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Line(left=0, top=3.2*cm, right = 29.7*cm, bottom = 3.2*cm),]
        
    class band_detail(DetailBand):
        height = 0.5*cm
        elements = [
                    ObjectValue(attribute="", get_value=lambda instance:"%s" %instance['fecha'] if not isinstance(instance['fecha'], date) else "%s -- %s / %s" %(instance['fecha'].strftime("%d/%m/%Y"),instance['tipo'],instance['numero']),left=1*cm, width=6.5*cm),                
                    ObjectValue(attribute_name='debe',get_value=lambda instance: "%.2f" %instance['debe'] if isinstance(instance['debe'],Decimal) else instance['debe'],left=10*cm, width=2.5*cm,style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='haber',get_value=lambda instance: "%.2f" %instance['haber'] if isinstance(instance['haber'],Decimal) else instance['haber'],left=14*cm,width=2.5*cm,style={'alignment':TA_RIGHT}),
                    ObjectValue(attribute_name='saldo',get_value=lambda instance: "%.2f" %instance['saldo'] if isinstance(instance['saldo'],Decimal) else instance['saldo'],left=16.6*cm,width=2.5*cm,style={'alignment':TA_RIGHT}),      
                    ]
    groups=[
            ReportGroup(attribute_name='proveedor_id',
                        band_header=ReportBand(
                                               height = 0.7*cm,
                                               borders = {'bottom': Line(stroke_color=black)},
                                               elements=[Label(text="PROVEEDOR:", top=0.1*cm, left=1*cm, 
                                                               style={'fontName':'Helvetica','fontSize':12}),
                                                         ObjectValue(attribute_name='proveedor_id', top=0.1*cm, left=6*cm, style={'fontName':'Helvetica-Bold','fontSize':10}),
                                                         ObjectValue(attribute_name='razon_social', top=0.1*cm, left=7.5*cm, width=12.5*cm, style={'fontName':'Helvetica-Bold','fontSize':10}),
                                                         ])
                        )
            ]
    
class ComposicionSaldoProveedores(Report):
    title = 'COMPOSICION DE SALDO'
    page_size = A4
    margin_left = 1*cm
    margin_top = 1*cm
    margin_right = 1*cm
    margin_bottom = 1*cm
    
    class band_page_header(ReportBand):    
        height = 4*cm
        elements = [SystemField(expression='%(report_title)s', top=1.4*cm, left=0, width=BAND_WIDTH, 
                                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
                    Label(text=RAZON_SOCIAL_EMPRESA, top=0.5*cm, width=BAND_WIDTH, 
                          style={'fontName':'Helvetica-Bold','fontSize':12, 'alignment': TA_CENTER}),
                    SystemField(expression='Fecha emisión: %(now:%d/%m/%Y)s', top=0*cm, left=14.4*cm, width=8*cm),
                    Line(left=0, top=2.5*cm, right = 21*cm, bottom = 2.5*cm),
                    #Encabezado de tabla
                    Label(text="Datos", top=2.7*cm, left=1*cm, width=2*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Total", top=2.7*cm, left=10*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Saldo", top=2.7*cm, left=14*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Label(text="Saldo Total", top=2.7*cm, left=17*cm, width=3.5*cm, style={'fontName':'Helvetica-Bold','fontSize':12,'alignment':TA_CENTER}),
                    Line(left=0, top=3.2*cm, right = 29.7*cm, bottom = 3.2*cm),]
        
    class band_detail(DetailBand):
        height = 0.7*cm
        elements = [
                    ObjectValue(attribute="", get_value=lambda instance:"%s" %instance['fecha'] if not isinstance(instance['fecha'], date) else "%s -- %s / %s" %(instance['fecha'].strftime("%d/%m/%Y"),instance['tipo'],instance['numero']),left=1*cm, width=7.5*cm, style={'fontName':'Helvetica','fontSize':11}),                
                    ObjectValue(attribute_name='total_c',get_value=lambda instance: "%.2f" %instance['total_c'] if isinstance(instance['total_c'],Decimal) else instance['debe'],left=10*cm, width=2.5*cm,style={'alignment':TA_RIGHT, 'fontName':'Helvetica','fontSize':11}),
                    ObjectValue(attribute_name='saldo_c',get_value=lambda instance: "%.2f" %instance['saldo_c'] if isinstance(instance['saldo_c'],Decimal) else instance['haber'],left=14*cm,width=2.5*cm,style={'alignment':TA_RIGHT, 'fontName':'Helvetica','fontSize':11}),
                    ObjectValue(attribute_name='saldo_t',get_value=lambda instance: "%.2f" %instance['saldo_t'] if isinstance(instance['saldo_t'],Decimal) else instance['saldo'],left=16.6*cm,width=2.5*cm,style={'alignment':TA_RIGHT, 'fontName':'Helvetica','fontSize':11}),      
                    ]
    groups=[
            ReportGroup(attribute_name='proveedor_id',
                        band_header=ReportBand(
                                               height = 0.7*cm,
                                               borders = {'bottom': Line(stroke_color=black)},
                                               elements=[Label(text="PROVEEDOR:", top=0.1*cm, left=1*cm, 
                                                               style={'fontName':'Helvetica','fontSize':12}),
                                                         ObjectValue(attribute_name='proveedor_id', top=0.1*cm, left=3*cm, style={'fontName':'Helvetica-Bold','fontSize':10}),
                                                         ObjectValue(attribute_name='razon_social', top=0.1*cm, left=4.5*cm, width=15*cm, style={'fontName':'Helvetica-Bold','fontSize':10}),
                                                         ])
                        )
            ]
    subreports=[
                SubReport(
                          queryset_string="%(object)s['detalle_compra']",
                          band_detail=ReportBand(
                                                 height=0.4*cm,
                                                 elements=[
                                                           ObjectValue(attribute_name='cantidad', get_value=lambda instance: "0.00" if instance['cantidad'].is_zero() else "%.2f" %instance['cantidad'], left=2.8*cm,style={'fontName':'Helvetica','fontSize':10}),
                                                           ObjectValue(attribute_name='detalle', truncate_overflow=True, height=0.4*cm, left=4*cm, width=10*cm, style={'fontName':'Helvetica','fontSize':10}),
                                                           ObjectValue(attribute_name='total', get_value=lambda instance: "0.00" if instance['total'].is_zero() else "%.2f" %instance['total'], left=15*cm, style={'fontName':'Helvetica','fontSize':10})]))]     
    
    
    
class OrdenPagoReport(Report):
    page_size = A4
    margin_left = 1*cm
    margin_top = 1*cm
    margin_right = 1*cm
    margin_bottom = 1*cm
    
    class band_detail(DetailBand):
        height=6*cm
        division_horizontal_top=3#En centimetros
        division_vertical_left=10
        elements = [#RECUADRO HEADER
                    Line(left=0*cm, top=0*cm, right = 19*cm, bottom = 0*cm),
                    Line(left=0*cm, top=0*cm, right = 0*cm, bottom = 5.3*cm),
                    Line(left=19*cm, top=0*cm, right = 19*cm, bottom = 5.3*cm),
                    Line(left=0*cm, top=5.3*cm, right = 19*cm, bottom = 5.3*cm),
                    #DATOS DE LA EMPRESA
                    Label(text=RAZON_SOCIAL_EMPRESA[:35], top=0.4*cm, left=0.2*cm, width=10*cm, 
                          style={'fontName':'Helvetica-Bold','fontSize':13}),
                    Label(text=RAZON_SOCIAL_EMPRESA[35:], top=1.2*cm, left=0.2*cm, width=10*cm, 
                          style={'fontName':'Helvetica','fontSize':11}),
                    Label(text=DOMICILIO_COMERCIAL, top=1.8*cm, left=0.2*cm, width=10*cm, 
                          style={'fontName':'Helvetica','fontSize':11}),
                    Label(text=CIUDAD+" - CORDOBA", top=2.4*cm, left=0.2*cm, width=10*cm, 
                          style={'fontName':'Helvetica','fontSize':11}),
                    #DIVISION VERTICAL
                    Line(left=division_vertical_left*cm, top=0*cm, right = division_vertical_left*cm, bottom = division_horizontal_top*cm),
                    #DATOS DE LA ORDEN DE PAGO
                    ObjectValue(attribute_name="numero_full", left=(division_vertical_left+0.5)*cm, top=1*cm, width=10*cm,\
                                display_format="LIQUIDACION  %s",style={'fontName':'Helvetica-Bold','fontSize':14}),
                    ObjectValue(attribute_name="fecha_dd_mm_aaaa", left=(division_vertical_left+0.5)*cm, top=1.8*cm,\
                                display_format="Fecha: %s",style={'fontName':'Helvetica','fontSize':12}),
                    #DIVISION HORIZONTAL
                    Line(left=0*cm, top=division_horizontal_top*cm, right = 19*cm, bottom = division_horizontal_top*cm),
                    #CABECERA DE LA ORDEN DE PAGO
                    Label(text="Señor(es):", top=(division_horizontal_top+0.5)*cm, left=0.2*cm,\
                          style={'fontName':'Helvetica','fontSize':10}),
                    ObjectValue(attribute_name="proveedor_razon_social",left=2.2*cm,top=(division_horizontal_top+0.5)*cm, width=8*cm,\
                                style={'fontName':'Helvetica-Bold','fontSize':10},truncate_overflow=True, height=0.5*cm),
                    Label(text="Domicilio:", top=(division_horizontal_top+1)*cm, left=0.2*cm,\
                          style={'fontName':'Helvetica','fontSize':10}),
                    ObjectValue(attribute_name="proveedor_direccion", truncate_overflow=True,left=2.2*cm,top=(division_horizontal_top+1)*cm, width=8*cm,\
                                style={'fontName':'Helvetica-Bold','fontSize':10},height=0.5*cm),
                    Label(text="Localidad:", top=(division_horizontal_top+1.5)*cm, left=0.2*cm,\
                          style={'fontName':'Helvetica','fontSize':10}),
                    ObjectValue(attribute_name="proveedor_localidad",left=2.2*cm,top=(division_horizontal_top+1.5)*cm, width=8*cm,\
                                style={'fontName':'Helvetica-Bold','fontSize':10},truncate_overflow=True,height=0.5*cm),
                    Label(text="IVA:", top=(division_horizontal_top+0.5)*cm, left=11*cm,\
                          style={'fontName':'Helvetica','fontSize':10}),
                    ObjectValue(attribute_name="proveedor_condicion_iva",left=13*cm,top=(division_horizontal_top+0.5)*cm,\
                                style={'fontName':'Helvetica-Bold','fontSize':10}),
                    Label(text="CUIT:", top=(division_horizontal_top+1)*cm, left=11*cm,\
                          style={'fontName':'Helvetica','fontSize':10}),
                    ObjectValue(attribute_name="proveedor_cuit",left=13*cm,top=(division_horizontal_top+1)*cm,\
                                style={'fontName':'Helvetica-Bold','fontSize':10}),
                    Label(text="Ing. Brutos:", top=(division_horizontal_top+1.5)*cm, left=11*cm,\
                          style={'fontName':'Helvetica','fontSize':10}),
                    ObjectValue(attribute_name="proveedor_codigo_ingresos_brutos",left=13*cm,top=(division_horizontal_top+1.5)*cm,\
                                style={'fontName':'Helvetica-Bold','fontSize':10}),
                    ]
    subreports=[SubReport(queryset_string="%(object)s['detalle_pago_set']",
                          band_header=ReportBand(elements=[Label(text="DETALLE DE PAGO", top=0*cm, left=0*cm, width=19*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           Line(left=0*cm, top=0.4*cm, right = 19*cm, bottom = 0.4*cm),
                                                           Label(text="Fecha", top=0.5*cm, left=0*cm, width=5*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           Label(text="Detalle", top=0.5*cm, left=5*cm, width=10*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           Label(text="Importe", top=0.5*cm, left=15*cm, width=4*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER})],
                                                           
                                                 ),
                          band_detail=ReportBand(height=0.4*cm,
                                                 elements=[ObjectValue(attribute_name="compra_fecha_dd_mm_aaaa",left=0*cm,width=5*cm,\
                                                                       style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           ObjectValue(attribute_name="compra_identificador_completo",left=5*cm,width=10*cm,\
                                                                       style={'fontName':'Helvetica','fontSize':8,'alignment':TA_LEFT}),
                                                           ObjectValue(attribute_name="monto", get_value=lambda instance: "%.2f" %instance['monto'],\
                                                                       left=15*cm,width=4*cm, style={'fontName':'Helvetica','fontSize':8,'alignment':TA_RIGHT})
                                                           ]),
                          band_footer=ReportBand(elements=[Label(text="TOTAL", top=0.5*cm, left=12*cm, width=5*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':9,'alignment':TA_CENTER},\
                                                                 borders = {'top': 1}),
                                                           ObjectValue(attribute_name="monto",\
                                                                       left=15*cm,width=4*cm, style={'fontName':'Helvetica','fontSize':8,'alignment':TA_RIGHT},\
                                                                       action=FIELD_ACTION_SUM, top=0.5*cm,\
                                                                       borders = {'top': 1})
                                                           ]
                         )),
                SubReport(queryset_string="%(object)s['dinero_set']",
                          band_header=ReportBand(elements=[Label(text="DETALLE DE VALORES", top=0*cm, left=0*cm, width=19*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           Line(left=0*cm, top=0.4*cm, right = 19*cm, bottom = 0.4*cm),
                                                           Label(text="Tipo", top=0.5*cm, left=0*cm, width=2*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           Label(text="Entidad Emisora", top=0.5*cm, left=2*cm, width=5*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           Label(text="Comprob", top=0.5*cm, left=7*cm, width=2*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           Label(text="CUIT", top=0.5*cm, left=9*cm, width=4*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           Label(text="Fecha", top=0.5*cm, left=13*cm, width=3*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           Label(text="Importe", top=0.5*cm, left=16*cm, width=3*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER})],
                                                 ),
                          band_detail=ReportBand(height=0.4*cm,
                                                 elements=[ObjectValue(attribute_name="tipo_valor", left=0*cm,width=2*cm,\
                                                                       style={'fontName':'Helvetica','fontSize':8,'alignment':TA_LEFT}),
                                                           ObjectValue(attribute_name="entidad", left=2*cm,width=5*cm,\
                                                                       style={'fontName':'Helvetica','fontSize':8,'alignment':TA_LEFT}),
                                                           ObjectValue(attribute_name="num_comprobante", left=7*cm,width=2*cm,\
                                                                       style={'fontName':'Helvetica','fontSize':8,'alignment':TA_LEFT}),
                                                           ObjectValue(attribute_name="CUIT", left=9*cm,width=4*cm,\
                                                                       style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           ObjectValue(attribute_name="FECHA", left=13*cm,width=3*cm,\
                                                                       style={'fontName':'Helvetica','fontSize':8,'alignment':TA_CENTER}),
                                                           ObjectValue(attribute_name="monto", left=15*cm,width=4*cm,\
                                                                       style={'fontName':'Helvetica','fontSize':8,'alignment':TA_RIGHT})
                                                           ]),
                          band_footer=ReportBand(elements=[Label(text="TOTAL", top=0.5*cm, left=12*cm, width=5*cm,\
                                                                 style={'fontName':'Helvetica','fontSize':9,'alignment':TA_CENTER},\
                                                                 borders = {'top': 1}),
                                                           ObjectValue(attribute_name="monto",\
                                                                       left=15*cm,width=4*cm, style={'fontName':'Helvetica','fontSize':8,'alignment':TA_RIGHT},\
                                                                       action=FIELD_ACTION_SUM, top=0.5*cm,\
                                                                       borders = {'top': 1})
                                                           ]),
                          )]
    
    