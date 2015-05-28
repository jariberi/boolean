# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from decimal import Decimal
from django.db.models import Q
from django.db.models.aggregates import Sum
from pdb import set_trace
from django.utils.timezone import now
from boolean.settings import CUIT

class Periodo(models.Model):
    mes = models.IntegerField()
    ano = models.IntegerField()
    
    def __unicode__(self):
        return "%s/%s" %(self.mes, self.ano)
    
    def periodo_full(self):
        mes=str(self.mes)
        if(0<len(mes)<3):
            restante = 2 - len(mes)
            if(restante!=0):
                for i in range(restante):
                    mes = '0' + mes
        return "%s/%s" %(mes, self.ano)
        

class Bancos(models.Model):
    nombre = models.CharField(max_length=50, help_text="Nombre del banco")
    
    def __unicode__(self):
        return self.nombre
    
class Cuentas_banco(models.Model):
    cbu = models.CharField(max_length=22)
    banco = models.ForeignKey(Bancos)
    
    def __unicode__(self):
        return "CBU: %s en banco %s" %(self.cbu, self.banco.nombre)
        
class Rubro(models.Model):
    IVA_CHOICES = (
                   ("IVA21","IVA 21%"),
                   ("IV105","IVA 10.5%"),
                  )
    
    cod = models.IntegerField()
    nombre = models.CharField(max_length=50, help_text="Nombre del rubro")
    iva = models.CharField(max_length=5, choices=IVA_CHOICES)
    
    def __unicode__(self):
        return self.nombre
    
class SubRubro(models.Model):
    IVA_CHOICES = (
                   ("IVA21","IVA 21%"),
                   ("IV105","IVA 10.5%"),
                  )
    
    rubro = models.ForeignKey(Rubro)
    nombre = models.CharField(max_length=50, help_text="Nombre del subrubro")
    iva = models.CharField(max_length=5, choices=IVA_CHOICES)
    
    def __unicode__(self):
        return "%s (%s)" %(self.nombre, self.rubro.nombre)
    
class Linea(models.Model):
    nombre = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.nombre    

class Condicion_venta(models.Model):
    descripcion = models.CharField(max_length=50, help_text="Descripcion")
    
    def __unicode__(self):
        return self.descripcion
    
class Condicion_compra(models.Model):
    descripcion = models.CharField(max_length=50, help_text="Descripcion")
    
    def __unicode__(self):
        return self.descripcion

class Transporte(models.Model):
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50, blank=True)
    localidad = models.CharField(max_length=40, blank=True)
    codigo_postal = models.CharField(max_length=40, blank=True)
    provincia = models.CharField(max_length=40, blank=True)
    pais = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    fax = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    cuit = models.CharField(max_length=13, blank=True)
    codigo_iva = models.CharField(max_length=30, blank=True)
    codigo_ingresos_brutos = models.CharField(max_length=30, blank=True)
    #saldo_transporte = models.DecimalField(max_digits=13, decimal_places=3)
    notas = models.CharField(max_length=400, blank=True)
    #modificado_por = models.ForeignKey(User)
    
    def __unicode__(self):
        return self.nombre
                           
