# -*- coding: utf-8 -*-

from boolean_app.models import Valores, OrdenPago, Proveedor

if __name__ == "__main__":
    ops = Proveedor.objects.all()
    i=1
    for op in ops:
        print i
        op.condicion_iva = op.codigo_ingresos_brutos
        op.save()
        i+=1
    