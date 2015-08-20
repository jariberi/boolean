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
        hdlr = logging.FileHandler(os.path.dirname(os.path.realpath(__file__))+'/log.txt')
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
        from boolean_app.models import Cliente, Venta, Detalle_cobro
        from django.db.models import Q, Sum
        clientes=Cliente.objects.all()
        logger.debug("Encontrados %s clientes" %len(clientes))
        i=1
        for cli in clientes:
            logger.debug("Cheking cliente %s: (%s) %s" %(i, cli.pk,cli.razon_social))
            logger.debug("Calculando saldo manualmente")
            #print ("Chequeando %s: %s" %(i, cli))
            clie=Q(cliente=cli)
            fact=Q(tipo__startswith="FA")
            nd=Q(tipo__startswith="ND")
            apr=Q(aprobado=True)
            factu = Venta.objects.filter(clie, apr,  fact).aggregate(total=Sum("total")) 
            nde = Venta.objects.filter(clie, apr,  nd).aggregate(total=Sum("total")) 
            nc=Q(tipo__startswith="NC")
            ncrs = Venta.objects.filter(clie, apr, nc).aggregate(total=Sum("total"))
            recibos = Detalle_cobro.objects.filter(recibo__cliente=cli).aggregate(total=Sum("monto"))
            ret=0
            if factu['total']:
                logger.debug("Total facturas: %s" %factu['total'])
                ret += factu['total']
            if nde['total']:
                logger.debug("Total Nota Debitos: %s" %nde['total'])
                ret += nde['total']
            if ncrs['total']:
                logger.debug("Total Nota Creditos: %s" %ncrs['total'])
                ret -= ncrs['total']
            if recibos['total']:
                logger.debug("Total Recibos: %s" %recibos['total'])
                ret -= recibos['total']
            #if verbose:
            #    print ("Saldo MANUAL Cliente: %s" %ret)
            logger.debug("Saldo MANUAL Cliente: %s" %ret)
            #Busco dinero que tenga saldo a usar
            from boolean_app.models import Dinero
            dine=Dinero.objects.filter(pendiente_para_recibo__gt=0, recibo__cliente=cli)
            logger.debug("Encontrado %s valor" %len(dine))
            if dine:
                ret+=dine[0].pendiente_para_recibo
            logger.debug("Saldo MANUAL+VALOR Cliente: %s" %ret)
            #Caso 1 -> Saldo manual positivo
            if ret >=0:
                factynd= Venta.objects.filter(clie,apr,fact|nd).order_by('-fecha','-numero')
                for f in factynd:
                    if ret==0:
                        logger.debug("Comprobante %s es cero." %f)
                        continue
                        #f.saldo=0
                        #f.save()
                    if ret >= f.total:
                        ret -= f.total
                        if f.saldo==f.total:
                            logger.debug("Comprobante %s es OK." %f)
                        else:
                            #f.saldo=f.total
                            #ret-=f.saldo
                            #f.save()
                            logger.debug("Comprobante %s es ERRONEO. (%s deberia ser %s)" %(f, f.saldo, ret))
                            print("Comprobante %s es ERRONEO. (%s deberia ser %s)" %(f, f.saldo, ret))
                    else:
                        if ret==f.saldo:
                            logger.debug("Comprobante %s es OK." %f)
                        else:
                            logger.debug("Comprobante %s es ERRONEO. (%s deberia ser %s)" %(f,f.saldo,ret))
                        ret=0
            else:
                pass
            i+=1


        
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