class Cliente(models.Model):
    PROVINCIA_CHOICES=(
                       ("BA","Buenos Aires"),
                       ("CT","Corrientes"),
                       ("CC","Chaco"),
                       ("CH","Chubut"),
                       ("CD","Córdoba"),
                       ("CR","Corrientes"),
                       ("ER","Entre Ríos"),
                       ("FO","Formosa"),
                       ("JY","Jujuy"),
                       ("LP","La Pampa"),
                       ("LR","La Rioja"),
                       ("MZ","Mendoza"),
                       ("MN","Misiones"),
                       ("NQ","Neuquén"),
                       ("RN","Río Negro"),
                       ("SA","Salta"),
                       ("SJ","San Juan"),
                       ("SL","San Luis"),
                       ("SC","Santa Cruz"),
                       ("SF","Santa Fe"),
                       ("SE","Santiago del Estero"),
                       ("TF","Tierra del Fuego, Antártida e Islas del Atlántico Sur"),
                       ("TM","Tucumán")
                       
                       )
    COND_IVA_CHOICES=(
                       ("RI","Responsable Inscripto"),
                       ("MO","Monotributo"),
                       ("CF","Consumidor Final"),
                       )
    razon_social = models.CharField(max_length=100, help_text="Razón social del cliente")
    direccion = models.CharField(max_length=100, help_text="Dirección del cliente", blank=True)
    localidad = models.CharField(max_length=100, help_text="Localidad de residencia del cliente", blank=True)
    codigo_postal = models.CharField(max_length=8, help_text="CP del cliente", blank=True)
    provincia = models.CharField(max_length=30, help_text="Provincia de residencia del cliente", choices=PROVINCIA_CHOICES, blank=True)
    telefono = models.CharField(max_length=60, help_text="Telefono de contacto del cliente", blank=True)
    fax = models.CharField(max_length=60, help_text="Fax del cliente", blank=True)
    email = models.EmailField(max_length=254, blank=True)
    cuit = models.CharField(max_length=13)
    codigo_iva = models.CharField(max_length=25, blank=True)
    cond_iva = models.CharField(max_length = 40, blank=True, choices=COND_IVA_CHOICES)
    codigo_ingresos_brutos = models.CharField(max_length=15, blank=True)
    transporte_preferido = models.ForeignKey(Transporte, help_text="Transporte preferido por el cliente", blank=True, null=True)
    ultima_compra = models.DateField(help_text="Fecha de última compra", editable=False, blank=True, null=True)
    ultimo_pago = models.DateField(help_text="Fecha último pago", editable=False, blank=True, null=True)
    saldo = models.DecimalField(max_digits=13, decimal_places=3, editable=False, default=0)
    notas = models.CharField(max_length=400, blank=True)
    modificado_por = models.ForeignKey(User, editable=False, blank=True)
    
    class Meta:
        ordering = ['razon_social']
    
    def __unicode__(self):
        return self.razon_social
    '''
    @return: Decimal - Saldo total a la fecha del cliente.
    '''
    def saldo_total(self):
        cli=Q(cliente=self)
        fact=Q(tipo__startswith="FA")
        nd=Q(tipo__startswith="ND")
        apr=Q(aprobado=True)
        factynd = Venta.objects.filter(cli, apr,  fact | nd).aggregate(total=Sum("total")) 
        nc=Q(tipo__startswith="NC")
        ncrs = Venta.objects.filter(cli, apr, nc).aggregate(total=Sum("total"))
        recibos = Detalle_cobro.objects.filter(recibo__cliente=self).aggregate(total=Sum("monto"))
        ret=0
        if factynd['total']:
            ret += factynd['total']
        if ncrs['total']:
            ret -= ncrs['total']
        if recibos['total']:
            ret -= recibos['total']
        return ret
    
    def saldo_anterior(self,fecha):
        cli=Q(cliente=self)
        fact=Q(tipo__startswith="FA")
        nd=Q(tipo__startswith="ND")
        apr=Q(aprobado=True)
        #fer=Q(recibo__fecha__lt=fecha)
        fef=Q(fecha__lt=fecha)
        factynd = Venta.objects.filter(cli, apr, fef, fact | nd).aggregate(total=Sum("total")) 
        nc=Q(tipo__startswith="NC")
        ncrs = Venta.objects.filter(cli, apr, fef, nc).aggregate(total=Sum("total"))
        recibos = Detalle_cobro.objects.filter(recibo__cliente=self, recibo__fecha__lte=fecha).aggregate(total=Sum("monto"))
        ret=0
        if factynd['total']:
            ret += factynd['total']
        if ncrs['total']:
            ret -= ncrs['total']
        if recibos['total']:
            ret -= recibos['total']
        return ret
    
    '''
    @param desde: Date con la fecha desde para los datos del resumen de cuenta
    @param hasta: Date con la fecha hasta para los datos del resumen de cuenta
    '''
    def resumen_cuenta(self, desde, hasta):
        ventas_totales = Venta.objects.filter(fecha__range=(desde, hasta), aprobado=True)

class Proveedor(models.Model):
    PROVINCIA_CHOICES=(
                       ("BA","Buenos Aires"),
                       ("CT","Corrientes"),
                       ("CC","Chaco"),
                       ("CP","Capital Federal"),
                       ("CH","Chubut"),
                       ("CD","Córdoba"),
                       ("CR","Corrientes"),
                       ("ER","Entre Ríos"),
                       ("FO","Formosa"),
                       ("JY","Jujuy"),
                       ("LP","La Pampa"),
                       ("LR","La Rioja"),
                       ("MZ","Mendoza"),
                       ("MN","Misiones"),
                       ("NQ","Neuquén"),
                       ("RN","Río Negro"),
                       ("SA","Salta"),
                       ("SJ","San Juan"),
                       ("SL","San Luis"),
                       ("SC","Santa Cruz"),
                       ("SF","Santa Fe"),
                       ("SE","Santiago del Estero"),
                       ("TF","Tierra del Fuego, Antártida e Islas del Atlántico Sur"),
                       ("TM","Tucumán")
                       
                       )
    COND_IVA_CHOICES=(
                       ("RI","Responsable Inscripto"),
                       ("RE","Responsable Exento"),
                       ("MO","Monotributo"),
                       )
    razon_social = models.CharField(max_length=150,help_text="Razón Social del proveedor")
    direccion = models.CharField(max_length=150,help_text="Dirección del proveedor", blank=True)
    localidad = models.CharField(max_length=80,help_text="Localidad del proveedor", blank=True)
    codigo_postal = models.CharField(max_length=8, blank=True)
    provincia = models.CharField(max_length=30, blank=True, choices=PROVINCIA_CHOICES)
    pais = models.CharField(max_length=30, blank=True, default="Argentina")
    telefono = models.CharField(max_length=30, blank=True)
    fax = models.CharField(max_length=30, help_text="Fax del proveedor", blank=True)
    email = models.EmailField(max_length=254, blank=True)
    cuit = models.CharField(max_length=13)
    condicion_iva= models.CharField(max_length=30, choices=COND_IVA_CHOICES, default="RI")
    codigo_ingresos_brutos = models.CharField(max_length=15, blank=True)
    contacto = models.CharField(max_length=50, blank=True)
    condicion_pago = models.CharField(max_length=60, blank=True)
    #saldo = models.DecimalField(max_digits=13, decimal_places=3, editable=False)
    notas = models.CharField(max_length=400, blank=True)
    modificado_por = models.ForeignKey(User, editable=False)
    
    def __unicode__(self):
        return self.razon_social
    
    def saldo_anterior(self,fecha):
        pro=Q(proveedor=self)
        fef=Q(fecha__lte=fecha)
        fact = Compra.objects.filter(pro, fef)
        ret=0
        for f in fact:
            ret +=f.total
        ops = Detalle_pago.objects.filter(orden_pago__proveedor=self, orden_pago__fecha__lte=fecha).aggregate(total=Sum("monto"))
        if ops['total']:
            ret -= ops['total']
        return ret
    
    def saldo_total(self):
        pro=Q(proveedor=self)
        fact = Compra.objects.filter(pro).aggregate(total=Sum("total")) 
        ops = Detalle_pago.objects.filter(orden_pago__proveedor=self).aggregate(total=Sum("monto"))
        ret=0
        if fact['total']:
            ret += fact['total']
        if ops['total']:
            ret -= ops['total']
        return ret

    
