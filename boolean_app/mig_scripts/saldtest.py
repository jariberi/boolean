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

from decimal import Decimal

import datetime
from math import fabs

from django.conf import settings
from django.db.models import Q, Sum

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


def order_querysets(ventas=None, debitos=None, creditos=None, recibos=None):
    all = []
    total_length = len(ventas) + len(debitos) + len(creditos) + len(recibos)
    while len(all) <= total_length:
        obj = None
        if len(ventas) > 0:
            if obj == None:
                obj = ventas[0]
        if len(debitos) > 0:
            if obj == None:
                obj = debitos[0]
            else:
                obj = obj if obj.fecha <= debitos[0].fecha else debitos[0]
        if len(creditos) > 0:
            if obj == None:
                obj = creditos[0]
            else:
                obj = obj if obj.fecha <= creditos[0].fecha else creditos[0]
        if len(recibos) > 0:
            if obj == None:
                obj = recibos[0]
            else:
                obj = obj if obj.fecha <= recibos[0].fecha else recibos[0]


def main(argv=None):  # IGNORE:C0111
    def es_cero(numero):
        return True if Decimal("-0.009") < numero < Decimal("0.009") else False

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

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose
        repair = args.repair

        print("-----INICIO-----")

        # INICIO DEL SCRIPT
        logger = logging.getLogger('saldtest')
        hdlr = logging.FileHandler(os.path.dirname(os.path.realpath(__file__)) + '/log.txt')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.DEBUG)
        # logging.basicConfig(filaname='log.txt', level=logging.DEBUG)
        logger.debug("---INICIO---")
        os.environ['DJANGO_SETTINGS_MODULE'] = 'boolean.settings'
        logger.debug("Seteando settings de Django en Environment... OK")
        path = 'D://Workspace//boolean'
        logger.debug("Seteando Path del proyecto de Django...: %s" % path)
        sys.path.append(path)
        logger.debug("Seteando Path del proyecto de Django... OK")
        from boolean_app.models import Cliente, Venta, Detalle_cobro, Dinero, Recibo
        # logger.debug("Seteando settings de Django en Environment...: %s" %django)
        # os.environ['DJANGO_SETTINGS_MODULE']=django
        # logger.debug("Seteando settings de Django en Environment... OK")
        # logger.debug("Seteando Path del proyecto de Django...: %s" %path)
        # sys.path.append(path)
        # logger.debug("Seteando Path del proyecto de Django... OK")

        if verbose:
            print("--Seteado Django Settings--")
        # BUSCAR TODOS LOS CLIENTES
        # from django.core import management
        # import boolean.settings as settings
        # management.setup_environ(settings)
        import django
        django.setup()
        clientes = Cliente.objects.all()
        logger.debug("Encontrados %s clientes" % len(clientes))
        i = 1
        for cli in clientes:
            logger.debug("Cheking cliente %s: (%s) %s" % (i, cli.pk, cli.razon_social))
            print("Cheking cliente %s: (%s) %s" % (i, cli.pk, cli.razon_social))
            saldo_cta_cte = cli.saldo_anterior(datetime.date.today())
            logger.debug("Saldo cuenta corriente: %s" %saldo_cta_cte)
            logger.debug("Ordenando comprobantes.......")
            ventas = Venta.objects.filter(Q(cliente=cli), Q(aprobado=True)).order_by('fecha', 'pk')
            logger.debug("Ordenando recibos.......")
            recibos = Recibo.objects.filter(cliente=cli).order_by('fecha', 'numero')
            logger.debug("Reordenando comprobantes.......")
            for rec in recibos:
                cobros = rec.detalle_cobro_set.all()
                for cobro in cobros:
                    if cobro.venta.fecha_hora > rec.fecha_hora:
                        cobro.venta.fecha_hora = rec.fecha_hora - datetime.timedelta(seconds=20)
                        cobro.venta.save()
            ventas = ventas.order_by('fecha', 'numero')
            todos = []
            cli.saldo = 0
            cli.save()
            logger.debug("Uniendo comprobantes......")
            if ventas:
                while len(ventas) != 0 or len(recibos) != 0:
                    if ventas.first():
                        if recibos.first():
                            if ventas.first().fecha_hora <= recibos.first().fecha_hora:
                                todos.append(ventas.first())
                                ventas = ventas.exclude(pk=ventas.first().pk)
                            else:
                                todos.append(recibos.first())
                                recibos = recibos.exclude(pk=recibos.first().pk)
                        else:
                            todos.append(ventas.first())
                            ventas = ventas.exclude(pk=ventas.first().pk)
                    elif recibos.first():
                        todos.append(recibos.first())
                        recibos = recibos.exclude(pk=recibos.first().pk)
            pendiente_recibo = credito_anterior = None
            if todos:
                for idx, el in enumerate(todos):
                    if isinstance(el, Venta):
                        if idx == 0 and not el.tipo.startswith("FA"):
                            logger.debug("La primer operación no es una factura. ERROR")
                            break
                        if el.tipo.startswith("FA") or el.tipo.startswith("ND"):
                            logger.debug("%s. Factura: %s. Seteando saldo = total -- %s" % (idx, el, el.total))
                            el.saldo = el.total
                            el.save()
                            cli.saldo += el.total
                            cli.save()
                        elif el.tipo.startswith("NC"):
                            logger.debug("%s. Nota de credito: %s. Seteando saldo = total -- %s" % (idx, el, el.total))
                            cli.saldo -= el.total
                            cli.save()
                            el.saldo = el.total
                            el.save()
                            # Descuento de facturas anteriores
                            logger.debug("Descontando de facturas anteriores......")
                            hasta_hoy = todos[0:idx]
                            for f in hasta_hoy:
                                if isinstance(f, Venta):
                                    logger.debug("Saldo factura actual: %s | Saldo NC: %s" % (f.saldo, el.saldo))
                                    if Decimal("-0.009") <= el.saldo <= Decimal("0.009"):
                                        break
                                    if f.saldo > Decimal("0.009"):  # Descuento
                                        if f.saldo >= el.saldo:
                                            f.saldo -= el.saldo
                                            f.save()
                                            el.saldo = 0
                                            el.save()
                                        else:
                                            el.saldo -= f.saldo
                                            el.save()
                                            f.saldo = 0
                                            f.save()
                                        logger.debug("Saldo factura actual: %s | Saldo NC: %s" % (f.saldo, el.saldo))
                    elif isinstance(el, Recibo):
                        logger.debug(
                            "%s. Recibo: %s. Total: %s Facturas pagas: %s" % (
                            idx, el, el.total, [v.venta for v in el.detalle_cobro_set.all()]))
                        # hasta_hoy = todos[0:idx]
                        for rec in el.detalle_cobro_set.all():
                            logger.debug("---Detalle cobro: %s :: %s" %(rec.venta, rec.monto))
                            venta = rec.venta
                            for comp in todos:
                                if comp == venta:
                                    logger.debug("Saldo factura: %s | Monto Recibo: %s" % (comp.saldo, rec.monto))
                                    comp.saldo -= rec.monto
                                    comp.save()
                        pendiente_recibo = el.a_cuenta
                        credito_anterior = el.credito_anterior
                sum_total = 0
                for el in todos:
                    if isinstance(el, Venta):
                        logger.debug("%s, %s" % (el, el.saldo))
                        sum_total += el.saldo
                if fabs(saldo_cta_cte - sum_total)>7:
                    logger.debug("ERROR EN SALDOS!!!!!! == %s" %fabs(saldo_cta_cte - sum_total + pendiente_recibo - credito_anterior))
            else:
                logger.debug("SIN COMPROBANTES")
            i+=1
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG:
            raise (e)
        exc_type, exc_obj, tb = sys.exc_info()
        lineno = tb.tb_lineno
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + str(lineno) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        # sys.argv.append("-v")
    sys.exit(main())
