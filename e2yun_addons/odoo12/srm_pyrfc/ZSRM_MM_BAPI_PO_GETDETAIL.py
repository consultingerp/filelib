#!/usr/bin/python
# -*- coding: UTF-8 -*-
try:
    from odoo.addons.srm_pyrfc import  get_pyrfc_conn
    import pyrfc
except BaseException as b:
    print(b)
    #pass
import importlib,sys
from odoo import exceptions

class ZSRM_MM_BAPI_PO_GETDETAIL():

    def BAPI_PO_GETDETAIL_GET(self,cr,IV_BEGIN,IV_END,EBELN,IV_QC):
        try:
            importlib.reload(sys)
            conn=""
            try:
                getconn = get_pyrfc_conn.get_pyrfc_conntion()
            except BaseException as b:
                raise exceptions.ValidationError("初始化引用包"+str(b))
            try:
                conn = getconn.get_conn(cr)
            except BaseException as b:
                raise exceptions.ValidationError("初始化SAP链接error"+str(b))

            result=""
            if len(EBELN)>0:
                result = conn.call('ZSRM_MM_BAPI_PO_GETDETAIL',IT_EBELN=EBELN,IV_QC=IV_QC)
                return result
            if not IV_BEGIN==" " and not IV_END==" ":
                result = conn.call('ZSRM_MM_BAPI_PO_GETDETAIL',IV_BEGIN=IV_BEGIN, IV_END=IV_END,IV_QC=IV_QC)
                return result
        except BaseException as b:
            raise  exceptions.ValidationError(b)
            pass
        finally:
            if conn:
                conn.close()
# try:
#     test=ZSRM_MM_BAPI_PO_GETDETAIL()
#     IV_BEGIN = "20180720"
#     IV_END = "20180810"
#     result=test.BAPI_PO_GETDETAIL_GET("","","1008527")
#
#     for head in result['ET_POHEADER']:
#     # 订单号 NAME
#            print(head['PO_NUMBER'])
#
#     picking_type_id=""
#     location_id=""  #送货地址
#     date_planned="" #交货日期
#     plant="" #工厂
# except Exception as err:
# 	print(err)

#
#     conn = psycopg2.connect(database='srm',user='openpg',password='openpgpwd',host='localhost',port='5432')
#     cur = conn.cursor()
#
#     for posc in result['ET_POSCHEDULE']:
#          #交货日期 date_planned
#          date_planned=posc['DELIVERY_DATE']
#
#     vals={}
#     order_line = []
#     for item in result['ET_POITEM']:
#         line_map_temp = {}
#         plant=item['PLANT']  # 工厂
#         if picking_type_id=="":
#             sql="select t.pack_type_id,lot_stock_id from stock_warehouse t where factory_code='"+str(plant)+"';"
#             cur.execute(sql)
#             sql_result = cur.fetchone()
#             picking_type_id=sql_result[0]
#             location_id=sql_result[1]
#
#         #产品代码
#         if item[ 'MATERIAL']:
#          sql=" select  id from product_product t where t.default_code='"+str(item[ 'MATERIAL'])+"' "
#          cur.execute(sql)
#          sql_result = cur.fetchone()
#          line_map_temp['product_id'] =sql_result[0]
#
#         line_map_temp['item'] = item['PO_ITEM']
#         line_map_temp['lgort'] = item['STGE_LOC']
#         line_map_temp['werks'] = plant
#         #name 产品描述
#         line_map_temp['name'] = item['MATERIAL']+item['SHORT_TEXT']
#         #产品单位  product_uom
#         line_map_temp['product_uom']=item['PO_UNIT']
#         #数量 product_qty
#         line_map_temp['product_qty'] = item['QUANTITY']
#         #价格
#         line_map_temp['price_unit'] = item['NET_PRICE']
#         #交货日期
#         line_map_temp['date_planned'] =date_planned
#
#         # taxes_id 税码
#         taxes_id=[]
#         taxes_id.append((6, False, [2]))
#         line_map_temp['taxes_id'] =taxes_id
#
#         order_line_map = (0, False,line_map_temp)
#         order_line.append(order_line_map)
#
#
#     for head in result['ET_POHEADER']:
#         # 订单号 NAME
#         vals['name']=head['PO_NUMBER']
#         vals['picking_type_id'] = picking_type_id
#         vals['location_id'] = location_id
#         vals['payment_term_id']=1
#         if head[ 'VENDOR']:
#          sql=" select  id from res_partner t where t.supplier_code='"+str(head[ 'VENDOR'])+"' "
#          cur.execute(sql)
#          sql_result = cur.fetchone()
#          vals['partner_id'] =sql_result[0]
#
#         if head['COMP_CODE']:
#           sql = " select   id  from res_company t where company_code= '" + str(head['COMP_CODE']) + "' "
#           cur.execute(sql)
#           sql_result = cur.fetchone()
#           vals['company_id'] = sql_result[0]
#
#         d1 = datetime.datetime.now()
#         d3 = d1 + datetime.timedelta(days=+2)
#         vals['odate']=d3.strftime('%Y-%m-%d');
#
#         if head['CURRENCY']:
#           sql = "  select id from product_pricelist t where type='purchase'  limit 1 "
#           cur.execute(sql)
#           sql_result = cur.fetchone()
#           vals['pricelist_id'] = sql_result[0]
#         vals['group_id'] = head['PUR_GROUP']
#         vals['order_line'] = order_line
#     print(vals)
#     conn.commit()
#     cur.close()
#     conn.close()
#
# except Exception as err:
# 	print(err)


#print(result['ET_POITEM'])