class Articulo(models.Model):
    UNIDADES_CHOICES = (
                        ("UN","Unidades"),
                        ("KG","Kilogramos"),
                        ("HS","Horas"),
                        ("MT","Metros"),
                        )
    
    codigo = models.CharField(max_length=60, blank=True)
    codigo_fabrica = models.CharField(max_length=70, blank=True)
    denominacion = models.CharField(max_length=200, help_text="Denominación del artículo")
    informacion_adicional = models.TextField(blank=True, help_text="Información adicional del artículo")
    rubro = models.ForeignKey(Rubro)
    proveedor_primario = models.ForeignKey(Proveedor, related_name="proveedor_primario", help_text="Proveedor primario de este artículo")
    proveedor_secundario = models.ForeignKey(Proveedor, related_name="proveedor_secundario", blank=True, null=True, help_text="Proveedor secundario de este artículo")
    unidad_medida = models.CharField(max_length=2, choices=UNIDADES_CHOICES, default="UN")
    costo_compra = models.DecimalField(max_digits=13, decimal_places=3)
    descuento_compra = models.DecimalField(max_digits=13, decimal_places=3)
    ganancia_venta = models.DecimalField(max_digits=13, decimal_places=3, help_text="Porcentaje de ganancia del artículo")
    #precio_venta = models.DecimalField(max_digits=13, decimal_places=3)
    ganancia_venta2 = models.DecimalField(max_digits=13, decimal_places=3, default=0, help_text="Porcentaje alternativo de ganancia del artículo. Opcional.")
    #precio_venta2 = models.DecimalField(max_digits=13, decimal_places=3)
    ganancia_venta3 = models.DecimalField(max_digits=13, decimal_places=3, default=0, help_text="Porcentaje alternativo de ganancia del artículo. Opcional.")
    #precio_venta3 = models.DecimalField(max_digits=13, decimal_places=3)
    linea = models.ForeignKey(Linea)
    fecha_ultima_compra= models.DateField(editable=False, blank=True, null=True)
    proveedor_ultima_compra = models.ForeignKey(Proveedor, related_name="ultimo_proveedor", editable=False, blank=True, null=True)
    ultima_actualizacion_precio = models.DateField(editable=False, blank=True, null=True)
    #modificado_por = models.ForeignKey(User, blank=True, editable=False)
    #habilitado = models.BooleanField(default=True)
    
    def __unicode__(self):
        return "%s - %s - %s" %(self.codigo, self.codigo_fabrica, self.denominacion)
    
    def _descuento_sobre_costo_compra(self):
        '''
        @return: Valor del descuento sobre el costo de compra
        @rtype: Decimal
        '''
        
        return self.costo_compra*self.descuento_compra/100
    
    def descuento_sobre_costo_compra(self):
        '''
        @return: Valor del descuento sobre el costo de compra
        @rtype: String
        '''
        
        return "%.2f" %self._descuento_sobre_costo_compra()
    
    def _costo_compra_real(self):
        '''
        @return: Costo de compra con descuento
        @rtype: Decimal
        '''
        
        return self.costo_compra-self._descuento_sobre_costo_compra()
    
    def costo_compra_real(self):
        '''
        @return: Costo de compra con descuento
        @rtype: String
        '''
        
        return "%.2f" %self._costo_compra_real()
    
    def _ganancia_real(self):
        '''
        @return: Valor de ganancia del articulo
        @rtype: Decimal
        '''
        
        return Decimal(1)+(self.ganancia_venta/Decimal(100))
    
    def ganancia_real(self):
        '''
        @return: Valor de ganancia del articulo
        @rtype: String
        '''
        
        return "%.2f" %self._ganancia_real()
        
    def _precio_venta(self):
        '''
        @return: Valor del precio de venta del articulo
        @rtype: Decimal
        '''
        pv = self._costo_compra_real()*self._ganancia_real()
        return pv
    
    @property
    def precio_venta(self):
        '''
        @return: Valor del precio de venta del articulo
        @rtype: String
        '''
        pv = self._costo_compra_real()*self._ganancia_real()
        return "%.2f" %pv
    
    def _iva_articulo(self):
        '''
        @return: Valor de IVA del articulo
        @rtype: Decimal
        '''
        return self._precio_venta()*Decimal(0.21)
    
    def iva_articulo(self):
        '''
        @return: Valor de IVA del articulo
        @rtype: String
        '''
        return "%.2f" %self._iva_articulo()
    
    
    def _precio_venta_iva_inc(self):
        '''
        @return: Valor precio del articulo iva incluido
        @rtype: Decimal
        '''
        pvii = self._precio_venta()+self._iva_articulo()
        return pvii
        
    @property
    def precio_venta_iva_inc(self):
        '''
        @return: Valor precio del articulo iva incluido
        @rtype: String
        '''
        return "%.2f" %self._precio_venta_iva_inc()
    
