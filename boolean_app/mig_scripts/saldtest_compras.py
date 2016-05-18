#!/usr/local/bin/python2.7
# encoding: utf-8
'''
boolean_app.mig_scripts.saldtest -- Comprueba y corrige los saldos de los clientes y proveedores en SF

boolean_app.mig_scripts.saldtest is a Script de corrección de errores en saldos

It defines classes_and_methods

@author:     Jorge Riberi

@copyright:  2015 Appline. All rights reserved.

@license:    Privada

@contact:    info@appline.com.ar
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import logging
import django
from decimal import Decimal

__all__ = []
__version__ = 0.1
__date__ = '2015-06-22'
__updated__ = '2015-06-22'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Jorge Riberi on %s.
  Copyright 2015 Appline. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-r", "--repair", dest="repair", action="store_true", help="Repair the saldos.")
        parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="set verbosity")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('path', help="Path to Django Project")
        parser.add_argument('setting', help="Settings of Django", default='boolean.settings')

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose
        repair = args.repair
        django=args.setting
        path=args.path

        print("-----INICIO-----")

        #INICIO DEL SCRIPT
        logger = logging.getLogger('saldtest')
        hdlr = logging.FileHandler(os.path.dirname(os.path.realpath(__file__))+'/log_compras.txt')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.DEBUG)
        #logging.basicConfig(filaname='log.txt', level=logging.DEBUG)
        logger.debug("---INICIO---")
        logger.debug("Seteando settings de Django en Environment...: %s" %django)
        os.environ['DJANGO_SETTINGS_MODULE']=django
        logger.debug("Seteando settings de Django en Environment... OK")
        logger.debug("Seteando Path del proyecto de Django...: %s" %path)
        sys.path.append(path)
        logger.debug("Seteando Path del proyecto de Django... OK")

        if verbose:
            print("--Seteado Django Settings--")
        #BUSCAR TODOS LOS CLIENTES
        #from django.core import management
        #import boolean.settings as settings
        #management.setup_environ(settings)
        from boolean_app.models import Proveedor, Compra, Detalle_compra, Dinero
        from django.db.models import Q, Sum
        proveedores=Proveedor.objects.all()
        logger.debug("Encontrados %s proveedores" %len(proveedores))
        i=1
        for prov in proveedores:
            logger.debug("Cheking proveedor %s: (%s) %s" %(i, prov.pk,prov.razon_social))
            logger.debug("Calculando saldo manualmente")
            prove = Q(proveedor=prov)
            fact = Q(tipo__startswith="FA")
            nd = Q(tipo__startswith="ND")
            factu = sum([de.total for de in Compra.objects.filter(prove, fact)])
            nde = sum([de.total for de in Compra.objects.filter(prove, nd)])
            nc = Q(tipo__startswith="NC")
            ncr = sum([de.total for de in Compra.objects.filter(prove, nc)])
            opago = Dinero.objects.filter(orden_pago__proveedor=prov).aggregate(total=Sum("monto"))
            ret=0
            if factu:
                logger.debug("Total facturas: %s" %factu)
                ret += factu
            if nde:
                logger.debug("Total Nota Debitos: %s" %nde)
                ret += nde
            if ncr:
                logger.debug("Total Nota Creditos: %s" %ncr)
                ret += ncr #El valor esta negativo en el comprobante
            if opago['total']:
                logger.debug("Total Orden Pagos: %s" %opago['total'])
                ret -= opago['total']
            #if verbose:
            #    print ("Saldo MANUAL Cliente: %s" %ret)
            logger.debug("Saldo MANUAL Proveedor: %s" %ret)
            #Busco dinero que tenga saldo a usar
            dine = Dinero.objects.filter(pendiente_para_orden_pago__gt=0, orden_pago__proveedor=prov)
            logger.debug("Encontrado %s valor" %len(dine))
            if dine:
                ret += dine[0].pendiente_para_recibo
            logger.debug("Saldo MANUAL+VALOR Cliente: %s" %ret)
            #Caso 1 -> Saldo manual positivo
            #Compruebo que haya diferencias de saldos
            saldo_compro = Compra.objects.filter(prove,fact|nd).aggregate(total=Sum('saldo'))
            try:
                if Decimal('-0.009') <= ret - saldo_compro['total'] <= Decimal('0.009'):
                    continue
            except:
                continue
            if ret >= 0:
                prove = Q(proveedor=prov)
                fact = Q(tipo__startswith="FA")
                nd = Q(tipo__startswith="ND")
                factynd = Compra.objects.filter(prove,fact|nd).order_by('-fecha','-numero')
                for f in factynd:
                    if ret == 0:
                        logger.debug("Comprobante %s deberia ser cero. Saldo: %s" %(f, f.saldo))
                        if repair:
                            f.saldo=0
                            f.pagado=True
                            f.save()
                        continue
                    if ret >= f.total:
                        ret -= f.total
                        if f.saldo == f.total:
                            logger.debug("Comprobante %s es OK. Saldo: %s. Total: %s" %(f, f.saldo, f.total))
                        else:
                            if repair:
                                f.saldo=f.total
                                f.save()
                            logger.debug("Comprobante %s es ERRONEO. (%s deberia ser %s)" %(f, f.saldo, f.total))
                            print("Comprobante %s de %s es ERRONEO. (%s deberia ser %s)" %(f, f.proveedor, f.saldo, f.total))
                    else:
                        if ret == f.saldo:
                            logger.debug("Comprobante %s es OK. Saldo: %s. Total: %s" %(f, f.saldo, f.total))
                        else:
                            logger.debug("Comprobante %s es ERRONEO. (%s deberia ser %s)" %(f,f.saldo,ret))
                            print("Comprobante %s de %s es ERRONEO. (%s deberia ser %s)" %(f, f.proveedor, f.saldo, ret))
                            if repair:
                                f.saldo=ret
                                f.save()
                        ret = 0
            else:
                pass
            i += 1



        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        #sys.argv.append("-v")
    sys.exit(main())