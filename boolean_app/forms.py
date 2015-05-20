# -*- coding: utf-8 -*-
'''
Created on 01/08/2014

@author: jorge
'''
from django.forms.models import ModelForm
from boolean_app.models import Venta, Detalle_venta, Periodo, Recibo, Valores, DetalleArticuloCompuesto,\
    Proveedor, Compra, Detalle_compra, OrdenPago, Bancos, Cuentas_banco, Proveedor,\
    Cliente
from django import forms
from django.forms.forms import Form

class FacturaForm(ModelForm):
    class Meta:
        model = Venta
        exclude = ('articulos','periodo')
        widgets = {
                   'comprobantes_relacionados': forms.SelectMultiple(attrs={'data-placeholder':"Elija uno o mas comprobantes"}),
                   'fecha':forms.DateInput(attrs={'data-bv-notempty':'true',\
                                                  'data-bv-notempty-message':'Debe ingresar la fecha del comprobante',\
                                                  'data-bv-date':'true',\
                                                  'data-bv-date-message':'Formato incorrecto, DD/MM/AAAA',\
                                                  'data-bv-date-format':'DD/MM/YYYY'}),
                   'tipo':forms.Select(attrs={'data-bv-notempty':'true',\
                                              'data-bv-notempty-message':'Debe seleccionar un tipo de comprobante'}),
                   'cliente':forms.Select(attrs={'data-bv-notempty':'true',\
                                                 'data-bv-notempty-message':'Debe seleccionar un cliente',\
                                                 'data-bv-excluded':'false'}),
                   'condicion_venta':forms.Select(attrs={'data-bv-notempty':'true',\
                                                         'data-bv-notempty-message':'Debe seleccionar una condición de venta'})
                   }

        
class DetalleVentaForm(ModelForm):
    class Meta:
        model = Detalle_venta
        exclude = ('venta',)
        widgets = {
                   #'articulo': forms.Select(attrs={'class':'articulo_select'}),
                   'articulo': forms.HiddenInput(attrs={'class':'articulo_input',\
                                                        'data-bv-excluded':'false',\
                                                        'data-bv-group':'td',\
                                                        'data-bv-selector':'.articulo_input',\
                                                        'data-bv-callback':'true',\
                                                        'data-bv-callback-callback':'checkArtAlmacenado',\
                                                        'data-bv-callback-message':'Debe seleccionar un articulo almacenado'}),
                   'tipo_articulo': forms.Select(attrs={'class':'tipo_articulo_select'}),
                   'precio_unitario': forms.TextInput(attrs={'class':'precio_unitario_input',\
                                                             'data-bv-group':'td',\
                                                             'data-bv-selector':'.precio_unitario_input',\
                                                             'data-bv-notempty':'true',\
                                                             'data-bv-notempty-message':'Debe ingresar el precio unitario',\
                                                             'data-bv-numeric':'true',\
                                                             'data-bv-numeric-message':'Ingrese solamente números'}),
                   'linea_articulo_personalizado': forms.Select(attrs={'class':'linea_articulo_personalizado_select',\
                                                                       'data-bv-group':'td',\
                                                                       'data-bv-selector':'.linea_articulo_personalizado_select',\
                                                                       'data-bv-notempty':'true',\
                                                                       'data-bv-notempty-message':'Debe seleccionar la linea del articulo personalizado'}),
                   'cantidad': forms.TextInput(attrs={'class':'cantidad_input',\
                                                      'data-bv-group':'td',\
                                                      'data-bv-selector':'.cantidad_input',\
                                                      'data-bv-notempty':'true',\
                                                      'data-bv-notempty-message':'Debe ingresar la cantidad',\
                                                      'data-bv-numeric':'true',\
                                                      'data-bv-numeric-message':'Ingrese solamente números'}),
                   'descuento': forms.TextInput(attrs={'class':'descuento_input',\
                                                       'data-bv-group':'td',\
                                                       'data-bv-selector':'.descuento_input',\
                                                       'data-bv-notempty':'true',\
                                                       'data-bv-notempty-message':'Debe ingresar el descuento',\
                                                       'data-bv-numeric':'true',\
                                                       'data-bv-numeric-message':'Ingrese solamente números'}),
                   'articulo_personalizado': forms.Textarea(attrs={'class':'articulo_personalizado_input','rows':5, 'cols':20,\
                                                                   'data-bv-group':'td',\
                                                                   'data-bv-selector':'.articulo_personalizado_input',\
                                                                   'data-bv-notempty':'true',\
                                                                   'data-bv-notempty-message':'Debe ingresar la descripcion del articulo personalizado'})
        }
        
