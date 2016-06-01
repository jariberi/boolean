from boolean_app.models import Articulo, Venta, Recibo, Detalle_cobro, Proveedor,\
    Valores, Compra, Dinero, OrdenPago, ChequeTercero, Cliente, ChequePropio
from django.db.models import Q
from StringIO import StringIO
from django.http.response import HttpResponse
import json
from datetime import date
from django.core.urlresolvers import reverse_lazy
from decimal import Decimal
from pdb import set_trace
from boolean.settings import RAZON_SOCIAL_EMPRESA
import datetime
import re

def _getattr_foreingkey(obj, attr):
    pt = attr.count('.')
    if pt == 0:#No hay clave foranea
        re = getattr(obj, attr)
        if isinstance(re, date):
            return re.strftime("%d/%m/%Y")
        if isinstance(re, Decimal):
            return "%.2f" %re
        else:
            return re
    else:
        nobj = getattr(obj, attr[:attr.find('.')])
        nattr = attr[attr.find('.')+1:]
        return _getattr_foreingkey(nobj,nattr)

def get_cantidad_tiempo(detalle):
    #set_trace()
    if detalle.tipo_articulo=="AA":
        if detalle.articulo and detalle.articulo.unidad_medida=="HS":
            mins = int(round((detalle.cantidad-int(detalle.cantidad))*60))
            return "%s:%s" %(int(detalle.cantidad),mins)
        else:
            return "%.2f" %detalle.cantidad
    else:
        return "%.2f" %detalle.cantidad

def get_cantidad_tiempo_ac(ac):
    if not ac.pers:
        if ac.articulo.unidad_medida=="HS":
            mins = int(round((ac.cantidad-int(ac.cantidad))*60))
            return "%s:%s" %(int(ac.cantidad),mins)
        else:
            return "%.2f" %ac.cantidad
    else:
        return "%.2f" %ac.cantidad

def filtering(get, dataset, data_struct, global_search):
    """
    :param get: Diccionario GET del request de la vista, para buscar los parametros
    :param dataset: Dataset con la info, normalmente objects.all()
    :param data_struct: Dictionario con la estructura de la tabla {0:'columna_a',1:'columna_b'}
    :param global_search: En que columna debe buscar el termino global
    :return: Dataset filtrado segun los parametros
    """
    # Extraccion de las busquedas indivuales
    individual_searchs_i = {}
    for item in get:
        match = re.match(r'columns\[(\d+)\]\[search\]\[value\]', item)
        if match and get[item]:
            individual_searchs_i[int(match.group(1))] = int(get[item])
    # Filtrado de los datos
    search = get['search[value]']
    queries_g = []
    for item in global_search:
        queries_g.append(Q(**{item + '__icontains': search}))
    print queries_g
    qs = reduce(lambda x, y: x | y, queries_g)
    queries_i = []
    for k, v in individual_searchs_i.iteritems():
        if v == 'false':
            queries_i.append(Q(**{data_struct[k]: False}))
        if v == 'true':
            queries_i.append(Q(**{data_struct[k]: True}))
        else:
            queries_i.append(Q(**{data_struct[k] + '__icontains': v}))
    if individual_searchs_i:
        qi = reduce(lambda x, y: x & y, queries_i)
        qs = qs | qi
    return dataset.filter(qs)


def ordering(get, dataset, data_struct):
    individual_orders = {}
    for item in get:
        match_dir = re.match(r'order\[(\d+)\]\[dir\]', item)
        match_col = re.match(r'order\[(\d+)\]\[column\]', item)
        if match_dir or match_col and get[item]:
            if match_dir:
                i = int(match_dir.group(1))
                if i not in individual_orders:
                    individual_orders[i] = ['', '']
                individual_orders[i][0] = get[item]
            if match_col:
                i = int(match_col.group(1))
                if i not in individual_orders:
                    individual_orders[i] = ['', '']
                individual_orders[i][1] = get[item]
    dirs = {'asc': '', 'desc': '-'}
    ordering = []
    for k, order in individual_orders.iteritems():
        ordering.append(dirs[order[0]] + data_struct[int(order[1])])
    ordering = tuple(ordering)
    return dataset.order_by(*ordering)


