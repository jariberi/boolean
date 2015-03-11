# -*- coding: utf-8 -*-

from boolean_app.models import Proveedor
from pdb import set_trace
from django.contrib.auth.models import User
if __name__ == "__main__":
    u=User.objects.get(pk=1)
    with open ("/home/jorge/Escritorio/COMERCIO/TPROVEEDOR.txt") as f:
        i=0
        for line in f:
            #line.replace('\"','')
            prov = {'CORDOBA':'CD','SANTA FE':'SF','BUENOS AIRES':'BA','ENTRE RIOS':'ER','CHACO':'CC',\
                    'SANTIAGO DEL ESTERO':'SE','LA PAMPA':'LP','RIO NEGRO':'RN', 'CAPITAL FEDERAL':'CP',\
                    'MENDOZA':'MZ'}
            civa = {'RESPONSABLE INSCRIPTO':'RI','MONOTRIBUTO':'MO','RESPONSABLE EXENTO':'RE'}
            c=line.split(";")
            #set_trace()
            #Guiones al cuit
            cuit = c[11]
            new_cuit = cuit[:2]+ '-' + cuit[2:10] + '-' + cuit[10:11]
            #set_trace()
            Proveedor.objects.create(razon_social=c[1],direccion=c[3],localidad=c[4],codigo_postal=c[5],\
                                     provincia=prov[c[6]], telefono=c[8],fax=c[9],email=c[10],cuit=new_cuit,\
                                     condicion_iva=civa[c[12]], codigo_ingresos_brutos=c[13],\
                                     modificado_por=u, contacto=c[14])
            i=i+1
            print i
                    