class DetalleArticulosCompuestosForm(ModelForm):
    id_detalle_venta = forms.CharField(widget=forms.HiddenInput({'class':'id_detalle_venta_hidden'}))
    
    class Meta:
        model = DetalleArticuloCompuesto
        exclude = ('detalle_venta','descuento')
        widgets = {'pers': forms.CheckboxInput(attrs={'class':'pers_checkbox'}),                   
                   'articulo': forms.HiddenInput(attrs={'class':'articulo_input'}),
                   'precio_unitario': forms.TextInput(attrs={'class':'precio_unitario_input'}),
                   'linea_articulo_personalizado': forms.Select(attrs={'class':'linea_articulo_personalizado_select'}),
                   'cantidad': forms.TextInput(attrs={'class':'cantidad_input'}),
                   'articulo_personalizado': forms.Textarea(attrs={'class':'articulo_personalizado_input','rows':5, 'cols':20})
                   }
        
class SubdiarioIVAVentPeriodoFecha(Form):
    folio_inicial = forms.IntegerField(min_value=1, initial=1)
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.all(), required=False)
    fecha_desde = forms.DateField(required=False)
    fecha_hasta = forms.DateField(required=False)
    
    def clean(self):
        cleaned_data = super(SubdiarioIVAPeriodoFecha, self).clean()
        periodo = cleaned_data.get("periodo")
        fd = cleaned_data.get("fecha_desde")
        fh = cleaned_data.get("fecha_hasta")
        
        if fd and fh:
            if periodo:
                raise forms.ValidationError("Debe seleccionar o un periodo o las fechas desde y hasta. No ambas condiciones.")
        elif periodo:
            if fd or fh:
                raise forms.ValidationError("Debe seleccionar o un periodo o las fechas desde y hasta. No ambas condiciones.")
        elif not fd and not fh and not periodo:
            raise forms.ValidationError("Debe seleccionar un periodo o las fechas desde y hasta.")
        
        return cleaned_data
        
class ReciboForm(ModelForm):
    que_hago_con_diferencia = forms.ChoiceField(widget=forms.RadioSelect(),choices=(('credito','Dejar a crédito'),('vuelto','Dar vuelto')),initial='credito')
    class Meta:
        model = Recibo
        exclude = ('venta', 'credito_anterior', 'a_cuenta')
        widgets = {
                   'cliente': forms.Select(attrs={'data-placeholder':'Elija un cliente...'}),
                   }

class ReciboContadoForm(ModelForm):
    que_hago_con_diferencia = forms.ChoiceField(widget=forms.RadioSelect(),choices=(('credito','Dejar a crédito'),('vuelto','Dar vuelto')),initial='credito')
    #_lcliente = forms.IntegerField(widget=forms.HiddenInput())
    class Meta:
        model = Recibo
        exclude = ('venta','credito_anterior', 'a_cuenta')
        widgets = {
                   'cliente': forms.Select(attrs={'disabled':'disabled'}),
                   }
        
class DetalleCobroForm(Form):
    pagar = forms.DecimalField(widget=forms.TextInput(attrs={'class':'entrega_input',\
                                                             'data-bv-notempty-message':'Debe ingresar el importe a cancelar, si no desea cancelar ingrese 0',\
                                                             'data-bv-notempty':'true',\
                                                             'data-bv-group':'td',\
                                                             'data-bv-selector':'.entrega_input',\
                                                             'data-bv-numeric':'true',\
                                                             'data-bv-numeric-message':'Ingrese solo números'}))
    id_factura = forms.CharField(widget=forms.HiddenInput(attrs={'class':'id_factura'}))
    
class DetalleCobroContadoForm(Form):
    id_factura = forms.CharField(widget=forms.HiddenInput(attrs={'class':'id_factura'}))
    