def make_data(dataset, list_display, url_modif=None, url_suspen=None, url_hab=None, detalle=None):
    """
    :param dataset: Dataset con la info, normalmente objects.all()
    :param list_display:
    :return: Datos en Array
    """
    data = []
    for obj in dataset:
        row = map(lambda field: _getattr_foreingkey(obj, field), list_display)
        if url_modif:
            row.append('<a href="%s"><i class="material-icons">mode_edit</i></a>' % reverse(url_modif, args=[obj.pk]))
        if url_suspen and url_hab:
            if obj.suspendido:
                row.append('<a href="%s"><i class="material-icons">keyboard_arrow_up</i></a>' % reverse(url_hab,
                                                                                                        args=[obj.pk]))
            else:
                row.append('<a href="%s"><i class="material-icons">keyboard_arrow_down</i></a>' % reverse(url_suspen,
                                                                                                          args=[
                                                                                                              obj.pk]))
        if detalle:
            real_detail = {}
            for field in re.findall(r'%\((\w+\(*\)*)\)s', detalle):
                real_detail[field] = getattr(obj, field[:-2])() if field.endswith("()") else getattr(obj, field)
            deta = detalle % real_detail
            row.insert(0, deta)
        data.append(row)
    return data


def format_det_venta(detalles_venta):
    html = """<table>
                <thead>
                    <tr>
                        <td>Cantidad</td>
                        <td>Articulo</td>
                        <td>P. Unitario</td
                        ><td>P. Total</td>
                    </tr>
                </thead>
                <tbody>"""
    for det in detalles_venta:
        print "Detalle venta"
        print det.id
        html = html + "<tr><td>"+get_cantidad_tiempo(det)+"</td>"
        if det.articulo and det.tipo_articulo == "AA":
            html = html + "<td>"+det.articulo.codigo+" "+det.articulo.codigo_fabrica+" "+det.articulo.denominacion+"</td>"
        elif det.tipo_articulo == "AP":
            html = html + "<td>"+det.articulo_personalizado+"</td>"
        elif det.tipo_articulo == "AC":
            html = html + "<td><table><tbody>"
            acs = det.detallearticulocompuesto_set.all()
            for ac in acs:
                html = html + "<tr><td>"+get_cantidad_tiempo_ac(ac)+"</td>"
                if ac.articulo:
                    html = html + "<td>"+ac.articulo.denominacion+"</td>"
                elif ac.articulo_personalizado:
                    html = html + "<td>"+ac.articulo_personalizado+"</td>"
                html = html + "<td>"+"%.2f" %ac.precio_unitario+"</td>"
                html = html + "<td>"+"%.2f" %ac.total_con_descuento_factura_e_item+"</td>"
                html = html + "</tr>"
            html = html + "</tbody></table></td>"
        html = html + "<td>"+"%.2f" %det.precio_unitario+"</td>"
        html = html + "<td>"+"%.2f" %det.total_con_descuento_factura+"</td>"
        html = html + "</tr>"
    html = html + "</tbody></table>"
    return html
    