class Venta(models.Model):
    TIPOS_CHOICES = (
                     ("FAA","FAA"),
                     ("FAB","FAB"),
                     ("NCA","NCA"),
                     ("NCB","NCB"),
                     ("NDA","NDA"),
                     ("NDB","NDB"),
                    )
    fecha_hora = models.DateTimeField(default=datetime.now(),editable=False)
    tipo = models.CharField(max_length=3, choices=TIPOS_CHOICES)
    punto_venta = models.IntegerField(blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True)
    fecha = models.DateField(default=datetime.today())
    cliente = models.ForeignKey(Cliente)
    condicion_venta = models.ForeignKey(Condicion_venta)
    transporte = models.ForeignKey(Transporte, blank=True, null=True)
    #vendedor = models.ForeignKey(User)
    articulos = models.ManyToManyField(Articulo, through='Detalle_venta')
    #flete = models.DecimalField(max_digits=13, decimal_places=3, default=Decimal('0.000'))
    subtotal = models.DecimalField(max_digits=13, decimal_places=3, editable=False, blank=True, null=True)
    neto = models.DecimalField(max_digits=13, decimal_places=3, editable=False, blank=True, null=True)
    iva21 = models.DecimalField(max_digits=13, decimal_places=3, editable=False, blank=True, null=True)
    iva105 = models.DecimalField(max_digits=13, decimal_places=3, editable=False, blank=True, null=True)
    #iva27 = models.DecimalField(max_digits=13, decimal_places=3)
    total = models.DecimalField(max_digits=13, decimal_places=3, editable=False, blank=True, null=True)
    descuento = models.DecimalField(max_digits=13, decimal_places=3, default=Decimal('0.000'))
    aprobado = models.BooleanField(default=False, editable=False)
    periodo = models.ForeignKey(Periodo)
    cae = models.CharField(max_length=50, blank=True, null=True, editable=False)
    fvto_cae = models.DateField(blank=True, editable=False, null=True)
    #comprobantes_relacionados = models.ManyToManyField('self', blank=True, null=True, default=None, symmetrical=False, related_name="crs")
    pagado = models.BooleanField(editable=False, default=False)
    comprobante_relacionado = models.ForeignKey('self', blank=True, null=True, default=None)
    saldo = models.DecimalField(max_digits=13, decimal_places=3, editable=False, blank=True, null=True)
   
    
    def __unicode__(self):
        return "Comprobante %s, %s-%s --- Fecha: %s" %(self.tipo, self.pto_vta_full(), self.num_comp_full(), self.fecha_dd_mm_aaaa())
    
    def descuento_importe(self):
        return self.subtotal*self.descuento/Decimal(100)
    
    def comp_completo_informe(self):
        return "%s %s-%s" %(self.tipo, self.pto_vta_full(), self.num_comp_full())
    
    @property
    def pto_vta_num_full(self):
        return "%s - %s" %(self.pto_vta_full(), self.num_comp_full())
    
    def neto_2dec(self):
        return "%.2f" %self.neto
    
    def iva21_2dec(self):
        return "%.2f" %self.iva21
    
    @property
    def TOTAL(self):
        return round(self.total,2)
    def total_2dec(self):
        return "%.2f" %self.total
    
    def fecha_dd_mm_aaaa(self):
        return self.fecha.strftime('%d/%m/%Y')
    
    def vto_cae_dd_mm_aaaa(self):
        return self.fvto_cae.strftime('%d/%m/%Y')
    
    def pto_vta_full(self):
        ptovta=str(self.punto_venta)
        if(0<len(ptovta)<5):
            restante = 4 - len(ptovta)
            if(restante!=0):
                for i in range(restante):
                    ptovta = '0' + ptovta
        return ptovta
    
    def num_comp_full(self):
        num=str(self.numero)
        if(0<len(num)<9):
            restante = 8 - len(num)
            if(restante!=0):
                for i in range(restante):
                    num = '0' + num
        return num
    
    def saldo__deprecated(self):
        resto = self.total
        #Buscar entre las NC si hay alguna relacionada a este comprobante
        ncs = Venta.objects.filter(comprobante_relacionado=self)
        for nc in ncs:
            resto -= nc.total
        cobros = Detalle_cobro.objects.filter(venta=self.id)
        for cobro in cobros:
            resto -= cobro.monto
        #resto="3333"
        return resto
    '''
    @return: [String] Codigo segun tabla comprobantes AFIP
    '''
    @property
    def codigo_comprobante_segun_afip(self):
        if self.tipo=="FAA":
            return "001"
        elif self.tipo=="FAB":
            return "006"
        elif self.tipo=="NCA":
            return "003"
        elif self.tipo=="NCB":
            return "008"
        elif self.tipo=="NDA":
            return "005"
        elif self.tipo=="NDB":
            return "007"
    
    @property
    def codigo_moneda_segun_afip(self):
        #Devuelve $ (pesos argentinos)
        return 'PES'