class ValoresForm(ModelForm):
    class Meta:
        model = Valores
        exclude = ('recibo','pendiente_para_recibo')
        widgets = {
                   'tipo': forms.Select(attrs={'class':'tipo_valor_select'}),
                   'cheque_numero': forms.TextInput(attrs={'class':'cheque_numero_input',\
                                                           'data-bv-notempty-message':'Debe ingresar el número del cheque',\
                                                           'data-bv-notempty':'true',\
                                                           'data-bv-group':'.seccion_cheque',\
                                                           'data-bv-selector':'.cheque_numero_input',\
                                                           'data-bv-integer':'true',\
                                                           'data-bv-integer-message':'Ingrese solo números',\
                                                           'maxlength':'12'}),
                   'cheque_banco': forms.Select(attrs={'class':'cheque_banco_select',\
                                                       'data-bv-notempty-message':'Debe ingresar el banco',\
                                                       'data-bv-notempty':'true',\
                                                       'data-bv-group':'.seccion_cheque',\
                                                       'data-bv-selector':'.cheque_banco_select'}),
                   'cheque_fecha': forms.TextInput(attrs={'class':'cheque_fecha_input',\
                                                          'data-bv-notempty-message':'Debe ingresar la fecha de emisión del cheque',\
                                                          'data-bv-notempty':'true',\
                                                          'data-bv-group':'.seccion_cheque',\
                                                          'data-bv-selector':'.cheque_fecha_input',\
                                                          'data-bv-date':'true',\
                                                          'data-bv-date-message':'Debe ingresar una fecha válida, dd/mm/aaaa',\
                                                          'data-bv-date-format':'DD/MM/YYYY'}),
                   'cheque_cobro': forms.TextInput(attrs={'class':'cheque_cobro_input',\
                                                          'data-bv-notempty-message':'Debe ingresar la fecha de cobro del cheque',\
                                                          'data-bv-notempty':'true',\
                                                          'data-bv-group':'.seccion_cheque',\
                                                          'data-bv-selector':'.cheque_cobro_input',\
                                                          'data-bv-date':'true',\
                                                          'data-bv-date-message':'Debe ingresar una fecha válida, dd/mm/aaaa',\
                                                          'data-bv-date-format':'DD/MM/YYYY'}),
                   'cheque_titular': forms.TextInput(attrs={'class':'cheque_titular_input',\
                                                            'data-bv-notempty-message':'Debe ingresar el titular del cheque',\
                                                            'data-bv-notempty':'true',\
                                                            'data-bv-group':'.seccion_cheque',\
                                                            'data-bv-selector':'.cheque_titular_input'}),
                   'cheque_cuit_titular': forms.TextInput(attrs={'class':'cheque_cuit_titular_input',
                                                                 'data-bv-notempty-message':'Debe ingresar el CUIT del titular del cheque',\
                                                                 'data-bv-notempty':'true',\
                                                                 'data-bv-group':'.seccion_cheque',\
                                                                 'data-bv-selector':'.cheque_cuit_titular_input'}),
                   'cheque_paguese_a': forms.TextInput(attrs={'class':'cheque_paguese_a_input',\
                                                              'data-bv-notempty-message':'Debe ingresar a nombre de quien esta el cheque',\
                                                              'data-bv-notempty':'true',\
                                                              'data-bv-group':'.seccion_cheque',\
                                                              'data-bv-selector':'.cheque_paguese_a_input'}),
                   'cheque_domicilio_de_pago': forms.TextInput(attrs={'class':'cheque_domicilio_pago_input',
                                                                      'data-bv-notempty-message':'Debe ingresar el domicilio de pago del cheque',\
                                                                      'data-bv-notempty':'true',\
                                                                      'data-bv-group':'.seccion_cheque',\
                                                                      'data-bv-selector':'.cheque_domicilio_pago_input'}),
                   'transferencia_banco_origen':forms.Select(attrs={'class':'transferencia_banco_origen_select',\
                                                                    'data-bv-notempty-message':'Debe ingresar el banco de origen de la transferencia',\
                                                                    'data-bv-notempty':'true',\
                                                                    'data-bv-group':'.seccion_transferencia',\
                                                                    'data-bv-selector':'.transferencia_banco_origen_select'}),
                   'transferencia_cuenta_origen': forms.TextInput(attrs={'class':'transferencia_cuenta_origen',\
                                                                         'data-bv-notempty-message':'Debe ingresar la cuenta de origen de la transferencia',\
                                                                         'data-bv-notempty':'true',\
                                                                         'data-bv-group':'.seccion_transferencia',\
                                                                         'data-bv-selector':'.transferencia_cuenta_origen_select'}),
                   'transferencia_numero_operacion': forms.TextInput(attrs={'class':'transferencia_numero_operacion_input',\
                                                                            'data-bv-notempty-message':'Debe ingresar el número de operación',\
                                                                            'data-bv-notempty':'true',\
                                                                            'data-bv-group':'.seccion_transferencia',\
                                                                            'data-bv-selector':'.transferencia_numero_operacion_input'}),
                   'transferencia_cuenta_destino': forms.Select(attrs={'class':'transferencia_cuenta_destino_select',\
                                                                       'data-bv-notempty-message':'Debe ingresar la cuenta de destino de la transferencia',\
                                                                       'data-bv-notempty':'true',\
                                                                       'data-bv-group':'.seccion_transferencia',\
                                                                       'data-bv-selector':'.transferencia_cuenta_destino_select'}),
                   'monto': forms.TextInput(attrs={'class':'monto_input',\
                                                   'data-bv-notempty-message':'Debe ingresar el monto',\
                                                   'data-bv-notempty':'true',\
                                                   'data-bv-group':'.col-md-2',\
                                                   'data-bv-selector':'.monto_input'}),
                  }