def articulo_datatables_view(request):
    objects = Articulo.objects.all()
    desde = request.GET['desde']
    es_b = True if 'es_b' in request.GET else False
    print es_b
    if desde == 'seleccionArticulo':
        list_display = ['pk','codigo', 'codigo_fabrica','denominacion','rubro.nombre','precio_venta']
        #list_filter = ['codigo', 'codigo_fabrica','denominacion']
    elif desde == 'mainArticulos':
        list_display = ['codigo', 'codigo_fabrica','denominacion','linea.nombre','rubro.nombre','ultima_actualizacion_precio']
        list_filter = ['codigo', 'codigo_fabrica','denominacion','linea__nombre','rubro__nombre']
    
    # Cuenta total de articulos:
    recordsTotal = objects.count()

    #Filtrado de los articulos
    search = request.GET['search[value]']
    if desde == 'seleccionArticulo':
        queries = []
        qcodigo = Q(**{'codigo__icontains' : search})
        queries.append(qcodigo)
        qcodigo_fabrica = Q(**{'codigo_fabrica__icontains' : search})
        queries.append(qcodigo_fabrica)
        qdenocontains = Q(**{'denominacion__icontains' : search})
        queries.append(qdenocontains)
        deno = ""
        if search:
            for pa in search.replace("  "," ").split(" "):
                if pa and pa is not " ":
                    deno = deno + "+"+pa+" "
            #set_trace()
            print deno
            qdenominacion = Q(**{'denominacion__search' : deno})
            queries.append(qdenominacion)        
        #queries = [Q(**{f+'__contains' : search}) for f in list_filter]
        qs = reduce(lambda x, y: x|y, queries)
        objects = objects.filter(qs)
    elif desde == 'mainArticulos':
        queries = [Q(**{f+'__icontains' : search}) for f in list_filter]
        qs = reduce(lambda x, y: x|y, queries)
        objects = objects.filter(qs)

    #Ordenado
    #order = dict( enumerate(list_display) )
    #dirs = {'asc': '', 'desc': '-'}
    #ordering = dirs[request.GET['sSortDir_0']] + order[int(request.GET['iSortCol_0'])]
    #objects = objects.order_by(ordering)

    # Conteo de articulos despues dle filtrado
    recordsFiltered = objects.count()


    # finally, slice according to length sent by dataTables:
    start = int(request.GET['start'])
    length = int(request.GET['length'])
    objects = objects[ start : (start+length)]
    
    # extract information
    #data = [map(lambda field: _getattr_foreingkey(obj, field), list_display) for obj in objects]
    data = []
    for obj in objects:
        row=map(lambda field: _getattr_foreingkey(obj, field), list_display)
        if es_b:
            row[5]= obj.precio_venta_iva_inc
        if desde == 'mainArticulos':
            ops = '<a href="%s">EDITAR</a>  --  <a href="%s">BORRAR</a>' %(reverse_lazy('editarArticulo',args=[obj.pk]),reverse_lazy('borrarArticulo',args=[obj.pk])) 
            row.append(ops)
        data.append(row)
        

    #define response
    response = {
        'data': data,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'draw': request.GET['draw']
    }

    #serialize to json
    s = StringIO()
    json.dump(response, s)
    s.seek(0)
    return HttpResponse(s.read())

def comp_datatables_view(request):
    comprobantes = Venta.objects.all().order_by('fecha','tipo','numero')
    print len(comprobantes)
    list_display = ['fecha', 'tipo','pto_vta_num_full','cliente.razon_social','neto','iva21','total','aprobado']
    list_filter = ['cliente__razon_social']

    # Cuenta total de articulos:
    recordsTotal = comprobantes.count()

    #Filtrado de los articulos
    search = request.GET['search[value]']
    queries = [Q(**{f+'__icontains' : search}) for f in list_filter]
    qs = reduce(lambda x, y: x|y, queries)
    comprobantes = comprobantes.filter(qs)

    #Ordenado
    #order = dict( enumerate(list_display) )
    #dirs = {'asc': '', 'desc': '-'}
    #ordering = dirs[request.GET['sSortDir_0']] + order[int(request.GET['iSortCol_0'])]
    #objects = objects.order_by(ordering)

    # Conteo de articulos despues dle filtrado
    recordsFiltered = comprobantes.count()


    # finally, slice according to length sent by dataTables:
    start = int(request.GET['start'])
    length = int(request.GET['length'])
    comprobantes = comprobantes[ start : (start+length)]
    
    # extract information
    #data = [map(lambda field: _getattr_foreingkey(obj, field), list_display) for obj in objects]
    data = []
    for obj in comprobantes:
        print obj.id 
        row=map(lambda field: _getattr_foreingkey(obj, field), list_display)
        detalles_venta_html = format_det_venta(obj.detalle_venta_set.all())
        row.insert(0,detalles_venta_html)
        if row[-1]:
            row[-1]="Aprobado"
        else:
            row[-1]="Borrador"
            row[3]="N/A"
        ops = '<a class="imprimirComprobante" href="%s">IMPRIMIR</a>' %(reverse_lazy('imprimirComprobante',args=[obj.pk])) if obj.aprobado else "" 
        row.append(ops)
        #Es un table (<table>..........</table>
        data.append(row)
        

    #define response
    response = {
        'data': data,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'draw': request.GET['draw']
    }

    #serialize to json
    s = StringIO()
    json.dump(response, s)
    s.seek(0)
    return HttpResponse(s.read())

