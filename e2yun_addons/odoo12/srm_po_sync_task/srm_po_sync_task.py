#!/usr/bin/python
# -*- coding: UTF-8 -*-
from odoo import api, fields, models, exceptions, _

try:
    from odoo.addons.srm_pyrfc import ZSRM_MM_BAPI_PO_GETDETAIL
except:
    pass
import datetime
import time
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError
class srm_po_sync_task(models.Model):
    _name = "srm.po.sync.task"
    _description = "srm_po_sync_task"

    def srm_po_sync_task_m(self,IV_BEGIN,IV_END,EBELNS,IV_QC,context=None):

        cr=self._cr
        uid=self._uid
        order_confim=False  #是否自动确认
        auto_send_email=False   #是否发送邮件
        bapi=ZSRM_MM_BAPI_PO_GETDETAIL.ZSRM_MM_BAPI_PO_GETDETAIL()
        IV_BEGIN_TEMP = datetime.datetime.now()
        temps =IV_BEGIN_TEMP.strftime('%Y%m%d')
        tempe = IV_BEGIN_TEMP + datetime.timedelta(days=+2)
        tempe=tempe.strftime('%Y%m%d')


        sql = "SELECT ret_purchase  FROM srm_pyrfc_config t where enabled='t' "
        cr.execute(sql)
        ret_purchase_flag = cr.fetchone()
        if IV_BEGIN=='':
            IV_BEGIN=temps
        else:
            try:
                datetime.datetime.strptime(IV_BEGIN,'%Y%m%d')
            except:
                raise exceptions.ValidationError(IV_BEGIN+'格式不正确')

        if IV_END=='':
            IV_END =tempe
        else:
            try:
                datetime.datetime.strptime(IV_BEGIN, '%Y%m%d')
            except:
                raise exceptions.ValidationError(IV_BEGIN + '格式不正确')
        EBELNS_T=[]
        for ebeln in EBELNS:
            ebeln_m={'EBELN':ebeln}
            EBELNS_T.append(ebeln_m)

        result=bapi.BAPI_PO_GETDETAIL_GET(cr,str(IV_BEGIN),str(IV_END),EBELNS_T,IV_QC)
        picking_type_id = ""
        location_id = ""  # 送货地址

        ET_POSCHEDULE={}
        if not result:
            return
        for posc in result['ET_POSCHEDULE']:
            # 交货日期 date_planned
            ET_POSCHEDULE[posc['PO_NUMBER']+posc['PO_ITEM']]= posc['DELIVERY_DATE']

        for head in result['ET_POHEADER']:
            PO_NUMBER=""
            IS_EXCEPTIONS=False  #记录是否有异常
            vals = {}
            order_line = []
            isCreate=True
            update_id=""


            # 订单号 NAME
            PO_NUMBER=head['PO_NUMBER']

            #判断订单号类型
            sap_order_type=PO_NUMBER[0:2]
            if sap_order_type=='99':
                vals['sap_order_type']='采购退补料合同'


            vals['name'] =PO_NUMBER
            vals['date_order'] = head['DOC_DATE']
            if head['DOC_DATE']:
                temp = datetime.datetime.strptime(head['DOC_DATE'], '%Y%m%d')
                vals['date_order1'] =str(temp.year) + "." + str(temp.month) + "." + str(temp.day)
            else:
                vals['date_order1']=head['DOC_DATE']
            updatetime_sap = time.strptime(head['UDATE']+head['UTIME'], "%Y%m%d%H%M%S")
            updatetime_sap_str=str(updatetime_sap.tm_year)+'-'+str(updatetime_sap.tm_mon)+'-'+str(updatetime_sap.tm_mday)+' '+str(updatetime_sap.tm_hour)+':'+str(updatetime_sap.tm_min)+':'+str(updatetime_sap.tm_sec)
            vals['updatetime_sap']=updatetime_sap_str

            #验证是否已经导入
            if PO_NUMBER!="":
                sql = " select  id,updatetime_sap from purchase_order t where t.name='" + str(PO_NUMBER) + "' "
                cr.execute(sql)
                sql_result = cr.fetchone()
                if sql_result:
                    isCreate = False
                    #如果已导入，验证是否修改过，执行修改函数
                    if sql_result[1]:
                         update_id=sql_result[0]
                         updatetime_sap0=time.strptime(sql_result[1].replace('-', '').replace(':', '').replace(' ', ''), "%Y%m%d%H%M%S")
                         isUpdate=int(time.strftime("%Y%m%d%H%M%S", updatetime_sap0)) - int(time.strftime("%Y%m%d%H%M%S", updatetime_sap))
                         if isUpdate==0:
                            continue
            SAP_AMOUNT_UNTAXED =0  # 总计不含税
            SAP_AMOUNT_TOTAL =0  # 总值含税
            SAP_AMOUNT_TAX =0  # 税额

            for item in result['ET_POITEM']:
                line_map_temp = {}
                if PO_NUMBER!=item['PO_NUMBER']:
                    continue
                plant = item['PLANT']  # 工厂
                if  item['ITEM_CAT']=='3':
                    line_map_temp['item_cat'] = 't'
                    # 采购订单行项目组件
                    component = {}
                    component['po_number'] = PO_NUMBER
                    component['po_item'] = item['PO_ITEM']
                    component['name']=PO_NUMBER+"-"+item['PO_ITEM']

                    component_lines = []
                    for components in result['ET_POCOMPONENTS']:
                        if components['PO_NUMBER'] ==PO_NUMBER and components['PO_ITEM']==item['PO_ITEM']:
                            component_line_add=[0,False]
                            component_line={}
                            component_line['po_number']=components['PO_NUMBER']
                            component_line ['po_item']=components['PO_ITEM']
                            component_line['material']=components['MATERIAL']
                            component_line ['entry_quantity']=components['ENTRY_QUANTITY']
                            component_line['entry_uom']=components['ENTRY_UOM']
                            component_line['plant']=components['PLANT']
                            component_line_add.append(component_line)
                            component_lines.append(component_line_add)
                            component['purchase_component_line']=component_lines

                    if component:
                      component_id= self.env['purchase.component'].create(component)
                      line_map_temp['component_id'] =component_id.id

                if item['NO_MORE_GR']:
                    line_map_temp['no_more_gr']=item['NO_MORE_GR']

                #退货项目
                if item['RET_ITEM']:
                   if ret_purchase_flag and ret_purchase_flag[0]==True:
                         line_map_temp['ret_item']='t'
                         # 退貨161
                         sql = "select ID  from stock_picking_type where move_type='161'"
                         cr.execute(sql)
                         ret_picking_type_id_sql = cr.fetchone()
                         if ret_picking_type_id_sql:
                             picking_type_id = ret_picking_type_id_sql[0]
                   else:
                       continue

                if picking_type_id == "":
                    sql = "select t.in_type_id,lot_stock_id from stock_warehouse t where factory_code='" + str(
                        plant) + "';"
                    cr.execute(sql)
                    sql_result = cr.fetchone()
                    if sql_result:
                     picking_type_id = sql_result[0]
                     location_id = sql_result[1]
                # 产品代码
                if item['MATERIAL']:
                    sql = " select  id from product_product t where t.default_code='" + str(item['MATERIAL']) + "' "
                    cr.execute(sql)
                    sql_result = cr.fetchone()
                    if sql_result:
                        line_map_temp['product_id'] = sql_result[0]
                    else:
                        IS_EXCEPTIONS=True
                        if IV_QC == 'MENU':
                            raise ValidationError('SAP物料未匹配到'+str(item['MATERIAL']))
                        continue

                # name 产品描述
                line_map_temp['name'] = item['MATERIAL'] + item['SHORT_TEXT']

                # 产品单位  product_uom
                if item['PO_UNIT']:
                    sql = " select  id from product_uom t where t.name like'" + str(item['PO_UNIT']) + "'  limit 1 "
                    cr.execute(sql)
                    sql_result = cr.fetchone()
                    if sql_result:
                        line_map_temp['product_uom'] = sql_result[0]
                    else:
                        if IV_QC == 'MENU':
                            raise ValidationError('SAP单位未匹配到' + str(item['PO_UNIT']))
                        continue

                line_map_temp['item'] = item['PO_ITEM']

                line_map_temp['lgort'] = item['STGE_LOC']
                line_map_temp['werks'] = plant
                # 数量 product_qty
                line_map_temp['product_qty'] = item['QUANTITY']

                line_map_temp['sap_product_qty'] = int(item['QUANTITY'])

                # 交货日期
                line_map_temp['date_planned'] = ET_POSCHEDULE[item['PO_NUMBER']+item['PO_ITEM']]

                # taxes_id 税码
                taxes_id = []
                #税率
                tax_rate=0
                sql = " select id,amount from account_tax t where t.name='"+str(item['TAX_CODE'])+"' AND  t.type_tax_use='" + str('purchase') + "' limit 1 "
                cr.execute(sql)
                sql_result = cr.fetchone()
                if sql_result:
                 taxes_id.append((6, False, [sql_result[0]]))
                 tax_rate=sql_result[1]
                line_map_temp['taxes_id'] = taxes_id
                order_line_map = (0, False, line_map_temp)

                if item['NET_PRICE'] and item['PRICE_UNIT'] and item['DELETE_IND']!='L':

                    price_unit=float(item['NET_PRICE']) / float(item['PRICE_UNIT'])
                    NET_PRICE_TEMP=round(price_unit*float(item['QUANTITY']),5)
                    NET_PRICE=round(NET_PRICE_TEMP,5)
                    # 单价
                    #line_map_temp['price_unit'] =price_unit
                    price_unit_tmep=round(price_unit*tax_rate+price_unit,5)

                    #line_map_temp['price_unit'] =self.get_two_float(price_unit_tmep,2)

                    line_map_temp['price_unit'] =price_unit
                    #含税单价
                    line_map_temp['sap_price_unit'] =price_unit_tmep

                    SAP_AMOUNT_UNTAXED=SAP_AMOUNT_UNTAXED+NET_PRICE
                    line_map_temp['sap_amount_qty'] =round(NET_PRICE_TEMP*tax_rate+NET_PRICE_TEMP,2)
                    SAP_AMOUNT_TOTAL =SAP_AMOUNT_TOTAL+line_map_temp['sap_amount_qty']
                if isCreate != True:
                    line_map_temp['DELETE_IND'] = item['DELETE_IND']
                if update_id!="":
                    line_map_temp['order_id']=update_id
                    #修改读取数据
                    sql="select id from purchase_order_line where order_id="+str(update_id)+" and item='"+str(item['PO_ITEM'])+"'"
                    cr.execute(sql)
                    sql_result = cr.fetchone()
                    if sql_result:
                        line_map_temp['id']=sql_result[0];
                    else:
                        line_map_temp['id'] =""


                if isCreate==True:
                    # 创建的排除，排除删除数据
                    if not item['DELETE_IND'] == 'L':
                        order_line.append(order_line_map)
                else:
                    order_line.append(order_line_map)


            #有部分物料不存在，整张单不同步
            if IS_EXCEPTIONS==True:
                continue

            vals['picking_type_id'] = picking_type_id
            vals['location_id'] = location_id


            if head['PMNTTRMS']:
                sql = " select   id  from account_payment_term t where name= '" + str(head['PMNTTRMS']) + "' "
                cr.execute(sql)
                sql_result = cr.fetchone()
                if sql_result:
                    vals['payment_term_id']=sql_result[0]

            if head['VENDOR']:

                sql = " select  id,auto_send_email,order_confirm from res_partner t where t.supplier_code='" + str(head['VENDOR']) + "' and t.supplier='True' "
                cr.execute(sql)
                sql_result = cr.fetchone()
                if sql_result:
                  vals['partner_id'] = sql_result[0]
                  if sql_result[1]:
                      order_confim=sql_result[1] #是否自动确认

                  if sql_result[2]:
                      auto_send_email = sql_result[2]  # 是否发送邮件
                else:
                  if IV_QC=='MENU':
                       raise  ValidationError('供应商未匹配' + str(head['VENDOR']))
                  continue



            if head['COMP_CODE']:
                sql = " select   id  from res_company t where company_code= '" + str(head['COMP_CODE']) + "' "
                cr.execute(sql)
                sql_result = cr.fetchone()
                if sql_result:
                  vals['company_id'] = sql_result[0]

            d1 = datetime.datetime.now()
            d3 = d1 + datetime.timedelta(days=+2)
            vals['odate'] = d3.strftime('%Y-%m-%d');

            # if head['CURRENCY']:
            #     sql = "  select id from product_pricelist t where type='purchase'  and name='"+head['CURRENCY']+"'  limit 1 "
            #     cr.execute(sql)
            #     sql_result = cr.fetchone()
            #     if sql_result:
            #         vals['pricelist_id'] = sql_result[0]
            #验证是否有采购组 head['PUR_GROUP']
            vals['group_id']=""
            if head['PUR_GROUP']:
                sql = "  select id from product_category t where group_id='"+str(head['PUR_GROUP'])+"'  limit 1 "
                cr.execute(sql)
                sql_result = cr.fetchone()
                if sql_result:
                    vals['group_id'] = sql_result[0]

            vals['order_line'] = order_line

            #SAP_AMOUNT_UNTAXED =round(SAP_AMOUNT_UNTAXED,2)  # 总计不含税
            SAP_AMOUNT_TOTAL=round(SAP_AMOUNT_TOTAL,2)
            SAP_AMOUNT_UNTAXED=round(SAP_AMOUNT_UNTAXED,2)
            SAP_AMOUNT_TAX =SAP_AMOUNT_TOTAL-SAP_AMOUNT_UNTAXED  # 税额

            #SAP_AMOUNT_TAX=round(SAP_AMOUNT_TAX,2)
            #SAP_AMOUNT_TOTAL =SAP_AMOUNT_UNTAXED+SAP_AMOUNT_TAX  # 总值含税
            #SAP_AMOUNT_TOTAL=round(SAP_AMOUNT_TOTAL,2)

            vals['sap_amount_untaxed']=SAP_AMOUNT_UNTAXED
            vals['sap_amount_tax'] =SAP_AMOUNT_TAX
            vals['sap_amount_total'] =SAP_AMOUNT_TOTAL

            if head['CREATED_BY']:
                sql = "  select id from res_users t where login='" + str(head['CREATED_BY']) + "'  limit 1 "
                cr.execute(sql)
                sql_result = cr.fetchone()
                if sql_result:
                    vals['create_uid']=sql_result[0]
                    uid=sql_result[0]

            if isCreate==True:
                if  'order_line' in vals.keys() and len(vals['order_line'])>0:
                    if auto_send_email == True:
                        vals['email_supplier'] = True
                    group_id_order=vals['group_id']
                    del vals['group_id']
                    order=self.env['purchase.order'].create(vals)
                    sql="update purchase_order set amount_untaxed="+str(SAP_AMOUNT_UNTAXED)+",amount_tax="+str(SAP_AMOUNT_TAX)+",amount_total="+str(SAP_AMOUNT_TOTAL)+" where id="+str(order.id)+" "
                    cr.execute(sql)

                    ids = []
                    ids.append(order.id)
                    state = 'approved'
                    if auto_send_email==True and order_confim==True:
                        # 发送邮件
                        try:
                            self.send_email_lifnr(cr, uid, ids)
                        except BaseException as e:
                            raise exceptions.ValidationError(e)
                    else:
                        state = "supply_confirm"
                    if order_confim==True:
                         #确认订单
                         #self.srm_wkf_confirm_order(cr,uid,ids,state,context)
                         order.button_approve()
            else:
                if False:
                #if update_id!="":
                    sql="update purchase_order set updatetime_sap='"+str(updatetime_sap_str)+"'"
                    if not vals['group_id']=="":
                        sql+=",group_id='"+str(vals['group_id'])+"'"
                    sql +=" where id="+str(update_id)+"";
                    cr.execute(sql)
                    order = self.pool.get('purchase.order').browse(cr, uid, [update_id], context)
                    stock_move = self.pool.get('stock.move')

                    number_updates_exception=False
                    for u_line in order_line:
                        orderline=self.pool.get('purchase.order.line').browse(cr, uid, [u_line[2]['id']], context)
                        stock_move_id=""
                        if orderline.id and order.state != 'draft':
                            if float(u_line[2]['product_qty']) < float(orderline.delivery_qty):
                                number_updates_exception=True
                                if IV_QC == 'MENU':
                                    raise exceptions.ValidationError('订单行项目数量更新异常')
                                break


                        if orderline.ret_item and u_line[2]['id']:
                            #退貨行
                            sql = "select m.id,m.state,m.picking_id from stock_move m LEFT JOIN stock_location l  on m.location_dest_id=l.id  where m.origin='" + str(
                                PO_NUMBER) + "' and m.purchase_line_id='" + str(u_line[2][
                                                                                    'id']) + "' and l.usage='supplier' and m.state<>'done' and m.state<>'cancel' ORDER BY m.id DESC LIMIT 1  "
                            cr.execute(sql)
                            stock_move_id = cr.fetchone()

                        elif u_line[2]['id']:
                           sql = "select m.id,m.state,m.picking_id from stock_move m LEFT JOIN stock_location l  on m.location_dest_id=l.id  where m.origin='" + str(
                                    PO_NUMBER) + "' and m.purchase_line_id='" + str(u_line[2]['id']) + "' and l.usage='internal' and m.state<>'done' and m.state<>'cancel' ORDER BY m.id DESC LIMIT 1  "
                           cr.execute(sql)
                           stock_move_id = cr.fetchone()


                        # 退货行项目修改为正常收货项目，执行删除，重新生成作业号
                        if u_line[2]['id'] and  \
                                (('ret_item' in u_line[2].keys() and not orderline.ret_item )
                                 or (orderline.ret_item and 'ret_item' not in u_line[2].keys())) :
                             sql = "delete from purchase_order_line where id=" + str(u_line[2]['id']) + ""
                             cr.execute(sql)
                             if stock_move_id:
                               sql = "delete from stock_move where id =" + str(stock_move_id[0]) + ""
                               cr.execute(sql)
                             u_line[2]['id']=''

                        if u_line[2]['DELETE_IND']=='L' and u_line[2]['id']!="":

                            sql = "SELECT SUM(case when d.state in ('supplier_create','print') then menge else done_menge end) FROM delivery_order_line dl  "
                            sql += "  INNER JOIN delivery_order d on d.id=dl.delivery_order_id  "
                            sql += "  INNER JOIN delivery_purchase_orders p on delivery_order_line_id = dl.id     "
                            sql += "  where  d.state in ('supplier_create','print','Finished') AND p.pline=" + str(
                                u_line[2]['id']) + " "
                            cr.execute(sql)
                            delivery_result = cr.fetchone()
                            if delivery_result and delivery_result[0] >0:
                                number_updates_exception = True
                                if IV_QC == 'MENU':
                                    raise ValidationError('删除异常，PO行已关联交货单')
                                break
                            else:
                                if delivery_result:
                                    sql = "update purchase_order_line set product_qty=0,the_po=0 where id=" + str(
                                        u_line[2]['id']) + ""
                                    cr.execute(sql)
                                else:
                                    sql="delete from purchase_order_line where id="+str(u_line[2]['id'])+""
                                    cr.execute(sql)
                            #删除行项目的作业号
                            if stock_move_id:
                                 sql="delete from stock_move where id ="+str(stock_move_id[0])+""
                                 cr.execute(sql)
                            continue

                        if u_line[2]['id']!="" and u_line[2]['DELETE_IND']!='L':
                            del u_line[2]['DELETE_IND']
                            sql = "SELECT SUM(case when d.state in ('supplier_create','print') then menge else done_menge end) FROM delivery_order_line dl  "
                            sql+=        "  INNER JOIN delivery_order d on d.id=dl.delivery_order_id  "
                            sql +=       "  INNER JOIN delivery_purchase_orders p on delivery_order_line_id = dl.id     "
                            sql +=        "  where  d.state in ('supplier_create','print','Finished') AND p.pline="+str(u_line[2]['id'])+" "
                            cr.execute(sql)
                            delivery_result = cr.fetchone()
                            if delivery_result and delivery_result[0]>u_line[2]['product_qty']:
                                number_updates_exception = True
                                if IV_QC == 'MENU':
                                    raise ValidationError('更新异常，PO数量小于交货单数量')
                                break
                            if order.state != 'draft' \
                                    and (u_line[2]['product_qty'] != orderline.product_qty or u_line[2]['product_id'] != orderline.product_id.id):
                               self.pool.get('purchase.order.line').write_sync(cr, uid, [u_line[2]['id']], u_line[2], context)
                               # 更新作业号
                               qty_tmep=float(u_line[2]['product_qty'])
                               if orderline.delivery_qty:
                                   qty_tmep = float(u_line[2]['product_qty']) - float(orderline.delivery_qty)
                               if stock_move_id and stock_move_id[0]:
                                   update_stock_move_val = {}
                                   update_stock_move_val['product_uom_qty'] = qty_tmep
                                   update_stock_move_val['product_uos_qty'] = qty_tmep
                                   update_stock_move_val['product_id'] = u_line[2]['product_id']
                                   stock_move.write(cr, uid, stock_move_id[0], update_stock_move_val, context)
                               else:
                                   ret_picking_type_id= order.picking_type_id.id
                                   if order_line.ret_item:
                                       # 退貨161
                                       sql = "select ID  from stock_picking_type where move_type='161'"
                                       cr.execute(sql)
                                       ret_picking_type_id_sql = cr.fetchone()
                                       if ret_picking_type_id_sql:
                                           ret_picking_type_id = ret_picking_type_id_sql[0]
                                   picking_vals = {}
                                   picking_vals['origin'] = PO_NUMBER
                                   picking_vals['partner_id'] = order.partner_id.id
                                   picking_vals['picking_type_id'] =ret_picking_type_id
                                   picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals,
                                                                                      context=context)
                                   orderline = self.pool.get('purchase.order.line').browse(cr, uid, [u_line[2]['id']],
                                                                                           context)
                                   todo_moves = []
                                   new_group = self.pool.get("procurement.group").create(cr, uid, {'name': order.name,
                                                                                                   'partner_id': order.partner_id.id},
                                                                                         context=context)
                                   product_qty_temp = orderline.product_qty
                                   orderline.product_qty = qty_tmep

                                   if order_line.ret_item :
                                       for create_stock_move_val in self.pool.get('purchase.order')._prepare_order_line_move_ref(cr, uid, order,
                                                                                                   orderline,
                                                                                                   picking_id,
                                                                                                   new_group,
                                                                                                   context=context):
                                            move = stock_move.create(cr, uid, create_stock_move_val, context=context)
                                            todo_moves.append(move)
                                   else:
                                        for create_stock_move_val in self._prepare_order_line_move(cr, uid, order,
                                                                                                   orderline,
                                                                                                   picking_id,
                                                                                                   new_group,
                                                                                                   context=context):
                                            move = stock_move.create(cr, uid, create_stock_move_val, context=context)
                                            todo_moves.append(move)
                                   todo_moves = stock_move.action_confirm(cr, uid, todo_moves)
                                   stock_move.force_assign(cr, uid, todo_moves)
                                   orderline.product_qty = product_qty_temp
                            else:
                               self.pool.get('purchase.order.line').write_sync(cr, uid, [u_line[2]['id']], u_line[2], context)
                            continue
                        elif u_line[2]['id']=="" and u_line[2]['DELETE_IND']!='L' :
                            del u_line[2]['DELETE_IND']
                            picking_id=""
                            #退货行项目处理
                            if 'ret_item' in u_line[2].keys() and  u_line[2]['ret_item']=='t':
                                sql = "select m.picking_id from stock_move m LEFT JOIN stock_location l  on m.location_dest_id=l.id  where m.origin='" + str(
                                    PO_NUMBER) + "' and l.usage='supplier' and m.state<>'done' and m.state<>'cancel' ORDER BY m.id DESC LIMIT 1  "
                                cr.execute(sql)
                                stock_picking_id = cr.fetchone()
                            else:
                                sql = "select m.picking_id from stock_move m LEFT JOIN stock_location l  on m.location_dest_id=l.id  where m.origin='" + str(
                                    PO_NUMBER) + "' and l.usage='internal' and m.state<>'done' and m.state<>'cancel' ORDER BY m.id DESC LIMIT 1  "
                                cr.execute(sql)
                                stock_picking_id = cr.fetchone()

                            if stock_picking_id:
                                picking_id=stock_picking_id[0]
                            line_id=self.pool.get('purchase.order.line').create(cr, uid,u_line[2], context)
                            orderline = self.pool.get('purchase.order.line').browse(cr, uid, [line_id],   context)
                            if picking_id!="":
                             todo_moves = []
                             new_group = self.pool.get("procurement.group").create(cr, uid, {'name': order.name,
                                                                                             'partner_id': order.partner_id.id},
                                                                                   context=context)

                             if 'ret_item' in u_line[2].keys() and  u_line[2]['ret_item']=='t':
                                 for create_stock_move_val in self.pool.get('purchase.order')._prepare_order_line_move_ref(cr, uid, order, orderline, picking_id,
                                                                             new_group, context=context):
                                     move = stock_move.create(cr, uid, create_stock_move_val, context=context)
                                     todo_moves.append(move)
                             else:
                                 for create_stock_move_val in self._prepare_order_line_move(cr, uid, order, orderline, picking_id,
                                                                             new_group, context=context):
                                     move = stock_move.create(cr, uid, create_stock_move_val, context=context)
                                     todo_moves.append(move)
                             #创建作业号
                             todo_moves = stock_move.action_confirm(cr, uid, todo_moves)
                             stock_move.force_assign(cr, uid, todo_moves)
                            else:
                                ret_picking_type_id = order.picking_type_id.id
                                if 'ret_item' in u_line[2].keys() and u_line[2]['ret_item'] == 't':
                                    # 退貨161
                                    sql = "select ID  from stock_picking_type where move_type='161'"
                                    cr.execute(sql)
                                    ret_picking_type_id_sql = cr.fetchone()
                                    if ret_picking_type_id_sql:
                                        ret_picking_type_id = ret_picking_type_id_sql[0]

                                picking_vals = {}
                                picking_vals['origin'] = PO_NUMBER
                                picking_vals['partner_id'] = order.partner_id.id
                                picking_vals['picking_type_id'] = ret_picking_type_id

                                picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals,
                                                                                   context=context)
                                todo_moves = []
                                new_group = self.pool.get("procurement.group").create(cr, uid, {'name': order.name,
                                                                                                'partner_id': order.partner_id.id},
                                                                                      context=context)

                                if 'ret_item' in u_line[2].keys() and  u_line[2]['ret_item']=='t':
                                    for create_stock_move_val in self.pool.get('purchase.order')._prepare_order_line_move_ref(cr, uid, order,
                                                                                           orderline,
                                                                                           picking_id,
                                                                                           new_group,
                                                                                           context=context):
                                        move = stock_move.create(cr, uid, create_stock_move_val, context=context)
                                        todo_moves.append(move)
                                else:
                                    for create_stock_move_val in self._prepare_order_line_move(cr, uid, order,
                                                                                               orderline,
                                                                                               picking_id,
                                                                                               new_group,
                                                                                               context=context):
                                        move = stock_move.create(cr, uid, create_stock_move_val, context=context)
                                        todo_moves.append(move)
                                todo_moves = stock_move.action_confirm(cr, uid, todo_moves)
                                stock_move.force_assign(cr, uid, todo_moves)

                    if number_updates_exception:
                        #订单行项目更新异常，执行完成
                        continue
                    if order.state != 'draft' :
                        if auto_send_email == True :
                            vals['state'] = 'approved'
                            vals['email_supplier'] = False
                        else:
                            vals['email_supplier'] = True
                            vals['state'] = 'supply_confirm'

                    vals['sap_update_flag'] = '1'
                    del vals['order_line']
                    group_id_order = vals['group_id']
                    del vals['group_id']
                    self.pool.get('purchase.order').write(cr, uid, update_id, vals, context)
                    sql = "update purchase_order set amount_untaxed=" + str(SAP_AMOUNT_UNTAXED) + ",group_id=" + str(group_id_order) + ",amount_tax=" + str(
                        SAP_AMOUNT_TAX) + ",amount_total=" + str(SAP_AMOUNT_TOTAL) + " where id=" + str(update_id) + " "
                    cr.execute(sql)


    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, group_id, context=None):
        ''' prepare the stock move data from the PO line. This function returns a list of dictionary ready to be used in stock.move's create()'''
        product_uom = self.pool.get('uom.uom')
        price_unit = order_line.price_unit
        if order_line.taxes_id:
            taxes = self.pool['account.tax'].compute_all(cr, uid, order_line.taxes_id, price_unit, 1.0,
                                                             order_line.product_id, order.partner_id)
            price_unit = taxes['total']
        if order_line.product_uom.id != order_line.product_id.uom_id.id:
            price_unit *= order_line.product_uom.factor / order_line.product_id.uom_id.factor
        if order.currency_id.id != order.company_id.currency_id.id:
            #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
            price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
        res = []
        if order.location_id.usage == 'customer':
            name = order_line.product_id.with_context(dict(context or {}, lang=order.dest_address_id.lang)).display_name
        else:
            name = order_line.name or ''
        move_template = {
            'name': name,
            'product_id': order_line.product_id.id,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': order.date_order,
            'date_expected': order_line.date_planned,
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id,
            'move_dest_id': False,
            'state': 'draft',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': order.picking_type_id.id,
            'group_id': group_id,
            'procurement_id': False,
            'origin': order.name,
            'route_ids': order.picking_type_id.warehouse_id and [(6, 0, [x.id for x in order.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id':order.picking_type_id.warehouse_id.id,
            'invoice_state': order.invoice_method == 'picking' and '2binvoiced' or 'none',
        }

        diff_quantity = order_line.product_qty
        for procurement in order_line.procurement_ids:
            procurement_qty = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=order_line.product_uom.id)
            tmp = move_template.copy()
            tmp.update({
                'product_uom_qty': min(procurement_qty, diff_quantity),
                'product_uos_qty': min(procurement_qty, diff_quantity),
                'move_dest_id': procurement.move_dest_id.id,  #move destination is same as procurement destination
                'group_id': procurement.group_id.id or group_id,  #move group is same as group of procurements if it exists, otherwise take another group
                'procurement_id': procurement.id,
                'invoice_state': procurement.rule_id.invoice_state or (procurement.location_id and procurement.location_id.usage == 'customer' and procurement.invoice_state=='2binvoiced' and '2binvoiced') or (order.invoice_method == 'picking' and '2binvoiced') or 'none', #dropship case takes from sale
                'propagate': procurement.rule_id.propagate,
            })
            diff_quantity -= min(procurement_qty, diff_quantity)
            res.append(tmp)
        #if the order line has a bigger quantity than the procurement it was for (manually changed or minimal quantity), then
        #split the future stock move in two because the route followed may be different.
        if float_compare(diff_quantity, 0.0, precision_rounding=order_line.product_uom.rounding) > 0:
            move_template['product_uom_qty'] = diff_quantity
            move_template['product_uos_qty'] = diff_quantity
            res.append(move_template)
        return res




    def send_email_lifnr(self,cr,uid,ids):
            id=ids[0]
            order = self.env['purchase.order'].browse(id)
            email_template_obj_message = self.env['mail.compose.message']
            email_template_obj = self.env['mail.template']
            ir_model_data = self.env['ir.model.data']
            template_ids = ir_model_data.get_object_reference('srm_purchase_order_workflow', 'email_template_confim_purchase')[1]
            # if template_ids:
            #     values = email_template_obj.generate_email(template_ids, id)
            attachment_ids_value = email_template_obj_message.onchange_template_id( template_ids,  'comment', 'purchase.order', id)
            vals = {}
            vals['composition_mode'] = 'comment'
            attachment_ids = []
            attachment_ids.append([6, False, attachment_ids_value['value']['attachment_ids']])
            #vals['attachment_ids'] = attachment_ids
            vals['template_id'] = template_ids
            vals['parent_id'] = False
            vals['notify'] = False
            vals['no_auto_thread'] = False
            vals['reply_to'] = False
            vals['model'] = 'purchase.order'
            partner_ids = []
            partner_ids.append([6, False, attachment_ids_value['value']['partner_ids']])
            vals['partner_ids'] = attachment_ids_value['value']['partner_ids']
            vals['body'] = attachment_ids_value['value']['body']
            vals['res_id'] = id
            vals['email_from'] = order.create_uid.email
            vals['subject'] = attachment_ids_value['value']['subject']
            emil_id = self.env['mail.compose.message'].create(vals)
            emil_id.send_mail()

    def srm_wkf_confirm_order(self, cr, uid, ids,state, context=None):
        self.button_confirm_sync(cr, uid, ids,state)


    def button_confirm_sync(self,cr, uid, ids,state):
        for order in self.pool.get('purchase.order', self).browse(cr, uid, ids):
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.user.company_id.currency_id.compute(
                        order.company_id.po_double_validation_amount, order.currency_id)) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve_sync()
            else:
                order.write({'state': 'to approve'})
        return True

        # 确认订单

    def button_approve_sync(self):
        state = 'purchase'
        for order in self:
            if order.partner_id.order_confirm and order.partner_id.order_confirm == True:
                state = 'supply_confirm'

        self.write({'state': state, 'date_approve': fields.Date.context_today(self)})
        self._create_picking_sync()
        self.filtered(
            lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
        return {}

    def _prepare_picking_sync(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise ValidationError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }

    def _create_picking_sync(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done','cancel'))
                if not pickings:
                    res = order._prepare_picking()
                    picking = StockPicking.create(res)
                else:
                    picking = pickings[0]
                moves = order.order_line._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True


    def get_two_float(self,f_str, n):
        f_str = str(f_str)  # f_str = '{}'.format(f_str) 也可以转换为字符串
        a, b, c = f_str.partition('.')
        c = (c + "0" * n)[:n]  # 如论传入的函数有几位小数，在字符串后面都添加n为小数0
        return ".".join([a, c])

class SrmProductCategoryGroupId(models.Model):
    _inherit = 'product.category'
    group_id=fields.Char("采购组")


class SrmPurchaseOrderLine(models.Model):
   _inherit = 'purchase.order.line'
   lgort = fields.Char(string='lgort')   #库存地点
   item = fields.Char(string='item')     #行项目
   werks = fields.Char(string='werks')   #工厂
   no_more_gr=fields.Char(string='no more gr') #交货已完成标识
   sap_product_qty = fields.Char(string='sap product qty')  #
   sap_amount_qty = fields.Char(string='sap amount qty')  # 含税金额
   sap_price_unit=fields.Char(string='sap price unit') #含税单价
   ret_item= fields.Boolean(string='ret item') #退货项目
   component_id = fields.Many2one('purchase.component', 'component', readonly=True)
   item_cat= fields.Boolean(string='item cat') #外协订单
   def write_sync(self, cr, uid, ids, vals,context=None):
       super(SrmPurchaseOrderLine, self).write(cr, uid, ids,vals,context=context)
       return True

   def unlink_sync(self, cr, uid, ids, context=None):
       super(SrmPurchaseOrderLine, self).unlink(cr, uid, ids, context=context)
       return True

   # def search(self):
   #     # order = 'item asc '
   #     # args.append(('product_qty', '<>', 0))
   #     return super(SrmPurchaseOrderLine, self).search()



class SrmPurchaseOrder(models.Model):
   _inherit = 'purchase.order'
   updatetime_sap=fields.Datetime(string='updatetime_sap') #SAP更新时间
   date_order1=fields.Char(string='date_order1') #创建日期
   sap_amount_untaxed=fields.Char(string='sap amount untaxed') #总计不含税金额
   sap_amount_tax=fields.Char(string='sap amount tax') #税额
   sap_amount_total=fields.Char(string='sap amount total') #总计含税

   sap_update_flag = fields.Char(string='sap update flag',default=0)  # 更新标识 0初始化 1=更新
   sap_order_type= fields.Char(string='sap update flag',default=0)  # SAP订单类型 0标准 99=采购退补料合同

   def action_picking_create(self, cr, uid, ids, context=None):

        for order in self.browse(cr, uid, ids):
            # picking_vals = {
            #     'picking_type_id': order.picking_type_id.id,
            #     'partner_id': order.partner_id.id,
            #     'date': order.date_order,
            #     'origin': order.name
            # }
            picking_id=""

            #picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals, context=context)
            self._create_stock_moves(cr, uid, order, order.order_line, picking_id, context=context)

        return picking_id

   def _create_stock_moves(self, cr, uid, order, order_lines, picking_id=False, context=None):

       stock_move = self.pool.get('stock.move')
       todo_moves = []
       new_group = self.pool.get("procurement.group").create(cr, uid,
                                                             {'name': order.name, 'partner_id': order.partner_id.id},
                                                             context=context)
       is_ret_item=False

       for order_line in order_lines:
           if order_line.state == 'cancel':
               continue
           if not order_line.product_id:
               continue
           if order_line.ret_item:
               is_ret_item=True
               continue
           if picking_id=="":
                picking_vals = {
                    'picking_type_id': order.picking_type_id.id,
                    'partner_id': order.partner_id.id,
                    'date': order.date_order,
                    'origin': order.name
                }
                picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals, context=context)
           if order_line.product_id.type in ('product', 'consu'):
               for vals in self._prepare_order_line_move(cr, uid, order, order_line, picking_id, new_group,
                                                         context=context):
                   move = stock_move.create(cr, uid, vals, context=context)
                   todo_moves.append(move)
       todo_moves = stock_move.action_confirm(cr, uid, todo_moves)
       stock_move.force_assign(cr, uid, todo_moves)


       if is_ret_item:
           #生成新的作业号
           todo_moves = []
           ret_picking_type_id=order.picking_type_id.id
           #退貨161
           sql="select ID  from stock_picking_type where move_type='161'"
           cr.execute(sql)
           ret_picking_type_id_sql = cr.fetchone()
           if ret_picking_type_id_sql:
               ret_picking_type_id=ret_picking_type_id_sql[0]

           picking_vals = {
               'picking_type_id': ret_picking_type_id,
               'partner_id': order.partner_id.id,
               'date': order.date_order,
               'origin': order.name
           }
           picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals, context=context)

           for order_line in order_lines:
               if order_line.state == 'cancel':
                   continue
               if not order_line.product_id:
                   continue
               if not order_line.ret_item:
                   continue
               if order_line.product_id.type in ('product', 'consu'):
                   for vals in self._prepare_order_line_move_ref(cr, uid, order, order_line, picking_id, new_group,context=context):
                       move = stock_move.create(cr, uid, vals, context=context)
                       todo_moves.append(move)
           todo_moves = stock_move.action_confirm(cr, uid, todo_moves)
           stock_move.force_assign(cr, uid, todo_moves)


   def _prepare_order_line_move_ref(self, cr, uid, order, order_line, picking_id, group_id, context=None):
       ''' prepare the stock move data from the PO line. This function returns a list of dictionary ready to be used in stock.move's create()'''
       product_uom = self.pool.get('uom.uom')
       price_unit = order_line.price_unit
       if order_line.taxes_id:
           taxes = self.pool['account.tax'].compute_all(cr, uid, order_line.taxes_id, price_unit, 1.0,
                                                        order_line.product_id, order.partner_id)
           price_unit = taxes['total']
       if order_line.product_uom.id != order_line.product_id.uom_id.id:
           price_unit *= order_line.product_uom.factor / order_line.product_id.uom_id.factor
       if order.currency_id.id != order.company_id.currency_id.id:
           # we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
           price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id,
                                                              order.company_id.currency_id.id, price_unit, round=False,
                                                              context=context)
       res = []
       if order.location_id.usage == 'customer':
           name = order_line.product_id.with_context(dict(context or {}, lang=order.dest_address_id.lang)).display_name
       else:
           name = order_line.name or ''
       move_template = {
           'name': name,
           'product_id': order_line.product_id.id,
           'product_uom': order_line.product_uom.id,
           'product_uos': order_line.product_uom.id,
           'date': order.date_order,
           'date_expected': order_line.date_planned,
           'location_id': order.location_id.id,
           'location_dest_id': order.partner_id.property_stock_supplier.id,
           'picking_id': picking_id,
           'partner_id': order.dest_address_id.id,
           'move_dest_id': False,
           'state': 'draft',
           'purchase_line_id': order_line.id,
           'company_id': order.company_id.id,
           'price_unit': price_unit,
           'picking_type_id': order.picking_type_id.id,
           'group_id': group_id,
           'procurement_id': False,
           'origin': order.name,
           'route_ids': order.picking_type_id.warehouse_id and [
               (6, 0, [x.id for x in order.picking_type_id.warehouse_id.route_ids])] or [],
           'warehouse_id': order.picking_type_id.warehouse_id.id,
           'invoice_state': order.invoice_method == 'picking' and '2binvoiced' or 'none',
       }

       diff_quantity = order_line.product_qty
       for procurement in order_line.procurement_ids:
           procurement_qty = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty,
                                                      to_uom_id=order_line.product_uom.id)
           tmp = move_template.copy()
           tmp.update({
               'product_uom_qty': min(procurement_qty, diff_quantity),
               'product_uos_qty': min(procurement_qty, diff_quantity),
               'move_dest_id': procurement.move_dest_id.id,  # move destination is same as procurement destination
               'group_id': procurement.group_id.id or group_id,
           # move group is same as group of procurements if it exists, otherwise take another group
               'procurement_id': procurement.id,
               'invoice_state': procurement.rule_id.invoice_state or (
                           procurement.location_id and procurement.location_id.usage == 'customer' and procurement.invoice_state == '2binvoiced' and '2binvoiced') or (
                                            order.invoice_method == 'picking' and '2binvoiced') or 'none',
           # dropship case takes from sale
               'propagate': procurement.rule_id.propagate,
           })
           diff_quantity -= min(procurement_qty, diff_quantity)
           res.append(tmp)
       # if the order line has a bigger quantity than the procurement it was for (manually changed or minimal quantity), then
       # split the future stock move in two because the route followed may be different.
       if float_compare(diff_quantity, 0.0, precision_rounding=order_line.product_uom.rounding) > 0:
           move_template['product_uom_qty'] = diff_quantity
           move_template['product_uos_qty'] = diff_quantity
           res.append(move_template)
       return res