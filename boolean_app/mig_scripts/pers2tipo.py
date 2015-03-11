# -*- coding: utf-8 -*-

from boolean_app.models import Articulo, Detalle_venta

if __name__ == "__main__":
    dvs = Detalle_venta.objects.all()
    i = 0
    for dv in dvs:
        i+=1
        if dv.pers:
            dv.tipo_articulo = "AP"
        else:
            dv.tipo_articulo = "AA"
        dv.save()
        print "%s" %i