def cobros_datatables_view(request):
    cobros = Recibo.objects.all()
    #Campos directos, personalizacion mas adelante
    list_display = ['fecha', 'numero_full','cliente.razon_social','total_str']
    list_filter = ['numero', 'cliente__razon_social']
    data_struct = {0: 'fecha', 1: 'numero', 2: 'cliente__razon_social'}

    # Cuenta total de articulos:
    recordsTotal = cobros.count()

    #Filtrado de los articulos
    search = request.GET['search[value]']
    queries = [Q(**{f+'__icontains' : search}) for f in list_filter]
    qs = reduce(lambda x, y: x|y, queries)
    cobros = cobros.filter(qs)

    #Ordenado
    cobros = ordering(request.GET, cobros, data_struct)
    #order = dict( enumerate(list_display) )
    #dirs = {'asc': '', 'desc': '-'}
    #ordering = dirs[request.GET['sSortDir_0']] + order[int(request.GET['iSortCol_0'])]
    #objects = objects.order_by(ordering)

    # Conteo de articulos despues dle filtrado
    recordsFiltered = cobros.count()


    # finally, slice according to length sent by dataTables:
    start = int(request.GET['start'])
    length = int(request.GET['length'])
    cobros = cobros[ start : (start+length)]
    
    # extract information
    #data = [map(lambda field: _getattr_foreingkey(obj, field), list_display) for obj in objects]
    data = []
    for obj in cobros:
        row=map(lambda field: _getattr_foreingkey(obj, field), list_display)
        detalle_pago = Detalle_cobro.objects.filter(recibo=obj)
        det = ""
        for detalle in detalle_pago:
            det = det + "%s<br>" %detalle.venta 
        row.insert(3, det)
        ops = '<a class="imprimirRecibo" href="%s">IMPRIMIR</a>' %(reverse_lazy('imprimirRecibo',args=[obj.pk])) 
        row.append(ops)
        data.append(row)
        
    #set_trace()
    #define response
    response = {
        'data': data,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'draw': request.GET['draw']
    }

    #serialize to json
    s = StringIO()
    json.dump(response, s)
    s.seek(0)
    return HttpResponse(s.read())

def get_comprobantes_de_cliente(request,cliente):
    cliente = Cliente.objects.get(id=cliente)
    comprs = Venta.objects.filter(cliente=cliente,pagado=False)
    data = []
    for com in comprs:
        obj = {"id":com.id,"comprobante":"%s" %com}
        data.append(obj)
    s = StringIO()
    json.dump(data,s)
    s.seek(0)
    return HttpResponse(s.read())

def get_datos_defecto_cheque(request,cliente):
    cliente = Cliente.objects.get(id=cliente)
    defe={'razon_social':cliente.razon_social,'cuit':cliente.cuit,'paguese_a':RAZON_SOCIAL_EMPRESA,'fecha':datetime.date.today().strftime("%d/%m/%Y")}
    s = StringIO()
    json.dump(defe,s)
    s.seek(0)
    return HttpResponse(s.read())

def get_credito_valores(request,cliente):
    cliente = Cliente.objects.get(id=cliente)
    for rec in cliente.recibo_set.all():
        for valor in rec.dinero_set.all():
            try:
                if valor.pendiente_para_recibo > 0.009:
                    #obj = {'num_cheque':valor.chequetercero.numero, 'pendiente':'%.2f' %valor.chequetercero.pendiente_para_recibo}
                    obj = {'pendiente':'%.2f' %valor.pendiente_para_recibo}
                    s = StringIO()
                    json.dump(obj,s)
                    s.seek(0)
                    return HttpResponse(s.read())
            except Dinero.DoesNotExist:
                continue
    return HttpResponse()

def get_credito_valores_op(request,proveedor):
    proveedor = Proveedor.objects.get(id=proveedor)
    for op in proveedor.ordenpago_set.all():
        for valor in op.dinero_set.all():
            try:
                #if valor.chequetercero.pendiente_para_orden_pago > 0.009:
                if valor.pendiente_para_orden_pago > 0.009:
                    print valor.pendiente_para_orden_pago
                    obj = {'pendiente':'%.2f' %valor.pendiente_para_orden_pago}
                    s = StringIO()
                    json.dump(obj,s)
                    s.seek(0)
                    return HttpResponse(s.read())
            except Dinero.DoesNotExist:
                continue
    return HttpResponse()

