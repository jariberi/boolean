# -*- coding: utf-8 -*-
from boolean_app.models import DetalleArticuloCompuesto
from decimal import Decimal

if __name__ == "__main__":
    acsb=DetalleArticuloCompuesto.objects.filter(detalle_venta__venta__tipo__endswith="B")
    i=1
    for ac in acsb:
        print "Iteracion %s de %s" %(i,len(acsb))
        print ac
        ac.precio_unitario = ac.precio_unitario / Decimal('1.21')
        i+=1