class Detalle_venta(models.Model):
    TIPO_ARTICULO_CHOICES = (
                     ("AA","Art. almacenado"),
                     ("AP","Art. personalizado"),
                     ("AC","Art. compuesto"),
                    )
    
    venta = models.ForeignKey(Venta)
    #pers = models.BooleanField(default=False)
    tipo_articulo = models.CharField(max_length=2, choices=TIPO_ARTICULO_CHOICES, default='AA')
    articulo = models.ForeignKey(Articulo, blank=True, null=True)
    cantidad = models.DecimalField(max_digits=13, decimal_places=3)
    articulo_personalizado = models.TextField(max_length=60, blank=True)
    linea_articulo_personalizado = models.ForeignKey(Linea, blank=True, null=True)
    #neto = models.DecimalField(max_digits=13, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=13, decimal_places=3)
    descuento = models.DecimalField(max_digits=6, decimal_places=3)
    #comprobante_relacionado = models.ForeignKey(Venta, blank=True, null=True)
    aclaracion = models.TextField(blank=True)
    
    @property
    def total_con_descuento_factura(self):
        '''
        Devuelve el precio total del item incluyendo los descuentos del mismo item, y de su factura.
        '''
        desc=self.venta.descuento/100
        final=self.precio_unitario_con_descuento()-(self.precio_unitario_con_descuento()*desc)
        return self.cantidad*final
    
    @property
    def total_con_descuento(self):
        return self.cantidad*self.precio_unitario_con_descuento()
    
    @property
    def iva(self):
        return self.cantidad*self.precio_unitario_con_descuento()*Decimal("0.21")
    
    @property
    def iva_con_descuento_factura(self):
        return self.total_con_descuento_factura*Decimal("0.21")
    
    def get_articulo(self):
        if self.articulo:
            return self.articulo.denominacion
        else:
            return self.articulo_personalizado
    
    def get_cod(self):
        if self.articulo:
            return self.articulo.codigo
        else:
            return "0"
        
    def get_cod_fab(self):
        if self.articulo:
            return self.articulo.codigo_fabrica
        else:
            return ""
    
    def precio_unitario_con_descuento(self):
        return self.precio_unitario - (self.precio_unitario*self.descuento/Decimal(100))
    
    def neto(self):
        return self.precio_unitario_con_descuento() * self.cantidad
        
    def __unicode__(self):
        if self.articulo_personalizado:
            return "V: %s, Art P: %s, Cant: %s" %(self.venta, self.articulo_personalizado, self.cantidad)
        else:
            return "V: %s, A: %s, Cant: %s" %(self.venta, self.articulo, self.cantidad)
    
class Recibo(models.Model):
    fecha_hora = models.DateTimeField(default=datetime.now(),editable=False)
    fecha = models.DateField(default=datetime.today())
    numero = models.IntegerField(blank=True, null=True)
    cliente = models.ForeignKey(Cliente)
    venta = models.ManyToManyField(Venta, through='Detalle_cobro')
    credito_anterior = models.DecimalField(max_digits=13, decimal_places=3, default=0.000)
    a_cuenta = models.DecimalField(max_digits=13, decimal_places=3, default=0.000)
    
    def __unicode__(self):
        return "Recibo nro: %s -> %s" %(self.numero_full,self.cliente.razon_social)
    
    def get_a_credito(self):
        '''
        @return: Decimal o 0, dependiendo si hay credito.
        '''
        #total_comprobantes = self.detalle_cobro_set.all().aggregate(Sum('monto'))['monto__sum']
        #total_valores = self.dinero_set.all().aggregate(Sum('monto'))['monto__sum']
        #print (total_comprobantes,total_valores)
        return self.cliente.saldo or 0
        #return total_valores-total_comprobantes or 0
    
    def fecha_dd_mm_aaaa(self):
        return self.fecha.strftime('%d/%m/%Y')
    
    @property
    def numero_full(self):
        num=str(self.numero)
        if(0<len(num)<9):
            restante = 8 - len(num)
            if(restante!=0):
                for i in range(restante):
                    num = '0' + num
        return num
    
    @property
    def total(self):
        total=self.dinero_set.all().aggregate(Sum('monto'))['monto__sum']
        #detalles = Detalle_cobro.objects.filter(recibo__id=self.id)
        #total = 0
        #for det in detalles:
        #    total += det.monto
        #a_cuenta = Cobranza_a_cuenta.objects.filter(recibo__id=self.id)
        #if a_cuenta:
        ##    total += a_cuenta[0].monto
        ##cred_ant = Cobranza_credito_anterior.objects.filter(recibo__id=self.id)
        #if cred_ant:
        #    total -= cred_ant[0].monto
        return total
    
    @property
    def total_str(self):
        return "%.2f" %self.total