def cliente_datatables_view(request):
    clientes = Cliente.objects.all()
    list_display = ['razon_social', 'telefono']
    list_filter = ['razon_social']

    # Cuenta total de articulos:
    recordsTotal = clientes.count()

    #Filtrado de los articulos
    search = request.GET['search[value]']
    queries = [Q(**{f+'__icontains' : search}) for f in list_filter]
    qs = reduce(lambda x, y: x|y, queries)
    clientes = clientes.filter(qs)

    #Ordenado
    #order = dict( enumerate(list_display) )
    #dirs = {'asc': '', 'desc': '-'}
    #ordering = dirs[request.GET['sSortDir_0']] + order[int(request.GET['iSortCol_0'])]
    #objects = objects.order_by(ordering)

    # Conteo de articulos despues dle filtrado
    recordsFiltered = clientes.count()


    # finally, slice according to length sent by dataTables:
    start = int(request.GET['start'])
    length = int(request.GET['length'])
    clientes = clientes[ start : (start+length)]
    
    # extract information
    #data = [map(lambda field: _getattr_foreingkey(obj, field), list_display) for obj in objects]
    data = []
    for obj in clientes:
        row=map(lambda field: _getattr_foreingkey(obj, field), list_display)
        direccion = obj.direccion+' - '+obj.localidad+' ('+obj.get_provincia_display()+')' 
        row.insert(1,direccion)
        #ops = '<a href="%s" class="btn btn-primary" role="button">EDITAR</a> <a href="%s" class="btn btn-danger" role="button">BORRAR</a>'\
        #        %(reverse_lazy('editarCliente',args=[obj.pk]),reverse_lazy('borrarCliente',args=[obj.pk])) 
        ops = '''<div class="btn-group">
                 <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                 Acciones <span class="caret"></span>
                 </button>
                 <ul class="dropdown-menu" role="menu">
                 <li><a href="%s">Editar</a></li>
                 <li><a href="%s">Suspender</a></li>
                 </ul>
                 </div>'''\
                 %(reverse_lazy('editarCliente',args=[obj.pk]),reverse_lazy('borrarCliente',args=[obj.pk]))
        detalle='''<u>CUIT</u>: <strong>%s</strong><br>
                   <u>Informacion fiscal</u>:  Condicion IVA: %s - IIBB: %s<br>
                   <u>Direccion</u>: %s, %s (%s) -- CP: %s<br>
                   <u>Contacto</u>:  TE: %s  FAX: %s<br>
                   </u>Informacion extra</u>:<br>
                   %s'''\
                   % (obj.cuit, obj.get_cond_iva_display(), obj.codigo_ingresos_brutos, obj.direccion,\
                      obj.localidad, obj.provincia, obj.codigo_postal, obj.telefono,\
                      obj.fax, obj.notas)
        row.insert(0, detalle)
        row.append(ops)
        data.append(row)
        

    #define response
    response = {
        'data': data,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'draw': request.GET['draw']
    }

    #serialize to json
    s = StringIO()
    json.dump(response, s)
    s.seek(0)
    return HttpResponse(s.read())

