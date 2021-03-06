from django.conf.urls import patterns, include, url
from boolean_app.views import Home, ClientesList, ClientesNuevo,\
    ClientesModificar, ClientesBorrar, BancosList, BancosNuevo, BancosModificar,\
    BancosBorrar, CondPagoList, CondPagoNuevo, CondPagoModificar, CondPagoBorrar,\
    ArticuloList, ArticuloNuevo, ArticuloModificar, ArticuloBorrar, LineaList,\
    LineaNuevo, LineaModificar, LineaBorrar, RubroList, RubroNuevo,\
    RubroModificar, RubroBorrar, ProveedoresList, ProveedoresNuevo,\
    ProveedoresModificar, ProveedoresBorrar, facturar,\
    get_punto_venta, get_num_prox_comprobante, get_precio_unitario,\
    ListarComprobantesPendientesDeAprobacion, afip_aprob,\
    get_precio_unitario_iva_inc, iva_periodo_fecha, recibo,\
    get_num_prox_recibo, get_facturas_pendiente_pago, actualizarPreciosRubro,\
    ComprobantesList, CobrosList, ventas_totales_fecha, resumen_cuenta,\
    comp_saldo, compra_new, comprasList, chequesList, subdiario_iva_compras,\
    orden_pago_new, get_num_prox_orden_pago, get_facturas_pendiente_pago_prov,\
    PagosList, imprimirOrdenPago, recibo_contado, orden_pago_contado_new,\
    proveedores_resumen_cuenta, proveedores_comp_saldo, rg3685_ventas,\
    rg3685_compras, ventas_totales_a_b_fecha, compras_totales_prov, chequesPropiosList, ventas_totales_clie
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from boolean_app.api import articulo_datatables_view, comp_datatables_view,\
    cobros_datatables_view, get_comprobantes_de_cliente, get_credito_valores,\
    cliente_datatables_view, proveedores_datatables_view,\
    comp_compras_datatables_view, cheques_datatables_view,\
    cheque_quitar_de_cartera, pagos_datatables_view, get_credito_valores_op,\
    get_datos_defecto_cheque, validar_comprobante_compra, cheques_propios_datatables_view
from boolean_app.reports import impr_comprobante, impr_recibo

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

clientesPattern = patterns('',
    url(r'^$', login_required(ClientesList.as_view()), name='listaClientes'),
    url(r'nuevo$', login_required(ClientesNuevo.as_view()), name='nuevoCliente'),
    url(r'editar/(?P<pk>\d+)$', login_required(ClientesModificar.as_view()), name='editarCliente'),
    url(r'borrar/(?P<pk>\d+)$', login_required(ClientesBorrar.as_view()), name='borrarCliente'),
    )

bancosPattern = patterns('',
    url(r'^$', login_required(BancosList.as_view()), name='listaBancos'),
    url(r'nuevo$', login_required(BancosNuevo.as_view()), name='nuevoBanco'),
    url(r'editar/(?P<pk>\d+)$', login_required(BancosModificar.as_view()), name='editarBanco'),
    url(r'borrar/(?P<pk>\d+)$', login_required(BancosBorrar.as_view()), name='borrarBanco'),
    )

cpPattern = patterns('',
    url(r'^$', login_required(CondPagoList.as_view()), name='listaCondPago'),
    url(r'nuevo$', login_required(CondPagoNuevo.as_view()), name='nuevoCondPago'),
    url(r'editar/(?P<pk>\d+)$', login_required(CondPagoModificar.as_view()), name='editarCondPago'),
    url(r'borrar/(?P<pk>\d+)$', login_required(CondPagoBorrar.as_view()), name='borrarCondPago'),
    )

lineasPattern = patterns('',
    url(r'^$', login_required(LineaList.as_view()), name='listaLineas'),
    url(r'nuevo$', login_required(LineaNuevo.as_view()), name='nuevoLinea'),
    url(r'editar/(?P<pk>\d+)$', login_required(LineaModificar.as_view()), name='editarLinea'),
    url(r'borrar/(?P<pk>\d+)$', login_required(LineaBorrar.as_view()), name='borrarLinea'),
    )

rubrosPattern = patterns('',
    url(r'^$', login_required(RubroList.as_view()), name='listaRubros'),
    url(r'nuevo$', login_required(RubroNuevo.as_view()), name='nuevoRubro'),
    url(r'editar/(?P<pk>\d+)$', login_required(RubroModificar.as_view()), name='editarRubro'),
    url(r'borrar/(?P<pk>\d+)$', login_required(RubroBorrar.as_view()), name='borrarRubro'),
    url(r'actualizar_precios/(?P<rubro>\d+)$', login_required(actualizarPreciosRubro), name='actualizarPrecioRubro'),
    )