class DetalleArticuloCompuesto(models.Model):
    detalle_venta = models.ForeignKey(Detalle_venta)
    pers = models.BooleanField(default=False)
    cantidad = models.DecimalField(max_digits=13, decimal_places=3)
    articulo = models.ForeignKey(Articulo, null=True, blank=True)
    articulo_personalizado = models.TextField(max_length=100, null=True, blank=True)
    linea_articulo_personalizado = models.ForeignKey(Linea, null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=13, decimal_places=3)
    descuento = models.DecimalField(max_digits=13, decimal_places=3, default=0.000)
    
    @property
    def total_con_descuento_factura_e_item(self):
        '''
        Devuelve el precio total del articulo compuestos incluyendo los descuentos del item, y de su factura.
        '''
        #Hago el descuento de la factura
        descf=self.detalle_venta.venta.descuento/100
        valor=self.precio_unitario_con_descuento
        valor_con_desc_factura = valor-(valor*descf)
        #Hago el descuento del item
        desci=self.detalle_venta.descuento/100
        valor_con_desc_item = valor_con_desc_factura-(valor_con_desc_factura*desci)
        return self.cantidad*valor_con_desc_item
    
    @property
    def neto(self):
        return self.cantidad*self.precio_unitario_con_descuento
    
    @property
    def precio_unitario_con_descuento(self):
        return self.precio_unitario-(self.precio_unitario*self.descuento/Decimal("100"))
    
    @property
    def iva(self):
        return self.cantidad*self.precio_unitario*Decimal("0.21")
    
    def get_articulo(self):
        if self.articulo:
            return self.articulo.denominacion
        else:
            return self.articulo_personalizado
    
    def get_cod(self):
        if self.articulo:
            return self.articulo.codigo
        else:
            return "0"
        
    def get_cod_fab(self):
        if self.articulo:
            return self.articulo.codigo_fabrica
        else:
            return ""
        
    def __unicode__(self):
        if self.articulo_personalizado:
            return "DV: %s, Art P: %s, Cant: %s" %(self.detalle_venta, self.articulo_personalizado, self.cantidad)
        else:
            return "DV: %s, A: %s, Cant: %s" %(self.detalle_venta, self.articulo, self.cantidad)
    
        
class Detalle_cobro(models.Model):
    venta = models.ForeignKey(Venta)
    recibo = models.ForeignKey(Recibo)
    monto = models.DecimalField(max_digits=13, decimal_places=3)
    
    def __unicode__(self):
        return "%s, venta: %s, monto %.2f" %(self.recibo,self.venta, self.monto)
    
    def monto_2d(self):
        return "%.2f" %self.monto
        

    
    
class Cobranza_a_cuenta(models.Model):
    recibo = models.ForeignKey(Recibo)
    monto = models.DecimalField(max_digits=13, decimal_places=3)
    
class Cobranza_credito_anterior(models.Model):
    recibo = models.ForeignKey(Recibo)
    monto = models.DecimalField(max_digits=13, decimal_places=3)
    
class Compra(models.Model):
    TIPOS_CHOICES = (
                     ("FAA","FAA"),
                     ("FAB","FAB"),
                     ("FAC","FAC"),
                     ("NCA","NCA"),
                     ("NCB","NCB"),
                     ("NCC","NCC"),
                     ("NDA","NDA"),
                     ("NDB","NDB"),
                     ("NDC","NDC"),
                    )
    fecha_hora = models.DateTimeField(default=now(),editable=False)
    tipo = models.CharField(max_length=3, choices=TIPOS_CHOICES)
    punto_venta = models.IntegerField()
    numero = models.IntegerField()
    fecha = models.DateField(default=datetime.today())
    condicion_compra = models.ForeignKey(Condicion_compra)
    proveedor = models.ForeignKey(Proveedor)
    #flete = models.DecimalField(max_digits=13, decimal_places=3, default=Decimal('0.000'))
    neto = models.DecimalField(max_digits=12, decimal_places=2, editable=False, blank=True, null=True)
    iva21 = models.DecimalField(max_digits=12, decimal_places=2, editable=False, blank=True, null=True)
    iva105 = models.DecimalField(max_digits=12, decimal_places=2, editable=False, blank=True, null=True)
    iva27 = models.DecimalField(max_digits=12, decimal_places=2, editable=False, blank=True, null=True)
    percepcion_iva = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    exento = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ingresos_brutos = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    impuesto_interno = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    redondeo = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    #total = models.DecimalField(max_digits=12, decimal_places=2, editable=False, blank=True, null=True)
    periodo = models.ForeignKey(Periodo)
    #pagado = models.BooleanField(editable=False, default=False)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    
    def __unicode__(self):
        return "Comprobante %s con fecha %s" %(self.identificador_completo,self.fecha_dd_mm_aaaa)
    
    @property
    def pagado(self):
        print self.saldo
        return True if self.saldo == 0 else False
    
    @property
    def total(self):
        return self.neto+self.iva+self.percepcion_iva+self.exento+self.ingresos_brutos+self.impuesto_interno+self.redondeo
    
    @property
    def estado(self):
        return "Pagado" if self.pagado else "Pendiente"
    
    def pto_vta_formateado(self):
        ptovta=str(self.punto_venta)
        if(0<len(ptovta)<5):
            restante = 4 - len(ptovta)
            if(restante!=0):
                for i in range(restante):
                    ptovta = '0' + ptovta
        return ptovta
    
    def num_comp_formateado(self):
        num=str(self.numero)
        if(0<len(num)<9):
            restante = 8 - len(num)
            if(restante!=0):
                for i in range(restante):
                    num = '0' + num
        return num
    
    @property
    def identificador(self):
        return "%s - %s" %(self.pto_vta_formateado(), self.num_comp_formateado())
    
    @property
    def identificador_completo(self):
        return "%s %s - %s" %(self.tipo, self.pto_vta_formateado(), self.num_comp_formateado())
    
    @property
    def iva(self):
        return self.iva105 + self.iva21 + self.iva27
    
    @property
    def fecha_dd_mm_aaaa(self):
        return self.fecha.strftime('%d/%m/%Y')
    
    @property
    def SALDO(self):
        resto = self.total
        pagos = Detalle_pago.objects.filter(compra=self)
        for pago in pagos:
            resto -= pago.monto
        return resto
    