def proveedores_datatables_view(request):
    proveedores = Proveedor.objects.all()
    list_display = ['razon_social', 'telefono']#Para direccion uso varios campos, definido abajo
    list_filter = ['razon_social']

    # Cuenta total de articulos:
    recordsTotal = proveedores.count()

    #Filtrado de los articulos
    search = request.GET['search[value]']
    queries = [Q(**{f+'__icontains' : search}) for f in list_filter]
    qs = reduce(lambda x, y: x|y, queries)
    proveedores = proveedores.filter(qs)

    #Ordenado
    #order = dict( enumerate(list_display) )
    #dirs = {'asc': '', 'desc': '-'}
    #ordering = dirs[request.GET['sSortDir_0']] + order[int(request.GET['iSortCol_0'])]
    #objects = objects.order_by(ordering)

    # Conteo de articulos despues dle filtrado
    recordsFiltered = proveedores.count()


    # finally, slice according to length sent by dataTables:
    start = int(request.GET['start'])
    length = int(request.GET['length'])
    proveedores = proveedores[ start : (start+length)]
    
    # extract information
    #data = [map(lambda field: _getattr_foreingkey(obj, field), list_display) for obj in objects]
    data = []
    for obj in proveedores:
        row=map(lambda field: _getattr_foreingkey(obj, field), list_display)
        direccion = obj.direccion+' - '+obj.localidad+' ('+obj.provincia+')' 
        row.insert(1,direccion)        
        ops = '''<div class="btn-group">
                 <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                 Acciones <span class="caret"></span>
                 </button>
                 <ul class="dropdown-menu" role="menu">
                 <li><a href="%s">Editar</a></li>
                 <li><a href="%s">Suspender</a></li>
                 </ul>
                 </div>'''\
                 %(reverse_lazy('editarProveedor',args=[obj.pk]),reverse_lazy('borrarProveedor',args=[obj.pk]))
        detalle='''<u>CUIT</u>: <strong>%s</strong><br>
                   <u>Informacion fiscal</u>:  Condicion IVA: %s - IIBB: %s<br>
                   <u>Direccion</u>: %s, %s (%s) -- CP: %s<br>
                   <u>Contacto</u>:  TE: %s  FAX: %s  EMAIL:%s<br>
                   </u>Informacion extra</u>:<br>
                   %s'''\
                   % (obj.cuit, obj.condicion_iva, obj.codigo_ingresos_brutos, obj.direccion,\
                      obj.localidad, obj.provincia, obj.codigo_postal, obj.telefono,\
                      obj.fax, obj.email, obj.notas)
        row.insert(0, detalle)
        row.append(ops)
        data.append(row)
        

    #define response
    response = {
        'data': data,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'draw': request.GET['draw']
    }

    #serialize to json
    s = StringIO()
    json.dump(response, s)
    s.seek(0)
    return HttpResponse(s.read())

def cheques_datatables_view(request):
    tipo=request.GET['tipo']
    if tipo=='cartera':
        cols={1:'fecha',2:'numero',3:'cobro',4:'titular',5:'monto'}
        cheques = ChequeTercero.objects.all().filter(en_cartera=True)
        list_display = ['fecha','numero', 'cobro','titular','monto']
        list_filter = ['numero']
    elif tipo=='completo':
        cols={1:'fecha',2:'numero',3:'cobro',4:'titular',5:'monto'}
        cheques = ChequeTercero.objects.all()
        list_display = ['fecha','numero', 'cobro','titular','monto']
        list_filter = ['numero']
    # Cuenta total de articulos:
    recordsTotal = cheques.count()

    #Filtrado de los articulos
    search = request.GET['search[value]']
    queries = [Q(**{f+'__icontains' : search}) for f in list_filter]
    qs = reduce(lambda x, y: x|y, queries)
    cheques = cheques.filter(qs)

    #Ordenado
    #order = dict( enumerate(list_display) )
    dirs = {'asc': '', 'desc': '-'}
    ordering = dirs[request.GET['order[0][dir]']] + cols[int(request.GET['order[0][column]'])]
    cheques = cheques.order_by(ordering)

    # Conteo de articulos despues dle filtrado
    recordsFiltered = cheques.count()


    # finally, slice according to length sent by dataTables:
    start = int(request.GET['start'])
    length = int(request.GET['length'])
    cheques = cheques[ start : (start+length)]
    
    # extract information
    #data = [map(lambda field: _getattr_foreingkey(obj, field), list_display) for obj in objects]
    data = []
    for obj in cheques:
        row=map(lambda field: _getattr_foreingkey(obj, field), list_display) 
        if tipo=='completo':
            estado = 'En cartera' if obj.en_cartera else 'Entregado'
            row.append(estado)
            attr_disabled=''
            #attr_disabled='' if obj.en_cartera else 'disabled'
            #class_disabled=''
            class_disabled='' if obj.en_cartera else ' class="disabled"'
            ops = '''<div class="btn-group">
                     <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                     Acciones <span class="caret"></span>
                     </button>
                     <ul class="dropdown-menu" role="menu">
                     <li%s><a class="btn_quitar_de_cartera" data-id="%s" %s href="#">Quitar de cartera</a></li>
                     </ul>
                     </div>''' %(class_disabled,obj.id,attr_disabled)
            row.append(ops)
        detalle='''<u>CUIT</u>: <strong>%s</strong><br>
                   <u>Banco</u>: %s<br>
                   <u>Entregado por</u>: %s (%s)<br>
                   <u>Paguese a</u>: %s<br>
                   <u>Domiclio de pago</u>: %s<br>
                   <u>Observaciones</u>: %s<br>'''\
                   % ( obj.cuit_titular, obj.banco.nombre, obj.recibo.cliente, obj.recibo.numero_full, obj.paguese_a,\
                      obj.domicilio_de_pago, obj.observaciones if obj.observaciones else "N/A")
        row.insert(0, detalle)
        if tipo =='cartera':
            row.append(obj.id)
        data.append(row)


    #define response
    response = {
        'data': data,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'draw': request.GET['draw']
    }

    #serialize to json
    s = StringIO()
    json.dump(response, s)
    s.seek(0)
    return HttpResponse(s.read())