class ValoresReciboForm(Form):
    TIPOS_CHOICES = (
                ("CHT","Cheque Tercero"),
                ("EFE","Efectivo"),
                ("TRB","Transferencia Bancaria"),
               )
    tipo=forms.ChoiceField(choices=TIPOS_CHOICES,widget=forms.Select(attrs={'class':'tipo_valor_select'}))
    cheque_numero = forms.CharField(widget=forms.TextInput(attrs={'class':'cheque_numero_input',\
                                                           'data-bv-notempty-message':'Debe ingresar el número del cheque',\
                                                           'data-bv-notempty':'true',\
                                                           'data-bv-group':'.seccion_cheque',\
                                                           'data-bv-selector':'.cheque_numero_input',\
                                                           'data-bv-integer':'true',\
                                                           'data-bv-integer-message':'Ingrese solo números',\
                                                           'maxlength':'12'}),
                                                           required=False)
    cheque_banco = forms.ModelChoiceField(queryset=Bancos.objects.all(),widget=forms.Select(attrs={'class':'cheque_banco_select',\
                                                       'data-bv-notempty-message':'Debe ingresar el banco',\
                                                       'data-bv-notempty':'true',\
                                                       'data-bv-group':'.seccion_cheque',\
                                                       'data-bv-selector':'.cheque_banco_select'}),
                                                       required=False)
    cheque_fecha = forms.DateField(widget=forms.TextInput(attrs={'class':'cheque_fecha_input',\
                                                          'data-bv-notempty-message':'Debe ingresar la fecha de emisión del cheque',\
                                                          'data-bv-notempty':'true',\
                                                          'data-bv-group':'.seccion_cheque',\
                                                          'data-bv-selector':'.cheque_fecha_input',\
                                                          'data-bv-date':'true',\
                                                          'data-bv-date-message':'Debe ingresar una fecha válida, dd/mm/aaaa',\
                                                          'data-bv-date-format':'DD/MM/YYYY'}),
                                                          required=False)
    cheque_cobro = forms.DateField(widget=forms.TextInput(attrs={'class':'cheque_cobro_input',\
                                                          'data-bv-notempty-message':'Debe ingresar la fecha de cobro del cheque',\
                                                          'data-bv-notempty':'true',\
                                                          'data-bv-group':'.seccion_cheque',\
                                                          'data-bv-selector':'.cheque_cobro_input',\
                                                          'data-bv-date':'true',\
                                                          'data-bv-date-message':'Debe ingresar una fecha válida, dd/mm/aaaa',\
                                                          'data-bv-date-format':'DD/MM/YYYY'}),
                                                          required=False)
    cheque_titular = forms.CharField(widget=forms.TextInput(attrs={'class':'cheque_titular_input',\
                                                            'data-bv-notempty-message':'Debe ingresar el titular del cheque',\
                                                            'data-bv-notempty':'true',\
                                                            'data-bv-group':'.seccion_cheque',\
                                                            'data-bv-selector':'.cheque_titular_input'}),
                                                            required=False)
    cheque_cuit_titular = forms.CharField(widget=forms.TextInput(attrs={'class':'cheque_cuit_titular_input',
                                                                 'data-bv-notempty-message':'Debe ingresar el CUIT del titular del cheque',\
                                                                 'data-bv-notempty':'true',\
                                                                 'data-bv-group':'.seccion_cheque',\
                                                                 'data-bv-selector':'.cheque_cuit_titular_input'}),
                                                                 required=False)
    cheque_paguese_a = forms.CharField(widget=forms.TextInput(attrs={'class':'cheque_paguese_a_input',\
                                                              'data-bv-notempty-message':'Debe ingresar a nombre de quien esta el cheque',\
                                                              'data-bv-notempty':'true',\
                                                              'data-bv-group':'.seccion_cheque',\
                                                              'data-bv-selector':'.cheque_paguese_a_input'}),
                                                              required=False)
    cheque_domicilio_de_pago = forms.CharField(widget=forms.TextInput(attrs={'class':'cheque_domicilio_pago_input',
                                                                      'data-bv-notempty-message':'Debe ingresar el domicilio de pago del cheque',\
                                                                      'data-bv-notempty':'true',\
                                                                      'data-bv-group':'.seccion_cheque',\
                                                                      'data-bv-selector':'.cheque_domicilio_pago_input'}),
                                                                      required=False)
    transferencia_banco_origen = forms.ModelChoiceField(queryset=Bancos.objects.all(), widget=forms.Select(attrs={'class':'transferencia_banco_origen_select',\
                                                                    'data-bv-notempty-message':'Debe ingresar el banco de origen de la transferencia',\
                                                                    'data-bv-notempty':'true',\
                                                                    'data-bv-group':'.seccion_transferencia',\
                                                                    'data-bv-selector':'.transferencia_banco_origen_select'}),
                                                                    required=False)
    transferencia_cuenta_origen = forms.CharField(widget=forms.TextInput(attrs={'class':'transferencia_cuenta_origen',\
                                                                                'data-bv-notempty-message':'Debe ingresar la cuenta de origen de la transferencia',\
                                                                                'data-bv-notempty':'true',\
                                                                                'data-bv-group':'.seccion_transferencia',\
                                                                                'data-bv-selector':'.transferencia_cuenta_origen_select'}),
                                                                                required=False)
    transferencia_numero_operacion = forms.CharField(widget=forms.TextInput(attrs={'class':'transferencia_numero_operacion_input',\
                                                                            'data-bv-notempty-message':'Debe ingresar el número de operación',\
                                                                            'data-bv-notempty':'true',\
                                                                            'data-bv-group':'.seccion_transferencia',\
                                                                            'data-bv-selector':'.transferencia_numero_operacion_input'}),
                                                                            required=False)
    transferencia_cuenta_destino = forms.ModelChoiceField(queryset=Cuentas_banco.objects.all(),widget=forms.Select(attrs={'class':'transferencia_cuenta_destino_select',\
                                                                       'data-bv-notempty-message':'Debe ingresar la cuenta de destino de la transferencia',\
                                                                       'data-bv-notempty':'true',\
                                                                       'data-bv-group':'.seccion_transferencia',\
                                                                       'data-bv-selector':'.transferencia_cuenta_destino_select'}),
                                                                       required=False)
    monto = forms.DecimalField(widget=forms.TextInput(attrs={'class':'monto_input',\
                                                             'data-bv-notempty-message':'Debe ingresar el monto',\
                                                             'data-bv-notempty':'true',\
                                                             'data-bv-group':'.col-md-2',\
                                                             'data-bv-selector':'.monto_input',\
                                                             'data-bv-greaterthan':'true',\
                                                             'data-bv-greaterthan-message':'Ingrese solo numeros positivos, en caso de exceder el sistema calcula el vuelto',\
                                                             'data-bv-greaterthan-inclusive':'false',\
                                                             'data-bv-greaterthan-value':'0'}))
