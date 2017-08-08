#!/usr/local/bin/python2.7
# encoding: utf-8

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

if __name__ == "__main__":
    logger = logging.getLogger('saldtest')
    hdlr = logging.FileHandler(os.path.dirname(os.path.realpath(__file__)) + '/log.txt')
    formatter = logging.Formatter('%(asctime)s %(message)s')
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
    from boolean_app.models import Cliente, Venta, Detalle_cobro, Dinero, Recibo, Proveedor, Compra
    import django

    django.setup()
    logger.debug("----------------------CLIENTES-----------------------------")
    clientes = Cliente.objects.all()
    logger.debug("Encontrados %s clientes" % len(clientes))

    for idx, cli in enumerate(clientes):
        if len(Venta.objects.filter(cliente=cli)) == 0:
            continue
        logger.debug("Checking cliente %s: (%s) %s" % (idx, cli.pk, cli.razon_social))
        print("Checking cliente %s: (%s) %s" % (idx, cli.pk, cli.razon_social))
        saldo_cta_cte = cli.saldo_anterior(datetime.date.today() + datetime.timedelta(days=1))
        saldo_comp = Venta.objects.filter(cliente=cli, pagado=False).aggregate(Sum("saldo"))['saldo__sum'] or 0
        try:
            dinero = Dinero.objects.get(recibo__cliente=cli, pendiente_para_recibo__gt=0).pendiente_para_recibo
        except Dinero.DoesNotExist:
            dinero = 0
        logger.debug("+ Composicion Saldo: %s" % saldo_comp)
        logger.debug("- Saldo Cta Cte: %s" % saldo_cta_cte)
        logger.debug("- Dinero pendiente: %s" % dinero)
        logger.debug("= Total: %s" % (saldo_comp - saldo_cta_cte - dinero))
        if abs(saldo_comp - saldo_cta_cte - dinero) > 2:
            logger.debug("ERROR EN SALDOS --- CONTROLAR!")
        else:
            logger.debug("OK!")

    logger.debug("----------------------PROVEEDORES-----------------------------")
    proveedores = Proveedor.objects.all()
    logger.debug("Encontrados %s proveedores" % len(proveedores))

    for idx, pro in enumerate(proveedores):
        if len(Compra.objects.filter(proveedor=pro)) == 0:
            continue
        logger.debug("Checking proveedor %s: (%s) %s" % (idx, pro.pk, pro.razon_social))
        print("Checking proveedor %s: (%s) %s" % (idx, pro.pk, pro.razon_social))
        saldo_cta_cte = pro.saldo_anterior(datetime.date.today() + datetime.timedelta(days=1))
        saldo_comp = Compra.objects.filter(Q(proveedor=pro), ~Q(saldo=0)).aggregate(Sum("saldo"))['saldo__sum'] or 0
        try:
            dinero = Dinero.objects.get(orden_pago__proveedor=pro, pendiente_para_orden_pago__gt=0).pendiente_para_orden_pago
        except Dinero.DoesNotExist:
            dinero = 0
        except Dinero.MultipleObjectsReturned:
            dinero = Dinero.objects.filter(orden_pago__proveedor=pro, pendiente_para_orden_pago__gt=0).first().pendiente_para_orden_pago
        logger.debug("+ Composicion Saldo: %s" % saldo_comp)
        logger.debug("- Saldo Cta Cte: %s" % saldo_cta_cte)
        logger.debug("- Dinero pendiente: %s" % dinero)
        logger.debug("= Total: %s" % (saldo_comp - saldo_cta_cte - dinero))
        if abs(saldo_comp - saldo_cta_cte - dinero) > 2:
            logger.debug("ERROR EN SALDOS --- CONTROLAR!")
        else:
            logger.debug("OK!")
