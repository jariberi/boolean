from boolean_app.models import Rubro
from pdb import set_trace
from django.contrib.auth.models import User
if __name__ == "__main__":
    with open ("/home/jorge/Escritorio/COMERCIO/TRUBROS.txt") as f:
        i=0
        for line in f:
            c=line.split(";")
            #Guiones al cuit
            Rubro.objects.create(cod=c[0],nombre=c[1])
            i=i+1
            print i