class ActualizarPrecioRubrosForm(Form):
    rubro = forms.IntegerField(widget=forms.HiddenInput())
    porcentaje = forms.DecimalField()
    
class VentasTotalesForm(Form):
    fecha_desde = forms.DateField()
    fecha_hasta = forms.DateField()
    
class ResumenCuentaForm(Form):
    LISTAR_CHOICES=[('UNO','Listar un cliente'),
                    ('TODOS','Listar todos los clientes')]
    
    listar=forms.ChoiceField(choices=LISTAR_CHOICES, widget=forms.RadioSelect())
    cliente=forms.ModelChoiceField(queryset=Cliente.objects.all(),required=False)
    desde=forms.DateField()
    hasta=forms.DateField()

class ProveedoresResumenCuentaForm(Form):
    LISTAR_CHOICES=[('UNO','Listar un proveedor'),
                    ('TODOS','Listar todos los proveedores')]
    
    listar=forms.ChoiceField(choices=LISTAR_CHOICES, widget=forms.RadioSelect())
    proveedor=forms.ModelChoiceField(queryset=Proveedor.objects.all(),required=False)
    desde=forms.DateField()
    hasta=forms.DateField()
    
    
class ComposicionSaldoForm(Form):
    LISTAR_CHOICES=[('UNO','Listar un cliente'),
                    ('TODOS','Listar todos los clientes')]
    TIPO_CHOICES=[('SIMPLE','Simple'),
                  ('DETALLADO','Detallado')]
    
    listar=forms.ChoiceField(choices=LISTAR_CHOICES, widget=forms.RadioSelect())
    tipo=forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.RadioSelect())
    cliente=forms.ModelChoiceField(queryset=Cliente.objects.all(),required=False)
    
