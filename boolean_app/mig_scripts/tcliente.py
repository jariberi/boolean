from boolean_app.models import Cliente
from pdb import set_trace
from django.contrib.auth.models import User
if __name__ == "__main__":
    u=User.objects.get(pk=1)
    with open ("/home/jorge/Escritorio/COMERCIO/TCLIENTE.txt") as f:
        i=0
        for line in f:
            #line.replace('\"','')
            c=line.split(";")
            #set_trace()
            #Guiones al cuit
            cuit = c[9]
            new_cuit = cuit[:2]+ '-' + cuit[2:10] + '-' + cuit[10:11]
            #set_trace()
            Cliente.objects.create(razon_social=c[1][1:-1],direccion=c[2][1:-1],localidad=c[3][1:-1],codigo_postal=c[4][1:-1],\
                                       provincia=c[5][1:-1], telefono=c[6][1:-1],fax=c[7][1:-1],email=c[8][1:-1],cuit=new_cuit,\
                                       codigo_iva=c[11][1:-1], cond_iva=c[12][1:-1], codigo_ingresos_brutos=c[12][1:-1],\
                                       modificado_por=u)
            i=i+1
            print i
                    