class Detalle_compra(models.Model):
    IVA_CHOICES=(
                 (0,"No Aplica"),
                 (10.5,"10.5%"),
                 (21,"21%"),
                 (27,"27%")
                 )
    compra = models.ForeignKey(Compra)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    detalle = models.TextField(max_length=200)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    iva = models.FloatField(choices=IVA_CHOICES, default=21, blank=True, null=True)
    iva_valor = models.DecimalField(max_digits=12, decimal_places=2)
    
    @property
    def total(self):
        return self.precio_unitario+self.iva_valor
    

class OrdenPago(models.Model):
    fecha_hora = models.DateTimeField(default=datetime.now(),editable=False)
    fecha = models.DateField(default=datetime.today().strftime('%d/%m/%Y'))
    numero = models.IntegerField(blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor)
    compra = models.ManyToManyField(Compra, through='Detalle_pago')
    credito_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __unicode__(self):
        return "Orden Pago nro: %s -> %s" %(self.numero_full,self.proveedor.razon_social)
    
    def fecha_dd_mm_aaaa(self):
        return self.fecha.strftime('%d/%m/%Y')
    
    @property
    def numero_full(self):
        num=str(self.numero)
        if(0<len(num)<9):
            restante = 8 - len(num)
            if(restante!=0):
                for i in range(restante):
                    num = '0' + num
        return num
    
    @property
    def total(self):
        total = self.dinero_set.all().aggregate(Sum('monto'))['monto__sum']
        return total
    
    @property
    def total_str(self):
        return "%.2f" %self.total
    
    @property
    def saldo_a_cuenta(self):
        dinero=self.dinero_set.all().aggregate(Sum('monto'))['monto__sum']
        compro=self.detalle_pago_set.all().aggregate(Sum('monto'))['monto__sum']
        
        return dinero+self.credito_anterior-compro or 0
    
class Detalle_pago(models.Model):
    compra = models.ForeignKey(Compra)
    orden_pago = models.ForeignKey(OrdenPago)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __unicode__(self):
        return "%s, compra: %s, monto %s" %(self.orden_pago, self.compra, self.monto)
    
    def monto_2d(self):
        return "%.2f" %self.monto
    
class Valores(models.Model):
    TIPOS_CHOICES = (
                ("CHT","Cheque Tercero"),
                ("CHP","Cheque Propio"),
                ("EFE","Efectivo"),
                ("TRB","Transferencia Bancaria"),
               )
    tipo = models.CharField(max_length=3, choices=TIPOS_CHOICES, default=TIPOS_CHOICES[0][0])
    recibo = models.ForeignKey(Recibo, blank=True, null=True)
    #CHEQUE!!!
    cheque_numero = models.CharField(max_length=12, blank=True, null=True)
    cheque_banco = models.ForeignKey(Bancos, blank=True, null=True, related_name = 'cheques')
    cheque_fecha = models.DateField(blank=True, null=True)
    cheque_cobro = models.DateField(blank=True, null=True)
    cheque_titular = models.CharField(max_length=60, blank=True, null=True)
    cheque_cuit_titular = models.CharField(max_length=13, blank=True, null=True)
    cheque_paguese_a = models.CharField(max_length=60, blank=True, null=True)
    cheque_domicilio_de_pago = models.CharField(max_length=200, blank=True, null=True)
    cheque_en_cartera = models.BooleanField(default=True)
    #cheque_entregado_op = models.ForeignKey(OrdenPago, blank=True, null=True) 
    #TRANSFERENCIA!!
    transferencia_banco_origen = models.ForeignKey(Bancos, blank=True, null=True)
    transferencia_cuenta_origen = models.CharField(max_length=22, blank=True, null=True)
    transferencia_numero_operacion = models.CharField(max_length=22, blank=True, null=True)
    transferencia_cuenta_destino = models.ForeignKey(Cuentas_banco, blank=True, null=True)
    monto = models.DecimalField(max_digits=13, decimal_places=3)
    pendiente_para_recibo=models.DecimalField(max_digits=13, decimal_places=3)
    #pendiente_para_orden_pago=models.DecimalField(max_digits=13, decimal_places=3)
    observaciones = models.TextField(blank=True, null=True)
    
    def cheque_fecha_dd_mm_aaaa(self):
        if self.cheque_fecha:
            return self.cheque_fecha.strftime('%d/%m/%Y')
        else:
            return ""
    
    def monto_2d(self):
        return "%.2f" %self.monto
    