class ProveedoresComposicionSaldoForm(Form):
    LISTAR_CHOICES=[('UNO','Listar un proveedor'),
                    ('TODOS','Listar todos los proveedores')]
    TIPO_CHOICES=[('SIMPLE','Simple'),
                  ('DETALLADO','Detallado')]
    
    listar=forms.ChoiceField(choices=LISTAR_CHOICES, widget=forms.RadioSelect())
    tipo=forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.RadioSelect())
    proveedor=forms.ModelChoiceField(queryset=Proveedor.objects.all(),required=False)
    
class ComprobanteCompraForm(ModelForm):
    class Meta:
        model = Compra
        exclude = ('saldo')
        widgets = {'tipo':forms.Select(attrs={'class':'form-control',\
                                              'data-bv-notempty':'true',\
                                              'data-bv-notempty-message':'Debe seleccionar un tipo de comprobante',\
                                              'data-bv-group':'.col-md-2'}),
                   'fecha':forms.DateInput(attrs={'class':'form-control',\
                                                  'data-bv-notempty':'true',\
                                                  'data-bv-notempty-message':'Debe ingresar la fecha del comprobante',\
                                                  'data-bv-date':'true',\
                                                  'data-bv-date-message':'Formato incorrecto, DD/MM/AAAA',\
                                                  'data-bv-date-format':'DD/MM/YYYY',\
                                                  'data-bv-group':'.col-md-2'}),
                   'punto_venta':forms.TextInput(attrs={'class':'form-control',\
                                                        'required':'required',\
                                                        'data-bv-notempty-message':'Debe ingresar el numero del comprobante',\
                                                        'maxlength':'4'}),
                   'numero':forms.TextInput(attrs={'class':'form-control',\
                                                   'required':'required',\
                                                   'data-bv-notempty-message':'Debe ingresar el numero del comprobante',\
                                                   'maxlength':'8'}),
                   'condicion_compra':forms.Select(attrs={'class':'form-control',\
                                                   'data-bv-notempty':'true',\
                                                   'data-bv-notempty-message':'Debe seleccionar una condicion compra',\
                                                   'data-bv-excluded':'false'}),
                   'periodo':forms.Select(attrs={'class':'form-control',\
                                                 'data-bv-notempty':'true',\
                                                 'data-bv-notempty-message':'Debe seleccionar un período'}),
                   'proveedor':forms.Select(attrs={'class':'form-control',\
                                                   'data-bv-notempty':'true',\
                                                   'data-bv-notempty-message':'Debe seleccionar un cliente',\
                                                   'data-bv-excluded':'false'}),
                   'exento':forms.TextInput(attrs={'class':'form-control'}),
                   'ingresos_brutos':forms.TextInput(attrs={'class':'form-control'}),
                   'percepcion_iva':forms.TextInput(attrs={'class':'form-control'}),
                   'impuesto_interno':forms.TextInput(attrs={'class':'form-control'}),
                   'redondeo':forms.TextInput(attrs={'class':'form-control'}),
                    }