def cheques_propios_datatables_view(request):
    cols={1:'fecha',2:'numero',3:'cobro',4:'monto'}
    cheques = ChequePropio.objects.all()
    list_display = ['fecha','numero', 'cobro','monto']
    list_filter = ['numero']
    # Cuenta total de articulos:
    recordsTotal = cheques.count()

    #Filtrado de los articulos
    search = request.GET['search[value]']
    queries = [Q(**{f+'__icontains' : search}) for f in list_filter]
    qs = reduce(lambda x, y: x|y, queries)
    cheques = cheques.filter(qs)

    #Ordenado
    #order = dict( enumerate(list_display) )
    dirs = {'asc': '', 'desc': '-'}
    ordering = dirs[request.GET['order[0][dir]']] + cols[int(request.GET['order[0][column]'])]
    cheques = cheques.order_by(ordering)

    # Conteo de articulos despues dle filtrado
    recordsFiltered = cheques.count()


    # finally, slice according to length sent by dataTables:
    start = int(request.GET['start'])
    length = int(request.GET['length'])
    cheques = cheques[ start : (start+length)]

    # extract information
    #data = [map(lambda field: _getattr_foreingkey(obj, field), list_display) for obj in objects]
    data = []
    for obj in cheques:
        row=map(lambda field: _getattr_foreingkey(obj, field), list_display)
        detalle='''<u>Paguese a</u>: %s<br>
                   <u>Orden Pago</u>: %s<br>'''\
                   % ( obj.paguese_a, obj.orden_pago)
        row.insert(0, detalle)
        data.append(row)


    #define response
    response = {
        'data': data,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'draw': request.GET['draw']
    }

    #serialize to json
    s = StringIO()
    json.dump(response, s)
    s.seek(0)
    return HttpResponse(s.read())


def comp_compras_datatables_view(request):
    cols = {0:'fecha',1:'tipo',2:'identificador',3:'proveedor__razon_social',4:'neto',\
            5:'iva',6:'total',7:'estado'}
    comprobantes = Compra.objects.all()
    print (request.GET)
    for k,v in request.GET.iteritems():
        print "Key: %s - Value: %s" %(k,v)
    list_display = ['fecha', 'tipo','identificador','proveedor.razon_social','neto','iva','total','estado']
    list_filter = ['proveedor__razon_social', 'numero']

    # Cuenta total de articulos:
    recordsTotal = comprobantes.count()

    #Filtrado de los articulos
    search = request.GET['search[value]']
    queries = [Q(**{f+'__icontains' : search}) for f in list_filter]
    qs = reduce(lambda x, y: x|y, queries)
    comprobantes = comprobantes.filter(qs)

    #Ordenado
    #order = dict( enumerate(list_display) )
    dirs = {'asc': '', 'desc': '-'}
    ordering = dirs[request.GET['order[0][dir]']] + cols[int(request.GET['order[0][column]'])]
    comprobantes=comprobantes.order_by(ordering)

    # Conteo de articulos despues dle filtrado
    recordsFiltered = comprobantes.count()


    # finally, slice according to length sent by dataTables:
    start = int(request.GET['start'])
    length = int(request.GET['length'])
    comprobantes = comprobantes[ start : (start+length)]
    
    # extract information
    #data = [map(lambda field: _getattr_foreingkey(obj, field), list_display) for obj in objects]
    data = []
    for obj in comprobantes:
        row=map(lambda field: _getattr_foreingkey(obj, field), list_display)
        print row
        #detalles_venta_html = format_det_venta(obj.detalle_venta_set.all())
        #row.insert(0,detalles_venta_html)
        #ops = '<a class="imprimirComprobante" href="%s">IMPRIMIR</a>' %(reverse_lazy('imprimirComprobante',args=[obj.pk])) if obj.aprobado else "" 
        #row.append(ops)
        #Es un table (<table>..........</table>
        data.append(row)
        

    #define response
    response = {
        'data': data,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'draw': request.GET['draw']
    }

    #serialize to json
    s = StringIO()
    json.dump(response, s)
    s.seek(0)
    return HttpResponse(s.read())

