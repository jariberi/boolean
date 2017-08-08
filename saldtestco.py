#!/usr/local/bin/python2.7
# encoding: utf-8
'''
boolean_app.mig_scripts.saldtest -- Comprueba y corrige los saldos de los proveedores en SF

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
__date__ = '2016-03-06'
__updated__ = '2016-03-06'

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


def main(argv=None):  # IGNORE:C0111
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
        django_settings = args.setting
        path = args.path

        print("-----INICIO-----")

        # INICIO DEL SCRIPT
        logger = logging.getLogger('saldtestco')
        hdlr = logging.FileHandler(os.path.dirname(os.path.realpath(__file__)) + '/log.txt')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.DEBUG)
        # logging.basicConfig(filaname='log.txt', level=logging.DEBUG)
        logger.debug("---INICIO---")
        logger.debug("Seteando settings de Django en Environment...: %s" % django_settings)
        os.environ['DJANGO_SETTINGS_MODULE'] = django_settings
        logger.debug("Seteando settings de Django en Environment... OK")
        logger.debug("Seteando Path del proyecto de Django...: %s" % path)
        sys.path.append(path)
        logger.debug("Seteando Path del proyecto de Django... OK")

        if verbose:
            print("--Seteado Django Settings--")
        # BUSCAR TODOS LOS CLIENTES
        # from django_settings.core import management
        # import boolean.settings as settings
        # management.setup_environ(settings)
        django.setup()
        from boolean_app.models import Proveedor, Compra, Detalle_pago
        from django.db.models import Q, Sum
        proveedores = Proveedor.objects.all()
        logger.debug("Encontrados %s proveedores" % len(proveedores))
        i = 1
        for pro in proveedores:
            logger.debug("Cheking proveedor %s: (%s) %s" % (i, pro.pk, pro.razon_social))
            logger.debug("Calculando saldo manualmente")
            # print ("Chequeando %s: %s" %(i, pro))
            prov = Q(proveedor=pro)
            fact = Q(tipo__startswith="FA")
            nd = Q(tipo__startswith="ND")
            factu = Compra.objects.filter(prov, fact)
            sumfactu=0
            for fa in factu:
                sumfactu += fa.neto + fa.iva21 + fa.iva105 + fa.iva27 + fa.percepcion_iva + fa.exento + fa.ingresos_brutos + fa.impuesto_interno + fa.redondeo 
            nde = Compra.objects.filter(prov, nd)
            sumnde = 0
            for qq in nde:
                sumnde += qq.neto + qq.iva21 + qq.iva105 + qq.iva27 + qq.percepcion_iva + qq.exento + qq.ingresos_brutos + qq.impuesto_interno + qq.redondeo
            nc = Q(tipo__startswith="NC")
            ncrs = Compra.objects.filter(prov, nc)
            sumncrs = 0
            for aa in ncrs:
                sumncrs += aa.neto + aa.iva21 + aa.iva105 + aa.iva27 + aa.percepcion_iva + aa.exento + aa.ingresos_brutos + aa.impuesto_interno + aa.redondeo
            ordenes = Detalle_pago.objects.filter(orden_pago__proveedor=pro).aggregate(total=Sum("monto"))
            ret = 0
            ret += sumfactu
            logger.debug("Total facturas: %s" % sumfactu)
            logger.debug("Total Nota Debitos: %s" % sumnde)
            ret += sumnde
            logger.debug("Total Nota Creditos: %s" % sumncrs)
            ret += sumncrs
            if ordenes['total']:
                logger.debug("Total Recibos: %s" % ordenes['total'])
                ret -= ordenes['total']
            # if verbose:
            #    print ("Saldo MANUAL Cliente: %s" %ret)
            logger.debug("Saldo MANUAL Cliente: %s" % ret)
            # Busco dinero que tenga saldo a usar
            from boolean_app.models import Dinero
            dine = Dinero.objects.filter(pendiente_para_orden_pago__gt=0, orden_pago__proveedor=pro)
            logger.debug("Encontrado %s valor" % len(dine))
            if dine:
                logger.debug("Valor: %s" % dine[0].pendiente_para_orden_pago)
                ret -= dine[0].pendiente_para_orden_pago
            logger.debug("Saldo MANUAL+VALOR Proveedor: %s" % ret)
            factynd = Compra.objects.filter(prov, fact | nd).order_by('-fecha', '-numero').aggregate(saldo=Sum("saldo"))
            if factynd['saldo']:
                logger.debug("Saldos de comprobantes: %s" % factynd['saldo'])
                if ret != factynd['saldo']:
                    print "DIFERENCIAS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                    logger.debug("DIFERENCIAS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # Caso 1 -> Saldo manual positivo
            # if ret >= 0:
            #     factynd = Compra.objects.filter(prov, fact | nd).order_by('-fecha', '-numero')
            #     for f in factynd:
            #         if ret == 0:
            #             logger.debug("Comprobante %s es cero." % f)
            #             continue
            #             # f.saldo=0
            #             # f.save()
            #         if ret >= f.total:
            #             ret -= f.total
            #             if f.saldo == f.total:
            #                 logger.debug("Comprobante %s es OK." % f)
            #             else:
            #                 # f.saldo=f.total
            #                 # ret-=f.saldo
            #                 # f.save()
            #                 logger.debug("Comprobante %s es ERRONEO. (%s deberia ser %s)" % (f, f.saldo, ret))
            #                 print("Comprobante %s es ERRONEO. (%s deberia ser %s)" % (f, f.saldo, ret))
            #         else:
            #             if ret == f.saldo:
            #                 logger.debug("Comprobante %s es OK." % f)
            #             else:
            #                 logger.debug("Comprobante %s es ERRONEO. (%s deberia ser %s)" % (f, f.saldo, ret))
            #             ret = 0
            # else:
            #     pass
            i += 1

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG:
            raise (e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        # sys.argv.append("-v")
    sys.exit(main())
