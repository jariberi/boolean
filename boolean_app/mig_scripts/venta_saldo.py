from boolean_app.models import Venta
if __name__ == "__main__":
    i=0
    ventas = Venta.objects.filter(tipo__startswith="FA")
    for venta in ventas:
        venta.saldo=venta.saldo__deprecated()
        venta.save()
        i+=1
        print i