class Dinero(models.Model):
    monto = models.DecimalField(max_digits=13, decimal_places=3)
    recibo = models.ForeignKey(Recibo, blank=True, null=True)
    orden_pago=models.ForeignKey(OrdenPago, blank=True, null=True)
    pendiente_para_recibo=models.DecimalField(max_digits=13, decimal_places=3, default=0)
    pendiente_para_orden_pago=models.DecimalField(max_digits=13, decimal_places=3, default=0)
    
    def __unicode__(self):
        try:
            return "Cheque tercero N %s" %self.chequetercero.numero
        except self.DoesNotExist:
            try:
                return "Cheque propio N %s" %self.chequepropio.numero
            except self.DoesNotExist:
                return "EFECTIVO por %s" %self.monto
    
    @property
    def tipo_valor(self):
        try:
            if self.chequetercero: return "Ch. Tercero"
        except self.DoesNotExist:
            try:
                if self.chequepropio: return "Ch. Propio"
            except self.DoesNotExist:
                try:
                    if self.transferenciabancariasaliente: return "Transferencia"
                except self.DoesNotExist:
                    return "Efectivo"
    @property
    def entidad(self):
        try:
            if self.chequetercero: return self.chequetercero.banco
        except self.DoesNotExist:
            try:
                if self.chequepropio or self.transferenciabancariasaliente: return "BANCO LOCAL"
            except self.DoesNotExist:
                return ""
            
    @property
    def num_comprobante(self):
        try:
            if self.chequetercero: return self.chequetercero.numero
        except self.DoesNotExist:
            try:
                if self.chequepropio: return self.chequepropio.numero
            except self.DoesNotExist:
                try:
                    if  self.transferenciabancariasaliente: return self.transferenciabancariasaliente.numero_operacion
                except self.DoesNotExist:
                    return ""
    
    @property
    def CUIT(self):
        try:
            if self.chequetercero: return self.chequetercero.cuit_titular
        except self.DoesNotExist:
            try:
                if self.chequepropio: return CUIT
            except self.DoesNotExist:
                try:
                    if  self.transferenciabancariasaliente: return ""
                except self.DoesNotExist:
                    return ""
    
    @property
    def FECHA(self):
        try:
            if self.chequetercero: return self.chequetercero.cobro.strftime('%d/%m/%Y')
        except self.DoesNotExist:
            try:
                if self.chequepropio: return self.chequepropio.cobro.strftime('%d/%m/%Y')
            except self.DoesNotExist:
                try:
                    if  self.transferenciabancariasaliente: return ""
                except self.DoesNotExist:
                    return ""
        

class ChequeTercero(Dinero):
    numero = models.CharField(max_length=12, blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    cobro = models.DateField(blank=True, null=True)
    paguese_a = models.CharField(max_length=60, blank=True, null=True)
    #pendiente_para_recibo=models.DecimalField(max_digits=13, decimal_places=3)
    #pendiente_para_orden_pago=models.DecimalField(max_digits=13, decimal_places=3)
    titular = models.CharField(max_length=60, blank=True, null=True)
    cuit_titular = models.CharField(max_length=13, blank=True, null=True)
    banco = models.ForeignKey(Bancos, blank=True, null=True, related_name = 'cheques1')
    en_cartera = models.BooleanField(default=True)
    domicilio_de_pago = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.CharField(max_length=200, blank=True, null=True)
    
    def __unicode__(self):
        return "Cheque de terceros N %s" %self.numero
    
    def fecha_dd_mm_aaaa(self):
        return self.fecha.strftime('%d/%m/%Y')

class ChequePropio(Dinero):
    numero = models.CharField(max_length=12)
    fecha = models.DateField()
    cobro = models.DateField()
    paguese_a = models.CharField(max_length=60)
    #banco = models.ForeignKey(Bancos, blank=True, null=True, related_name = 'cheques1')
    #cheque_domicilio_de_pago = models.CharField(max_length=200, blank=True, null=True)
    #pendiente_para_orden_pago=models.DecimalField(max_digits=13, decimal_places=3)
    
    def __unicode__(self):
        return "Cheque propio N° %s" %self.numero
    
    def fecha_dd_mm_aaaa(self):
        return self.fecha.strftime('%d/%m/%Y')
    
class TransferenciaBancariaEntrante(Dinero):
    banco_origen = models.ForeignKey(Bancos, blank=True, null=True)
    cuenta_origen = models.CharField(max_length=22, blank=True, null=True)
    numero_operacion = models.CharField(max_length=22)
    cuenta_destino = models.ForeignKey(Cuentas_banco)
    
class TransferenciaBancariaSaliente(Dinero):
    #banco_origen = models.ForeignKey(Bancos, blank=True, null=True)
    cuenta_origen = models.ForeignKey(Cuentas_banco)
    numero_operacion = models.CharField(max_length=22)
    cuenta_destino = models.CharField(max_length=22, blank=True, null=True)  