'''
Created on 18/10/2014

@author: jorge
'''

from boolean.settings import CUIT, PUNTO_VENTA_FAA
from suds.client import Client
from suds import WebFault
from datetime import datetime

class WSFEV1(object):
    '''
    classdocs
    '''
    WSAA=None
    SOLICITUD=None
    WSFEV1URL_TESTING='https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL' 
    WSFEV1URL_PRODUCCION = 'https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL'
    TIPO_COMPROBANTE={'FAA':1,'FAB':6,'NCA':3,'NDA':2,'NCB':8,'NDB':7}
    CONCEPTOS_COMPROBANTES={'Productos':1,'Servicios':2,'Productos y servicios':3}
    CAE=CAE_VENC=None
    OBS=[]
    ERRORS_SOLICITUD=[]
    RESULTADO=None

    def __init__(self, wsaa_instance):
        '''
        Constructor
        '''
        self.WSAA = wsaa_instance
    
    def nuevaSolicitudAprobacion(self, cbt_desde, cbt_hasta, imp_total, imp_neto, fecha_cbte,\
                                 concepto=1, tipo_doc=80, nro_doc="", tipo_cbte=1,\
                                 punto_vta=PUNTO_VENTA_FAA, imp_tot_conc=0.00, imp_iva=0.00,\
                                 imp_trib=0.00, imp_op_ex=0.00, fecha_venc_pago=None,\
                                 fecha_serv_desde=None, fecha_serv_hasta=None, \
                                 moneda_id="PES", moneda_ctz="1.0000", caea=None):
        "Creo un objeto factura" 
        sol = {'tipo_doc': tipo_doc, 'nro_doc':  nro_doc,
               'tipo_cbte': tipo_cbte, 'punto_vta': punto_vta,
               'cbt_desde': cbt_desde, 'cbt_hasta': cbt_hasta,
               'imp_total': imp_total, 'imp_tot_conc': imp_tot_conc,
               'imp_neto': imp_neto, 'imp_iva': imp_iva,
               'imp_trib': imp_trib, 'imp_op_ex': imp_op_ex,
               'fecha_cbte': fecha_cbte,
               'fecha_venc_pago': fecha_venc_pago,
               'moneda_id': moneda_id, 'moneda_ctz': moneda_ctz,
               'concepto': concepto,
               'cbtes_asoc': [],
               'tributos': [],
               'iva': [],
            }
        if fecha_serv_desde: sol['fecha_serv_desde'] = fecha_serv_desde
        if fecha_serv_hasta: sol['fecha_serv_hasta'] = fecha_serv_hasta

        self.SOLICITUD = sol
        return True
    
    def agregarCmpAsoc(self, tipo=1, pto_vta=0, nro=0, **kwarg):
        "Agrego un comprobante asociado a una factura (interna)"
        cmp_asoc = {'tipo': tipo, 'pto_vta': pto_vta, 'nro': nro}
        self.SOLICITUD['cbtes_asoc'].append(cmp_asoc)
        return True

    def agregarTributo(self, tributo_id=0, desc="", base_imp=0.00, alic=0, importe=0.00, **kwarg):
        "Agrego un tributo a una factura (interna)"
        tributo = { 'tributo_id': tributo_id, 'desc': desc, 'base_imp': base_imp, 
                    'alic': alic, 'importe': importe}
        self.SOLICITUD['tributos'].append(tributo)
        return True

    def agregarIva(self, iva_id=0, base_imp=0.0, importe=0.0, **kwarg):
        "Agrego un tributo a una factura (interna)"
        iva = { 'iva_id': iva_id, 'base_imp': base_imp, 'importe': importe }
        self.SOLICITUD['iva'].append(iva)
        return True
    
    def consultaUltimoComprobante(self, tipo_cbte):
        if self.WSAA.PRODUCCION:
            wsfec=Client(self.WSFEV1URL_PRODUCCION)
        else:
            wsfec=Client(self.WSFEV1URL_TESTING)
        try:
            auth=wsfec.factory.create('FEAuthRequest')
            auth.Token=self.WSAA.get_token()
            auth.Sign=self.WSAA.get_sign()
            auth.Cuit=CUIT.replace('-', '')
            resp=wsfec.service.FECompUltimoAutorizado(Auth=auth,PtoVta=PUNTO_VENTA_FAA,CbteTipo=tipo_cbte)
        except WebFault as e: 
            print e.fault
            self.ERROR=e.fault
            print "--------!!!!!!!!!!!-----------!!!!!!!!!!!------------"
            print e.fault.faultcode
        if resp:
            print resp
            return resp.CbteNro
        else:
            return False
    
    def consultaComprobante(self, tipo, nro):
        if self.WSAA.PRODUCCION:
            wsfec=Client(self.WSFEV1URL_PRODUCCION)
        else:
            wsfec=Client(self.WSFEV1URL_TESTING)
        try:
            auth=wsfec.factory.create('FEAuthRequest')
            auth.Token=self.WSAA.get_token()
            auth.Sign=self.WSAA.get_sign()
            auth.Cuit=CUIT.replace('-', '')
            fecompconsreq=wsfec.factory.create('FECompConsultaReq')
            fecompconsreq.CbteTipo=tipo
            fecompconsreq.CbteNro=nro
            fecompconsreq.PtoVta=PUNTO_VENTA_FAA
            resp=wsfec.service.FECompConsultar(Auth=auth,FeCompConsReq=fecompconsreq)
        except WebFault as e: 
            print e.fault
            self.ERROR=e.fault
            print "--------!!!!!!!!!!!-----------!!!!!!!!!!!------------"
            print e.fault.faultcode
        if resp:
            print resp
            return resp
        else:
            return False
        
    def CAESolicitar(self):
        s = self.SOLICITUD
        #logging.info("FActura:")
        for item in s:
            print("Clave %s - Valor %s - Tipo: %s" %(item, s[item], type(s[item])))
        if self.WSAA.PRODUCCION:
            wsfec=Client(self.WSFEV1URL_PRODUCCION)
        else:
            wsfec=Client(self.WSFEV1URL_TESTING)
        try:
            #Autorizacion
            auth=wsfec.factory.create('FEAuthRequest')
            auth.Token=self.WSAA.get_token()
            auth.Sign=self.WSAA.get_sign()
            auth.Cuit=CUIT.replace('-', '')
            #Cabecera del comprobante o lote
            fecaecabrequest = wsfec.factory.create('FECAECabRequest')
            fecaecabrequest.CantReg=1
            fecaecabrequest.PtoVta=s['punto_vta']
            fecaecabrequest.CbteTipo=s['tipo_cbte']
            #Detalle
            fecaedetrequest=wsfec.factory.create('FECAEDetRequest')
            fecaedetrequest.Concepto=s['concepto']
            fecaedetrequest.DocTipo=s['tipo_doc']
            fecaedetrequest.DocNro=s['nro_doc']
            fecaedetrequest.CbteDesde=s['cbt_desde']
            fecaedetrequest.CbteHasta=s['cbt_hasta']
            fecaedetrequest.CbteFch=s['fecha_cbte']
            fecaedetrequest.ImpTotal=s['imp_total']
            fecaedetrequest.ImpTotConc=s['imp_tot_conc']
            fecaedetrequest.ImpNeto=s['imp_neto']
            fecaedetrequest.ImpOpEx=s['imp_op_ex']
            fecaedetrequest.ImpTrib=s['imp_trib']
            fecaedetrequest.ImpIVA=s['imp_iva']
            fecaedetrequest.MonId=s['moneda_id']
            fecaedetrequest.MonCotiz=s['moneda_ctz']
            arrayofcbte=wsfec.factory.create('ArrayOfCbteAsoc')
            for cbte_asoc in s['cbtes_asoc']:
                cbte=wsfec.factory.create('CbteAsoc')
                cbte.Tipo=cbte_asoc['tipo']
                cbte.PtoVta=cbte_asoc['pto_vta']
                cbte.Nro=cbte_asoc['nro']
                arrayofcbte.CbteAsoc.append(cbte)
            fecaedetrequest.CbtesAsoc=arrayofcbte
            arrayofiva=wsfec.factory.create('ArrayOfAlicIva')
            for iva in s['iva']:
                iv=wsfec.factory.create('AlicIva')
                iv.Id=iva['iva_id']
                iv.BaseImp=iva['base_imp']
                iv.Importe=iva['importe']
                arrayofiva.AlicIva.append(iv)
            fecaedetrequest.Iva=arrayofiva
            fecaereq=wsfec.factory.create('FECAERequest')
            fecaereq.FeCabReq=fecaecabrequest
            arraydetreq=wsfec.factory.create('ArrayOfFECAEDetRequest')
            arraydetreq.FECAEDetRequest.append(fecaedetrequest)
            fecaereq.FeDetReq=arraydetreq
            print auth
            print fecaereq
            resp=wsfec.service.FECAESolicitar(Auth=auth,FeCAEReq=fecaereq)
        except WebFault as e: 
            print e.fault
            self.ERROR=e.fault
            print "--------!!!!!!!!!!!-----------!!!!!!!!!!!------------"
            print e.fault.faultcode
            return False
        self.RESULTADO=resp.FeDetResp[0][0].Resultado
        if resp.FeDetResp[0][0].Resultado == 'A':
            #Quitar 'print resp' cuando salga de version beta
            print resp
            self.CAE=resp.FeDetResp[0][0].CAE
            self.CAE_VENC=datetime.strptime(resp.FeDetResp[0][0].CAEFchVto, "%Y%m%d").date()
            try:
                for ob in resp.FeDetResp[0][0].Observaciones[0]:
                    self.OBS.append(ob.Msj)
            except AttributeError:
                self.OBS=None
            return True
        elif resp.FeDetResp[0][0].Resultado == 'R' or resp.FeCabResp.Resultado == 'R':
            self.ERRORS_SOLICITUD=[]
            try:
                for er in resp.Errors[0]:
                    self.ERRORS_SOLICITUD.append(er.Msg)
            except AttributeError:
                self.ERRORS_SOLICITUD=[]
            self.OBS=[]
            try:
                for ob in resp.FeDetResp[0][0].Observaciones[0]:
                    self.OBS.append(ob.Msj)
            except AttributeError:
                self.OBS=[]
            return False