from boolean_app.models import Valores, ChequeTercero, Dinero
if __name__ == "__main__":
    chts=Valores.objects.filter(tipo='CHT')
    i=0
    for cht in chts:
        ChequeTercero.objects.create(recibo=cht.recibo,numero=cht.cheque_numero,banco=cht.cheque_banco,\
                                     fecha=cht.cheque_fecha,cobro=cht.cheque_cobro,titular=cht.cheque_titular,\
                                     cuit_titular=cht.cheque_cuit_titular,paguese_a=cht.cheque_paguese_a,\
                                     domicilio_de_pago=cht.cheque_domicilio_de_pago,en_cartera=cht.cheque_en_cartera,\
                                     monto=cht.monto, pendiente_para_recibo=cht.pendiente_para_recibo)
        i+=1
        print i
    efepo=Valores.objects.filter(tipo='EFE')
    i=0
    for efe in efepo:
        Dinero.objects.create(recibo=efe.recibo,monto=efe.monto)
        i+=1
        print i