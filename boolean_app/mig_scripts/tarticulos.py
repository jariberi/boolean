# -*- coding: utf-8 -*-
from boolean_app.models import Rubro, Linea, Articulo, Proveedor
from pdb import set_trace
from decimal import Decimal

if __name__ == "__main__":
    with open ("/home/jorge/Escritorio/COMERCIO/TARTICULOS.txt") as f:
        i=0
        for line in f:
            c=line.split(";")
            #Rubro
            id_rubro = c[5]
            ru=Rubro.objects.get(cod=id_rubro)
            #set_trace()
            #Medida
            medi = c[8][1:-1]
            me = ""
            if medi=="U" or "C/U":
                me="UN"
            elif medi =="K":
                me="KG"
            elif medi == "M":
                me="MT"
            elif medi == "HS" or medi == "H":
                me="HS"
            else:
                me="U"
            #Linea
            lin = c[26]
            li=None
            if lin == '"Bienes de uso"':
                li = Linea.objects.get(pk=2)
            elif lin == '"Productos"':
                li= Linea.objects.get(pk=1)
            elif lin == '"Fabricación"':
                li = Linea.objects.get(pk=4)
            else:
                li = Linea.objects.get(pk=3)
            #Proveedor unico por ahora
            #Calculo precio venta
            #pv=Decimal(c[13])*((Decimal(c[17])/Decimal(100))+Decimal(1))
            #set_trace()
            pro = Proveedor.objects.get(pk=1)
            Articulo.objects.create(codigo=c[0],codigo_fabrica=c[1][1:-1],denominacion=c[2][1:-1],rubro=ru,unidad_medida=me,\
                                    costo_compra=Decimal(c[13]),descuento_compra=Decimal(c[14]),\
                                    ganancia_venta=Decimal(c[17]),linea=li, proveedor_primario=pro, proveedor_secundario=pro)
            #set_trace()
            i=i+1
            print i