articulosPattern = patterns('',
    url(r'^$', login_required(ArticuloList.as_view()), name='listaArticulos'),
    url(r'nuevo$', login_required(ArticuloNuevo.as_view()), name='nuevoArticulo'),
    url(r'editar/(?P<pk>\d+)$', login_required(ArticuloModificar.as_view()), name='editarArticulo'),
    url(r'borrar/(?P<pk>\d+)$', login_required(ArticuloBorrar.as_view()), name='borrarArticulo'),
    )

proveedoresPattern = patterns('',
    url(r'^$', login_required(ProveedoresList.as_view()), name='listaProveedores'),
    url(r'nuevo$', login_required(ProveedoresNuevo.as_view()), name='nuevoProveedor'),
    url(r'editar/(?P<pk>\d+)$', login_required(ProveedoresModificar.as_view()), name='editarProveedor'),
    url(r'borrar/(?P<pk>\d+)$', login_required(ProveedoresBorrar.as_view()), name='borrarProveedor'),
    url(r'resumen_cuenta$', login_required(proveedores_resumen_cuenta), name='proveedoresResumenCuenta'),
    url(r'composicion_saldo$', login_required(proveedores_comp_saldo), name='proveedoresComposicionSaldo'),
    )

ventasPattern = patterns('',
    url(r'^$', login_required(ComprobantesList.as_view()), name='listaComprobantes'),
    url(r'lista_pendientes$', login_required(ListarComprobantesPendientesDeAprobacion.as_view()), name='listarPendientes'),
    url(r'nuevo$', login_required(facturar), name='nuevoComprobante'),
    url(r'afip_aprobar/(?P<pk>\d+)$', login_required(afip_aprob), name='afipAprobar'),
    url(r'impr_comprobante/(?P<pk>\d+)$', login_required(impr_comprobante), name='imprimirComprobante'),
    #url(r'editar/(?P<pk>\d+)$', login_required(ProveedoresModificar.as_view()), name='editarProveedor'),
    #url(r'borrar/(?P<pk>\d+)$', login_required(ProveedoresBorrar.as_view()), name='borrarProveedor'),
    )

cobrosPattern = patterns('',
    url(r'^$', login_required(CobrosList.as_view()), name='listarCobros'),
    url(r'cheques_en_cartera$', login_required(chequesList.as_view()), name='listarChequesEnCartera'),
    url(r'cheques_propios$', login_required(chequesPropiosList.as_view()), name='listarChequesPropios'),
    url(r'nuevo$', login_required(recibo), name='nuevoRecibo'),
    url(r'nuevo_contado/(?P<venta>\d+)$', login_required(recibo_contado), name='nuevoReciboContado'),
    url(r'impr_recibo/(?P<pk>\d+)$', login_required(impr_recibo), name='imprimirRecibo'),
    #url(r'aprobado/(?P<pk>\d+)$', login_required(comprobanteAprobado), name='comprobanteAprobado'),
    #url(r'recibo$', login_required(recibo), name='nuevoRecibo'),
    #url(r'editar/(?P<pk>\d+)$', login_required(ProveedoresModificar.as_view()), name='editarProveedor'),
    #url(r'borrar/(?P<pk>\d+)$', login_required(ProveedoresBorrar.as_view()), name='borrarProveedor'),
    )

informesPattern = patterns('',
    url(r'iva_ventas$', login_required(iva_periodo_fecha), name='subdiarioIVAVentas'),
    url(r'exportar_3685_ventas/(?P<periodo>\d+)$', login_required(rg3685_ventas), name='AFIP3685Ventas'),
    url(r'iva_compras$', login_required(subdiario_iva_compras), name='subdiarioIVACompras'),
    url(r'exportar_3685_compras/(?P<periodo>\d+)$', login_required(rg3685_compras), name='AFIP3685Compras'),
    url(r'ventas_totales$', login_required(ventas_totales_fecha), name='informeVentasTotales'),
    url(r'ventas_totales_a_b$', login_required(ventas_totales_a_b_fecha), name='informeVentasTotalesAB'),
    url(r'resumen_cuenta$', login_required(resumen_cuenta), name='informeResumenCuenta'),
    url(r'composicion_saldo$', login_required(comp_saldo), name='informeComposicionSaldo'),
    url(r'compras_por_proveedor$', login_required(compras_totales_prov), name='comprasTotalesProv'),
    url(r'ventas_por_cliente$', login_required(ventas_totales_clie), name='ventasTotalesClie'),
    )

comprasPattern = patterns('',
    url(r'^$', login_required(comprasList.as_view()), name='listaCompras'),
    #url(r'lista_pendientes$', login_required(ListarComprobantesPendientesDeAprobacion.as_view()), name='listarPendientes'),
    url(r'nuevo$', login_required(compra_new), name='nuevaCompra'),
    #url(r'afip_aprobar/(?P<pk>\d+)$', login_required(afip_aprob), name='afipAprobar'),
    #url(r'impr_comprobante/(?P<pk>\d+)$', login_required(impr_comprobante), name='imprimirComprobante'),
    #url(r'editar/(?P<pk>\d+)$', login_required(ProveedoresModificar.as_view()), name='editarProveedor'),
    #url(r'borrar/(?P<pk>\d+)$', login_required(ProveedoresBorrar.as_view()), name='borrarProveedor'),
    )

