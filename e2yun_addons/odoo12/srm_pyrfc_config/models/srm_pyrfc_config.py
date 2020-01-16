#!/usr/bin/python
# -*- coding: UTF-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _

try:
    from odoo.addons.srm_pyrfc import ZSRM_MM_BAPI_PO_GETDETAIL
    from odoo.addons.srm_pyrfc import get_pyrfc_conn
except :
    pass
from datetime import datetime
class srm_pyrfc_config(models.Model):
    _name = "srm.pyrfc.config"
    _table = 'srm_pyrfc_config'

    service_name = fields.Char('service_name')
    enabled = fields.Boolean('enabled', defatult=False)
    ret_purchase = fields.Boolean('ret purchase',defatult=False)
    user = fields.Char('user')
    passwd = fields.Char('passwd')
    ashost = fields.Char('ashost')
    sysnr = fields.Char('sysnr')
    client = fields.Char('client')
    saprouter = fields.Char('saprouter')
    lang = fields.Char('lang')

    def confirm_srm_pyrfc_config(self, cr, uid, ids, context=None):
        print(uid)
        #(self, cr, uid, vals, context=None):
        # vals={'name':'4500000013','picking_type_id': 1,'partner_id': 8,'company_id': 1,
        #     'odate': '2018-7-19',
        #     'payment_term_id': 1,
        #     'pricelist_id': 2,
        #     'group_id': 4,
        #     'location_id': 12 }
        # order_line=[]
        # taxes_id=[]
        # taxes_id.append((6, False, [2]))
        # order_line_map=(0,False,{
			# 'product_id': 3,
			# 'product_uom': 1,
			# 'date_planned':  '2018-7-18',
			# 'price_unit': 12.0,
			# 'taxes_id': taxes_id,
			# 'product_qty': 11222.0,
			# 'name': 'SMT FFC排插座 1.0/6P 立贴双面接/黑色'
        # })
        # order_line.append(order_line_map)
        # vals['order_line']=order_line

        bapi=ZSRM_MM_BAPI_PO_GETDETAIL.ZSRM_MM_BAPI_PO_GETDETAIL()
        IV_BEGIN = "20180720"
        IV_END = "20180810"
        result=bapi.BAPI_PO_GETDETAIL_GET(IV_BEGIN,IV_END)

        picking_type_id = ""
        location_id = ""  # 送货地址
        date_planned = ""  # 交货日期

        for posc in result['ET_POSCHEDULE']:
            # 交货日期 date_planned
            date_planned = posc['DELIVERY_DATE']

        for head in result['ET_POHEADER']:
            PO_NUMBER=""
            vals = {}
            order_line = []
            # 订单号 NAME
            PO_NUMBER=head['PO_NUMBER']
            vals['name'] =PO_NUMBER
            #验证是否已经导入
            if PO_NUMBER!="":
                sql = " select  id from purchase_order t where t.name='" + str(PO_NUMBER) + "' "
                cr.execute(sql)
                sql_result = cr.fetchone()
                if sql_result:
                    continue
            for item in result['ET_POITEM']:
                line_map_temp = {}
                if PO_NUMBER!=item['PO_NUMBER']:
                    continue
                plant = item['PLANT']  # 工厂
                if picking_type_id == "":
                    sql = "select t.pack_type_id,lot_stock_id from stock_warehouse t where factory_code='" + str(
                        plant) + "';"
                    cr.execute(sql)
                    sql_result = cr.fetchone()
                    picking_type_id = sql_result[0]
                    location_id = sql_result[1]
                # 产品代码
                if item['MATERIAL']:
                    sql = " select  id from product_product t where t.default_code='" + str(item['MATERIAL']) + "' "
                    cr.execute(sql)
                    sql_result = cr.fetchone()
                    line_map_temp['product_id'] = sql_result[0]

                # name 产品描述
                line_map_temp['name'] = item['MATERIAL'] + item['SHORT_TEXT']
                # 产品单位  product_uom

                # 产品代码
                if item['MATERIAL']:
                    sql = " select  id from product_uom t where t.name like'" + str(item['PO_UNIT']) + "%'  limit 1 "
                    cr.execute(sql)
                    sql_result = cr.fetchone()
                    line_map_temp['product_uom'] = sql_result[0]

                line_map_temp['item'] = item['PO_ITEM']
                line_map_temp['lgort'] = item['STGE_LOC']
                line_map_temp['werks'] = plant
                # 数量 product_qty
                line_map_temp['product_qty'] = item['QUANTITY']
                # 价格
                line_map_temp['price_unit'] = item['NET_PRICE']
                # 交货日期
                line_map_temp['date_planned'] = date_planned

                # taxes_id 税码
                taxes_id = []
                taxes_id.append((6, False, [2]))
                line_map_temp['taxes_id'] = taxes_id

                order_line_map = (0, False, line_map_temp)
                order_line.append(order_line_map)
            vals['picking_type_id'] = picking_type_id
            vals['location_id'] = location_id
            vals['payment_term_id'] = 1
            if head['VENDOR']:
                sql = " select  id from res_partner t where t.supplier_code='" + str(head['VENDOR']) + "' "
                cr.execute(sql)
                sql_result = cr.fetchone()
                vals['partner_id'] = sql_result[0]

            if head['COMP_CODE']:
                sql = " select   id  from res_company t where company_code= '" + str(head['COMP_CODE']) + "' "
                cr.execute(sql)
                sql_result = cr.fetchone()
                vals['company_id'] = sql_result[0]

            d1 = datetime.datetime.now()
            d3 = d1 + datetime.timedelta(days=+2)
            vals['odate'] = d3.strftime('%Y-%m-%d');

            if head['CURRENCY']:
                sql = "  select id from product_pricelist t where type='purchase'  limit 1 "
                cr.execute(sql)
                sql_result = cr.fetchone()
                vals['pricelist_id'] = sql_result[0]
            #验证是否有采购组 head['PUR_GROUP']
            vals['group_id'] = 4
            vals['order_line'] = order_line
            order_line = []
            self.pool.get('purchase.order').create(cr, uid, vals, context)

    # def create(self, cr, uid, vals, context=None):
    #     lid=super(srm_pyrfc_config, self).create(cr, uid, vals, context=context)
    #     return True
    def pyrfc_config_test(self,cr, uid, ids, context=None):
        # getconn = get_pyrfc_conn.get_pyrfc_conntion()
        # conn = getconn.get_conn(cr)
        # print(conn)
        # conn.close()
        for id in context['active_ids']:
            sql = "select * from srm_pyrfc_config where id=" + str(id) + ""
            cr.execute(sql)
            result = cr.dictfetchall()
            if result[0]['user'] == 'srmsqltest':
                cr.execute(result[0]['service_name'])

        sql="delete from srm_pyrfc_config  where service_name is null"
        cr.execute(sql)
