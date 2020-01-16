# -*- coding: UTF-8 -*-
from odoo import models, fields, tools, api, exceptions
import datetime


class delivery_order_import(models.Model):
    _name = "delivery.order.import"

    name = fields.Char("Order Name")
    lifnr = fields.Char("Lifnr")
    delivery_order_line = fields.One2many('delivery.order.line.import', 'order_id', 'Delivery Order Line Import')

    _order = " create_date desc "

    def search(self, args, offset=0, limit=None, order=None,  count=False):
        lifnr = self.env['res.users']._get_default_supplier()
        if lifnr > 0:
            args += [('lifnr', '=', lifnr)]
        return super(delivery_order_import, self).search(
            args, offset=offset, limit=limit, order=order,
            count=count)


    def create(self, vals):
        context = dict(self._context or {})
        context['source'] = 'import'
        deliveryOrder = self.env['delivery.order']
        lifnr = self.env['res.users']._get_default_supplier()
        comco = self.env['res.company']._company_default_get('delivery.order').id
        if 'delivery_order_line' in vals.keys():
            delivery_order_vals ={}
            delivery_order_vals['lifnr'] = lifnr
            delivery_order_vals['werks'] = 1
            delivery_order_vals['comco'] = comco
            lines = vals['delivery_order_line']
            delivery_order_line_array = []
            for line in lines:
                delivery_order_line_obj = {}
                deliveryorderline = self.env["delivery.order.line"]
                if 'line_po_mo' in line[2].keys():
                    linepomos = line[2]['line_po_mo']
                    delivery_purchase_orders_array = []
                    delivery_product_orders_array=[]
                    sumdnmng =0
                    mantr = 0
                    for linepomo in linepomos:
                        if  linepomo[2]==False:
                            raise exceptions.ValidationError("No data in the import file was obtained.")

                        if  linepomo[2]['menge']==False:
                            raise exceptions.ValidationError("Menge is not allowed to be empty.")

                        importobj =  linepomo[2]
                        sumdnmng += importobj['menge']
                        if importobj['po'] == False:
                            raise exceptions.ValidationError("Purchase order is not allowed to be empty!")
                        if importobj['poitem'] == False:
                            raise exceptions.ValidationError("The purchase order line item is not allowed to be empty!")
                        poitem = str(importobj['poitem'])
                        if len(poitem)==2:
                            importobj['poitem'] = '000'+poitem
                        elif len(poitem)==3:
                            importobj['poitem'] = '00'+poitem
                        elif len(poitem)==4:
                            importobj['poitem'] = '0'+poitem

                        purchase_obj = self.env['purchase.order'].search([('name','=',importobj['po'])])
                        if len(purchase_obj)==0:
                            raise exceptions.ValidationError("Purchase Order:"+importobj['po']+"not exists!")


                        poLine = self.env['purchase.order.line']
                        poline_obj = poLine.search([('order_id', '=', purchase_obj.id),('item','=',str(importobj['poitem']))])
                        if len(poline_obj)==0:
                            raise exceptions.ValidationError("Purchase Order:" + importobj['po'] + ",Item:"+poitem+" not exists!")
                        meins = poline_obj.product_uom
                        mantr = poline_obj.product_id
                        today = datetime.datetime.today()
                        todaystr = today.strftime('%Y-%m-%d')
                        delivery_order_vals['datoo'] = todaystr
                        poline = self.select_po_residual_quantity(lifnr, comco, poline_obj.product_id.id, 1, purchase_obj.id, poline_obj.id)
                        if len(poline)==0:
                            raise exceptions.ValidationError("No order quantity for purchase orders:%s ,item:%s." %(purchase_obj.name,poline_obj.item))
                        for line in poline:
                            if importobj['menge']>line['menge']:
                                raise exceptions.ValidationError("The quantity is larger than the quantity of purchase order:%s, item:%s.Max matching number:%s" %(purchase_obj.name,str(line['item']),int(line['menge'])))

                        delivery_purchase_orders_obj ={
                            'werks': 1,
                            'matnr': poline_obj.product_id.id,
                            'pline': poline_obj.id,
                            'ponum': purchase_obj.id,
                            'ddate': todaystr,
                            'lifnr': lifnr,
                            'item': poline_obj.item,
                            'comco': comco,
                            'menge': importobj['menge'],
                            'old_menge':0
                        }
                        delivery_purchase_orders_array.append([0,False,delivery_purchase_orders_obj])
                        productName = ''
                        if importobj['demand_id']:
                            if importobj['po'][0:1] == '5' or importobj['po'][0:2] == '92':
                                raise exceptions.ValidationError("Purchase orders with 5 or 92 are not allowed to associate production orders.")

                            if len(delivery_product_orders_array)>0 and delivery_product_orders_array[0][2]['details_id']==importobj['demand_id']:
                                delivery_product_orders_array[0][2]['penge'] = sumdnmng
                            else:
                                demandDetail = self.env['mat.demand.line.details'].browse(importobj['demand_id'])
                                if poline_obj.product_id != demandDetail.matnr:
                                    raise exceptions.ValidationError("The material of purchase order is inconsistent with the material in demand line!")
                                delivery_purchase_orders_obj['ddate'] = demandDetail.ddate
                                delivery_order_vals['datoo'] = demandDetail.ddate
                                productName = demandDetail.prnum
                                delivery_product_orders_obj = {
                                    'matnr': demandDetail.matnr.id,
                                    'aprng': 0,
                                    'lifnr': lifnr,
                                    'details_id': demandDetail.id,
                                    'prnum':demandDetail.prnum,
                                    'penge': importobj['menge'],
                                    'menge': demandDetail.menge,
                                    'ddate':demandDetail.ddate
                                }
                                delivery_product_orders_array.append([0,False,delivery_product_orders_obj])
                        else:
                            partner = self.env['res.partner'].browse(lifnr)
                            isallownoschedulecreate = partner.allow_no_schedule_create
                            if isallownoschedulecreate ==False:
                                raise exceptions.ValidationError("Suppliers are not allowed to make non scheduled delivery.")

                        if len(delivery_product_orders_array)>0:
                            for delivery_product_orders in delivery_product_orders_array:
                                demandResQtyList = self.get_demand_residual_quantity(delivery_product_orders[2]['details_id'])
                                if len(demandResQtyList)==0:
                                    raise exceptions.ValidationError("Demand line "+delivery_product_orders['details_id']+" has no quantity delivered.")
                                for demandRes in demandResQtyList:
                                    if delivery_product_orders[2]['penge']>demandRes['penge']:
                                        raise exceptions.ValidationError("The quantity of delivery is greater than the quantity of demand line.")




                    delivery_order_line_obj={
                        'werks': 1,
                        'matnr': mantr.id,
                        'meins': meins.id,
                        'prnum': productName,
                        'ekgrp': False,
                       # 'monum': 'RSR-DS402A-12-05-A',
                        'lifnr': lifnr,
                        'admng': 0,
                        'sdmng': 0,
                        'comco': comco,
                        'dnmng': sumdnmng,
                        'aomng': False,
                    }
                    delivery_order_line_obj['delivery_purchase_orders'] = delivery_purchase_orders_array
                    delivery_order_line_obj['delivery_product_orders'] = delivery_product_orders_array
                delivery_order_line_array.append([0,False,delivery_order_line_obj])
            delivery_order_vals['delivery_order_line'] = delivery_order_line_array
            deliveryOrderId = deliveryOrder.create(delivery_order_vals)
            neworder = deliveryOrder.browse(deliveryOrderId)
            vals['name'] = neworder.dnnum
            vals['lifnr'] = lifnr
            return super(delivery_order_import, self).create(vals)


    def select_po_residual_quantity(self,lifnr,comco,product_id,werks,poid,polineid):
        line = []
        order_sql = "select h.id as order_id,l.id as line_id,l.product_qty - l.delivery_qty as product_qty,l.date_planned,l.product_id,h.picking_type_id, " \
                    " case when l.item is not null then l.item else ''||l.id end as item from purchase_order h " \
                    " inner join purchase_order_line l on h.id = l.order_id " \
                    " left JOIN stock_move sm ON sm.purchase_line_id = l.id " \
                    " left JOIN stock_picking sp ON sp.ID = sm.picking_id " \
                    " where l.NO_MORE_GR is null AND h.id = %s AND l.id = %s AND h.partner_id = %s and h.company_id = %s  " \
                    " and h.state = 'supply_confirm' and sp.state='assigned' and l.product_id = %s and h.location_id = (select lot_stock_id from stock_warehouse where id = %s ) " \
                    " order by h.id "
        self._cr.execute(order_sql, (poid,polineid,lifnr, comco, product_id, werks))
        order_dicts = self._cr.dictfetchall()

        for od in order_dicts:
            po_sql = "select sum(menge) from delivery_purchase_orders o " \
                     "inner join delivery_order_line l on l.id = o.delivery_order_line_id " \
                     "inner join delivery_order h on h.id = l.delivery_order_id " \
                     "where h.state in ('supplier_create','print') " \
                     "and o.ponum = %s and o.pline = %s "
            self._cr.execute(po_sql, (poid, polineid))
            pomenge = self._cr.fetchone()
            if not pomenge[0]:
                pomenge = 0
            else:
                pomenge = pomenge[0]

            if od['product_qty'] - pomenge > 0:
                line.append({
                    'ponum': od['order_id'],
                    'pline': od['line_id'],
                    'menge': od['product_qty'] - pomenge,
                    'old_menge': od['product_qty'] - pomenge,
                    'matnr': od['product_id'],
                    'werks': werks,
                    'ddate': od['date_planned'],
                    'comco': comco,
                    'lifnr': lifnr,
                    'item': od['item']
                })
        return line

    def get_demand_residual_quantity(self,details_id):
        demandsql = "select details_id, prnum, menge, ddate, lifnr, matnr, aprng, menge - COALESCE(aprng,0) AS penge  " \
                    "from (SELECT md.ID AS details_id,prnum, menge,ddate, lifnr,matnr, " \
                    "(SELECT SUM(case when d.state in ('supplier_create','print') then penge else done_menge end) FROM delivery_product_orders dp " \
                    " INNER JOIN delivery_order_line dl on dp.delivery_product_line_id = dl.id " \
                    " INNER JOIN delivery_order d on d.id=dl.delivery_order_id  " \
                    " INNER JOIN delivery_purchase_orders on delivery_order_line_id = dl.id 	" \
                    " where dp.details_id = md.ID and d.state in ('supplier_create','print','Finished')) AS aprng " \
                    " FROM mat_demand_line_details md inner join mat_demand_head h on md.mat_demand_id =h.id where h.state='publish' and  md.state in ('create','supplier_confirm','supplier_edit','purchase_edit','purchase_confirm', 'not_confirm') and " \
                    " md.id = %(details_id)s )t where menge - COALESCE ( aprng, 0 )>0  "
        self._cr.execute(demandsql, {'details_id':details_id})
        productLine = self._cr.dictfetchall()
        return productLine



class delivery_order_line_import(models.Model):
    _name = "delivery.order.line.import"

    name = fields.Char("Line Name")
    order_id = fields.Many2one('delivery.order.import', 'Delivery Order Import', required=True, readonly=True,
                                        ondelete='cascade')
    line_po_mo = fields.One2many('order.line.po.mo.import', 'line_id', 'Order Line Po Mo Import')




class order_line_po_mo_import(models.Model):
    _name = "order.line.po.mo.import"


    po = fields.Char("Purchase Order")
    poitem = fields.Char("Purchase Order Item")
    matnr = fields.Char("Matnr")
    matnrdesc = fields.Char("Matnr Desc")
    menge = fields.Integer("Menge")
    demand_id = fields.Integer("Demand Id")
    line_id = fields.Many2one('delivery.order.line.import', 'Delivery Order Line Import', required=True, readonly=True,
                                        ondelete='cascade')