class DetalleCompraForm(ModelForm):
    class Meta:
        model=Detalle_compra
        exclude=('compra')
        widgets = {'cantidad':forms.TextInput(attrs={'class':'form-control cantidad_input',\
                                                     'required':'required',\
                                                     'data-bv-notempty-message':'Debe ingresar la cantidad',\
                                                     'data-bv-numeric':'true',\
                                                     'data-bv-numeric-message':'Ingrese solo numeros',\
                                                     'data-bv-group':'td',\
                                                     'data-bv-selector':'.cantidad_input'}),
                   'detalle':forms.Textarea(attrs={'class':'form-control detalle_textarea','cols':28,'rows':2,\
                                                   'required':'required',\
                                                   'data-bv-notempty-message':'Debe ingresar el detalle del item',\
                                                   'data-bv-group':'td',\
                                                   'data-bv-selector':'.detalle_textarea'}),
                   'precio_unitario':forms.TextInput(attrs={'class':'form-control precio_unitario_input',\
                                                            'required':'required',\
                                                            'data-bv-notempty-message':'Debe ingresar el precio unitario del item',\
                                                            'data-bv-numeric':'true',\
                                                            'data-bv-numeric-message':'Ingrese solo numeros',\
                                                            'data-bv-group':'td',\
                                                            'data-bv-selector':'.precio_unitario_input'}),
                   'iva':forms.Select(attrs={'class':'form-control iva_select',\
                                             'data-bv-excluded':'false',\
                                             'required':'required',\
                                             'data-bv-notempty-message':'Debe ingresar la alicuota de IVA del item',\
                                             'data-bv-group':'td',\
                                             'data-bv-selector':'.iva_select'}),
                   'iva_valor':forms.TextInput(attrs={'class':'form-control iva_valor_input',\
                                                      'required':'required',\
                                                      'data-bv-notempty-message':'Debe ingresar el valor de IVA del item',\
                                                      'data-bv-group':'td',\
                                                      'data-bv-selector':'.iva_valor_input'}),
                   }
        
class SubdiarioIVAPeriodoFecha(Form):
    folio_inicial = forms.IntegerField(min_value=1, initial=1, widget=forms.TextInput(attrs={'class':'form-control',\
                                                                                             'required':'required',\
                                                                                             'data-bv-integer':'true',\
                                                                                             'data-bv-integer-message':'Debe ingresar un número entero'}))
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.all(), required=False, widget=forms.Select(attrs={'class':'form-control'}))
    fecha_desde = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    fecha_hasta = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    
    def clean(self):
        cleaned_data = super(SubdiarioIVAPeriodoFecha, self).clean()
        periodo = cleaned_data.get("periodo")
        fd = cleaned_data.get("fecha_desde")
        fh = cleaned_data.get("fecha_hasta")
        
        if fd and fh:
            if periodo:
                raise forms.ValidationError("Debe seleccionar o un periodo o las fechas desde y hasta. No ambas condiciones.")
        elif periodo:
            if fd or fh:
                raise forms.ValidationError("Debe seleccionar o un periodo o las fechas desde y hasta. No ambas condiciones.")
        elif not fd and not fh and not periodo:
            raise forms.ValidationError("Debe seleccionar un periodo o las fechas desde y hasta.")
        
        return cleaned_data
    
class OrdenPagoForm(ModelForm):
    que_hago_con_diferencia = forms.ChoiceField(widget=forms.RadioSelect(),choices=(('credito','CREDITO'),('vuelto','VUELTO')),initial='credito')
    class Meta:
        model = OrdenPago
        exclude = ('compra','credito_anterior')
        widgets = {
                   'proveedor': forms.Select(attrs={'required':'true',\
                                                    'data-bv-notempty-message':'Debe seleccionar el proveedor'}),
                   'fecha': forms.TextInput(attrs={'required':'true',\
                                                    'data-bv-notempty-message':'Debe ingresar la fecha'})
                   }
        
class OrdenPagoContadoForm(ModelForm):
    que_hago_con_diferencia = forms.ChoiceField(widget=forms.RadioSelect(),choices=(('credito','CREDITO'),('vuelto','VUELTO')),initial='credito')
    class Meta:
        model = OrdenPago
        exclude = ('compra','credito_anterior')
        widgets = {
                   'proveedor': forms.Select(attrs={'disabled':'disabled'}),
                   'fecha': forms.TextInput(attrs={'readonly':'true'})
                   }
    
class DetallePagoForm(Form):
    pagar = forms.DecimalField(widget=forms.TextInput(attrs={'class':'pago_input'}))
    id_factura_compra = forms.CharField(widget=forms.HiddenInput(attrs={'class':'id_factura_compra_hidden'}))

class DetallePagoContadoForm(Form):
    id_factura_compra = forms.CharField(widget=forms.HiddenInput(attrs={'class':'id_factura_compra_hidden'}))
    