pagosPattern = patterns('',
    url(r'^$', login_required(PagosList.as_view()), name='listaOrdenesPago'),
    #url(r'lista_pendientes$', login_required(ListarComprobantesPendientesDeAprobacion.as_view()), name='listarPendientes'),
    url(r'nuevo$', login_required(orden_pago_new), name='nuevaOrdenPago'),
    url(r'nuevo_contado/(?P<compra>\d+)$', login_required(orden_pago_contado_new), name='nuevaOrdenPagoContado'),
    #url(r'afip_aprobar/(?P<pk>\d+)$', login_required(afip_aprob), name='afipAprobar'),
    url(r'impr_op/(?P<pk>\d+)$', login_required(imprimirOrdenPago), name='imprimirOrdenPago'),
    #url(r'editar/(?P<pk>\d+)$', login_required(ProveedoresModificar.as_view()), name='editarProveedor'),
    #url(r'borrar/(?P<pk>\d+)$', login_required(ProveedoresBorrar.as_view()), name='borrarProveedor'),
    )

urlpatterns = patterns('',
    url(r'^$', login_required(Home.as_view()), name="home"),
    url(r'^login/$',login, {"template_name":"login.html"}, name="login"),
    url(r'^clientes/', include(clientesPattern)),
    url(r'^bancos/', include(bancosPattern)),
    url(r'^cond_pago/', include(cpPattern)),
    url(r'^articulos/', include(articulosPattern)),
    url(r'^lineas/', include(lineasPattern)),
    url(r'^rubros/', include(rubrosPattern)),
    url(r'^proveedores/', include(proveedoresPattern)),
    url(r'^ventas/', include(ventasPattern)),
    url(r'^informes/', include(informesPattern)),
    url(r'^api/get_punto_venta/(?P<tipo_comprobante>\w{0,50})/$', get_punto_venta,),
    url(r'^api/get_proximo_nro_comprobante/(?P<tipo_comprobante>\w{0,50})/$', get_num_prox_comprobante,),
    url(r'^api/get_precio_unitario/(?P<pk>\d+)/$', get_precio_unitario,),
    url(r'^api/get_precio_unitario_iva_inc/(?P<pk>\d+)/$', get_precio_unitario_iva_inc,),
    url(r'^api/get_num_recibo/$', get_num_prox_recibo,),
    url(r'^api/get_facturas_pendiente_pago/(?P<cliente>\d+)/$', get_facturas_pendiente_pago,),
    url(r'^api/get_credito_valores/(?P<cliente>\d+)/$', get_credito_valores),
    url(r'^api/get_credito_valores_op/(?P<proveedor>\d+)/$', get_credito_valores_op),
    url(r'^api/obtener_articulos_datatables/$', articulo_datatables_view, name='art_datatables'),
    url(r'^api/obtener_clientes_datatables/$', cliente_datatables_view, name='cli_datatables'),
    url(r'^api/obtener_proveedores_datatables/$', proveedores_datatables_view, name='pro_datatables'),
    url(r'^api/obtener_comprobantes_datatables/$', comp_datatables_view, name='comp_datatables'),
    url(r'^api/obtener_compras_datatables/$', comp_compras_datatables_view, name='compras_datatables'),
    url(r'^api/obtener_cobros_datatables/$', cobros_datatables_view, name='cobros_datatables'),
    url(r'^api/obtener_cheques_datatables/$', cheques_datatables_view, name='cheques_datatables'),
    url(r'^api/obtener_cheques_propios_datatables/$', cheques_propios_datatables_view, name='cheques_propios_datatables'),
    url(r'^api/obtener_comprobantes_cliente/(?P<cliente>\d+)/$', get_comprobantes_de_cliente, name='cobros_datatables'),
    url(r'^api/quitar_cheque_de_cartera/$', cheque_quitar_de_cartera, name='cheque_quitar_de_cartera'),
    url(r'^api/obtener_pagos_datatables/$', pagos_datatables_view, name='pagos_datatables'),
    url(r'^api/get_datos_cheque_defecto/(?P<cliente>\d+)/$', get_datos_defecto_cheque, name='datos_def_cheque'),
    url(r'^api/validar_comprobante_compra/$', validar_comprobante_compra, name='validar_comprobante_compra'),

    url(r'^cobros/', include(cobrosPattern)),
    url(r'^compras/', include(comprasPattern)),
    url(r'^pagos/', include(pagosPattern)),
    url(r'^api/get_num_orden_pago/$', get_num_prox_orden_pago,),
    url(r'^api/get_facturas_pendiente_pago_prov/(?P<proveedor>\d+)/$', get_facturas_pendiente_pago_prov,),
    #url(r'^api/get_precio_unitario/', include(ventasPattern)),
    # Examples:
    # url(r'^$', 'boolean.views.home', name='home'),
    # url(r'^boolean/', include('boolean.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
