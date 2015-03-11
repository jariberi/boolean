#-*- coding: utf-8 -*-
'''
Created on 12/10/2014

@author: jorge
'''
import xml.etree.ElementTree as ET
import email
from datetime import datetime, timedelta
from M2Crypto import BIO, SMIME
import os
from suds.client import Client
import logging
import random
from suds import WebFault
from pdb import set_trace
from boolean.settings import PRIVATE_KEY_FILE, CERT_FILE_PROD, CERT_FILE_TEST
from afip_ws.models import AFIP_Datos_Autenticacion
from django.utils import timezone


class WSAA(object):
    '''
    Gestiona todo el proceso de acceso a los WebService de AFIP, incluye pedido TRA, firma del TRA
    y obtencion de la respuesta
    @author: Jorge Riberi - Appline
    @version: 1.0a
    '''
    KEYFILE=CERTFILE=PRODUCCION=RESPUESTA=SIGN=TOKEN=EXPIRATION_TIME=None
    WSAAURL_PRODUCCION="https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl"
    WSAAURL_TESTING="https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"
    ERROR=None

    def __init__(self, produccion=False):
        '''
        Inicializa los parametros
        @param produccion: Si se trabaja en ambiente de producción, en caso de ser False se trabaja en prueba
        '''
        self.PRODUCCION=produccion
        self.KEYFILE=PRIVATE_KEY_FILE
        self.CERTFILE=CERT_FILE_PROD if produccion else CERT_FILE_TEST

    def get_sign(self):
        return self.SIGN


    def get_token(self):
        return self.TOKEN

    
    def _extraerSign(self):
        self.SIGN=str(self.RESPUESTA[1][1].text)
        
    def _extraerToken(self):
        self.TOKEN=str(self.RESPUESTA[1][0].text)
        
    def _extraerET(self):
        te=self.RESPUESTA[0][4].text[:-6]
        appline=datetime.strptime(te,"%Y-%m-%dT%H:%M:%S.%f")
        self.EXPIRATION_TIME=timezone.make_aware(appline, timezone.get_current_timezone())
    
    def generarTRA(self,ttl=120, servicio="wsfe"):
        '''
        Generar un Ticket de Requerimiento de Acceso (TRA) para el servicio establecido en la creacion del objeto
        @param ttl: Tiempo en minutos del plazo de exp del ticket
        '''
        ahora=timezone.now()
        td=timedelta(minutes=ttl)
        tra = ET.fromstring('<?xml version="1.0" encoding="UTF-8"?>'
                 '<loginTicketRequest version="1.0">'
                 '</loginTicketRequest>')
        header=ET.SubElement(tra,'header')
        uniqueId=ET.SubElement(header,'uniqueId')
        uniqueId.text="%s" %random.randint(1,999999999)
        #uniqueId.text=""
        #tra.header.add_child('uniqueId',str(date('U')))
        generationTime=ET.SubElement(header, 'generationTime')
        generationTime.text=(timezone.make_naive(ahora, timezone.get_current_timezone())-td).strftime("%Y-%m-%dT%H:%M:%S")
        #tra.header.add_child('generationTime',str(date('c',date('U')-ttl)))
        expirationTime=ET.SubElement(header, 'expirationTime')
        expirationTime.text=(timezone.make_naive(ahora, timezone.get_current_timezone())+td).strftime("%Y-%m-%dT%H:%M:%S")
        #tra.header.add_child('expirationTime',str(date('c',date('U')+ttl)))
        service=ET.SubElement(tra,'service')
        service.text=servicio
        #tra.add_child('service',service)
        return '<?xml version="1.0" encoding="UTF-8"?>'+ET.tostring(tra)
        #return tra.as_xml()
    
    def firmarTRA(self, tra):
        if BIO:
            # Firmar el texto (tra) usando m2crypto (openssl bindings para python)
            buf = BIO.MemoryBuffer(tra)             # Crear un buffer desde el texto
            s = SMIME.SMIME()                       # Instanciar un SMIME
            # Cargar clave privada y certificado
            if self.KEYFILE.startswith("-----BEGIN RSA PRIVATE KEY-----"):
                key_bio = BIO.MemoryBuffer(self.KEYFILE)
                crt_bio = BIO.MemoryBuffer(self.CERTFILE)
                s.load_key_bio(key_bio, crt_bio)  # (desde buffer)
            elif os.path.exists(self.KEYFILE) and os.path.exists(self.CERTFILE):
                s.load_key(self.KEYFILE, self.CERTFILE)      # (desde archivo)
            else:
                raise RuntimeError("Archivos no encontrados: %s, %s" % (self.KEYFILE, self.CERTFILE))
            p7 = s.sign(buf,0)                      # Firmar el buffer
            out = BIO.MemoryBuffer()                # Crear un buffer para la salida 
            s.write(out, p7)                        # Generar p7 en formato mail

            # extraer el cuerpo del mensaje (parte firmada)
            msg = email.message_from_string(out.read())
            for part in msg.walk():
                filename = part.get_filename()
                if filename == "smime.p7m":                 # es la parte firmada?
                    return part.get_payload(decode=False)   # devolver CMS
                
    def loginWSAA(self, cms):
        if self.PRODUCCION:
            wsaa=Client(self.WSAAURL_PRODUCCION)
        else:
            wsaa=Client(self.WSAAURL_TESTING)
        try:
            resp=wsaa.service.loginCms(cms)
        except WebFault as e: 
            print e.fault
            self.ERROR=e.fault
            print "--------!!!!!!!!!!!-----------!!!!!!!!!!!------------"
            print e.fault.faultcode
        if resp:
            self.RESPUESTA=ET.fromstring(resp)
            print resp
            self._extraerSign()
            self._extraerToken()
            self._extraerET()
            try:
                permiso=AFIP_Datos_Autenticacion.objects.get(produccion=self.PRODUCCION)
                permiso.sign=self.get_sign()
                permiso.token=self.get_token()
                permiso.expiration=self.EXPIRATION_TIME
                permiso.save()
            except AFIP_Datos_Autenticacion.DoesNotExist:
                AFIP_Datos_Autenticacion.objects.create(sign=self.get_sign(),token=self.get_token(),expiration=self.EXPIRATION_TIME, produccion=self.PRODUCCION)
            return True
        else:
            return False

def obtener_o_crear_permiso(produccion=False, ttl=120, servicio="wsfe"):
        try:
            permiso=AFIP_Datos_Autenticacion.objects.get(produccion=produccion)
        except AFIP_Datos_Autenticacion.DoesNotExist:
            wsaa=WSAA(produccion=produccion)
            tra=wsaa.generarTRA(ttl=ttl, servicio=servicio)
            cms=wsaa.firmarTRA(tra)
            print "No hay ningun permiso"
            if wsaa.loginWSAA(cms): return wsaa
        if permiso.expiration > timezone.now():
            wsaa=WSAA(produccion=produccion)
            wsaa.SIGN=permiso.sign
            wsaa.TOKEN=permiso.token
            print "Hay un permiso valido"
            return wsaa
        else:
            wsaa=WSAA(produccion=produccion)
            tra=wsaa.generarTRA(ttl=ttl, servicio=servicio)
            cms=wsaa.firmarTRA(tra)
            print "Hay un permiso pero no es valido"
            if wsaa.loginWSAA(cms): return wsaa
    
        