class ValoresOPForm(Form):
    TIPOS_CHOICES = (
                ("CHT","Cheque Tercero"),
                ("CHP","Cheque Propio"),
                ("EFE","Efectivo"),
                ("TRB","Transferencia Bancaria"),
               )
    id_cheque_tercero = forms.IntegerField(widget=forms.HiddenInput(attrs={'class':'id_cheque_tercero_hidden'}),required=False)
    tipo=forms.ChoiceField(choices=TIPOS_CHOICES,widget=forms.Select(attrs={'class':'tipo_valor_select'}))
    cheque_numero = forms.CharField(widget=forms.TextInput(attrs={'class':'cheque_numero_input',\
                                                           'data-bv-notempty-message':'Debe ingresar el número del cheque',\
                                                           'data-bv-notempty':'true',\
                                                           'data-bv-group':'.seccion_cheque',\
                                                           'data-bv-selector':'.cheque_numero_input',\
                                                           'data-bv-integer':'true',\
                                                           'data-bv-integer-message':'Ingrese solo números',\
                                                           'maxlength':'12'}),
                                                           required=False)
    cheque_fecha = forms.DateField(widget=forms.TextInput(attrs={'class':'cheque_fecha_input',\
                                                          'data-bv-notempty-message':'Debe ingresar la fecha de emisión del cheque',\
                                                          'data-bv-notempty':'true',\
                                                          'data-bv-group':'.seccion_cheque',\
                                                          'data-bv-selector':'.cheque_fecha_input',\
                                                          'data-bv-date':'true',\
                                                          'data-bv-date-message':'Debe ingresar una fecha válida, dd/mm/aaaa',\
                                                          'data-bv-date-format':'DD/MM/YYYY'}),
                                                          required=False)
    cheque_cobro = forms.DateField(widget=forms.TextInput(attrs={'class':'cheque_cobro_input',\
                                                          'data-bv-notempty-message':'Debe ingresar la fecha de cobro del cheque',\
                                                          'data-bv-notempty':'true',\
                                                          'data-bv-group':'.seccion_cheque',\
                                                          'data-bv-selector':'.cheque_cobro_input',\
                                                          'data-bv-date':'true',\
                                                          'data-bv-date-message':'Debe ingresar una fecha válida, dd/mm/aaaa',\
                                                          'data-bv-date-format':'DD/MM/YYYY'}),
                                                          required=False)
    cheque_paguese_a = forms.CharField(widget=forms.TextInput(attrs={'class':'cheque_paguese_a_input',\
                                                              'data-bv-notempty-message':'Debe ingresar a nombre de quien esta el cheque',\
                                                              'data-bv-notempty':'true',\
                                                              'data-bv-group':'.seccion_cheque',\
                                                              'data-bv-selector':'.cheque_paguese_a_input'}),
                                                              required=False)
    transferencia_cuenta_origen = forms.ModelChoiceField(queryset=Cuentas_banco.objects.all(),widget=forms.Select(attrs={'class':'transferencia_cuenta_origen_select',\
                                                                       'data-bv-notempty-message':'Debe ingresar la cuenta de origen de la transferencia',\
                                                                       'data-bv-notempty':'true',\
                                                                       'data-bv-group':'.seccion_transferencia',\
                                                                       'data-bv-selector':'.transferencia_cuenta_origen_select'}),
                                                                       required=False)
    transferencia_cuenta_destino = forms.CharField(widget=forms.TextInput(attrs={'class':'transferencia_cuenta_destino',\
                                                                                'data-bv-notempty-message':'Debe ingresar la cuenta de destino de la transferencia',\
                                                                                'data-bv-notempty':'true',\
                                                                                'data-bv-group':'.seccion_transferencia',\
                                                                                'data-bv-selector':'.transferencia_cuenta_destino_select'}),
                                                                                required=False)
    transferencia_numero_operacion = forms.CharField(widget=forms.TextInput(attrs={'class':'transferencia_numero_operacion_input',\
                                                                            'data-bv-notempty-message':'Debe ingresar el número de operación',\
                                                                            'data-bv-notempty':'true',\
                                                                            'data-bv-group':'.seccion_transferencia',\
                                                                            'data-bv-selector':'.transferencia_numero_operacion_input'}),
                                                                            required=False)    
    monto = forms.DecimalField(widget=forms.TextInput(attrs={'class':'monto_input',\
                                                             'data-bv-notempty-message':'Debe ingresar el monto',\
                                                             'data-bv-notempty':'true',\
                                                             'data-bv-group':'.col-md-2',\
                                                             'data-bv-selector':'.monto_input',\
                                                             'data-bv-greaterthan':'true',\
                                                             'data-bv-greaterthan-message':'Ingrese solo numeros positivos, en caso de exceder el sistema calcula el vuelto',\
                                                             'data-bv-greaterthan-inclusive':'false',\
                                                             'data-bv-greaterthan-value':'0'}))