def cheque_quitar_de_cartera(request):#Mandar id y observaciones en POST
    print "LALALALALALALALA"
    if request.POST:
        id_cheque = request.POST['id_cheque']
        observaciones = request.POST['observaciones']
        cheque = ChequeTercero.objects.get(id=id_cheque)
        cheque.observaciones = observaciones
        cheque.en_cartera=False
        cheque.save()
        #obj = {'id':recibo.id}
        #s = StringIO()
        #json.dump(obj,s)
        #s.seek(0)
        return HttpResponse()
    
def pagos_datatables_view(request):
    pagos = OrdenPago.objects.all()
    #Campos directos, personalizacion mas adelante
    list_display = ['fecha', 'numero_full','proveedor.razon_social','total_str']
    list_filter = ['numero', 'proveedor__razon_social']
    data_struct = {0: 'fecha', 1: 'numero', 2: 'proveedor__razon_social'}

    # Cuenta total de articulos:
    recordsTotal = pagos.count()

    #Filtrado de los articulos
    search = request.GET['search[value]']
    queries = [Q(**{f+'__icontains' : search}) for f in list_filter]
    qs = reduce(lambda x, y: x|y, queries)
    pagos = pagos.filter(qs)

    #Ordenado
    pagos = ordering(request.GET, pagos, data_struct)
    #order = dict( enumerate(list_display) )
    #dirs = {'asc': '', 'desc': '-'}
    #ordering = dirs[request.GET['sSortDir_0']] + order[int(request.GET['iSortCol_0'])]
    #objects = objects.order_by(ordering)

    # Conteo de articulos despues dle filtrado
    recordsFiltered = pagos.count()


    # finally, slice according to length sent by dataTables:
    start = int(request.GET['start'])
    length = int(request.GET['length'])
    pagos = pagos[ start : (start+length)]
    
    # extract information
    #data = [map(lambda field: _getattr_foreingkey(obj, field), list_display) for obj in objects]
    data = []
    for obj in pagos:
        row=map(lambda field: _getattr_foreingkey(obj, field), list_display)
        det = ""
        for detalle in obj.detalle_pago_set.all():
            det = det + "%s<br>" %detalle.compra 
        row.insert(3, det)
        val = ""
        for valor in obj.dinero_set.all():
            val = val + "%s<br>" %valor 
        row.insert(4, val)
        ops = '<a class="imprimirOrdenPago" href="%s">IMPRIMIR</a>' %(reverse_lazy('imprimirOrdenPago',args=[obj.pk])) 
        row.append(ops)
        data.append(row)
        
    #set_trace()
    #define response
    response = {
        'data': data,
        'recordsTotal': recordsTotal,
        'recordsFiltered': recordsFiltered,
        'draw': request.GET['draw']
    }

    #serialize to json
    s = StringIO()
    json.dump(response, s)
    s.seek(0)
    return HttpResponse(s.read())

def validar_comprobante_compra(request):
    numero = request.GET['numero']
    punto_venta = request.GET['punto_venta']
    tipo = request.GET['tipo_comprobante']
    proveedor = request.GET['proveedor']

    try:
        com = Compra.objects.get(numero=numero, punto_venta=punto_venta, tipo=tipo, proveedor__id=proveedor)
        print com
        if com:
            existe = True
        else:
            existe = False
    except Compra.DoesNotExist:
        existe = False
    print "Existe: %s" %existe
    obj = {'existe': existe}
    s = StringIO()
    json.dump(obj, s)
    s.seek(0)
    return HttpResponse(s.read())