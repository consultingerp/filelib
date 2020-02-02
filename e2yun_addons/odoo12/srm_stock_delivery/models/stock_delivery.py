#!/usr/bin/python
# -*- coding: UTF-8 -*-
from odoo import models, fields, tools, api, exceptions

import logging
import time
try:
    from odoo.addons.srm_pyrfc import ZSRM_BAPI_GOODSMVT_CREATE
except:
    pass
import sys
import datetime

_logger = logging.getLogger(__name__)


class transfer_log(models.Model):
    _name = 'transfer.log'
    _description = "Transfer Log"

    picking_id = fields.Many2one('stock.picking', 'Picking')
    po_line_id = fields.Many2one('purchase.order.line', 'Purchase Order Line')
    qty = fields.Float('Qty')
    product_id = fields.Many2one('product.product', 'Product')
    move_id = fields.Many2one('stock.move', 'Move')
    used = fields.Boolean('Used')


class stock_delivery(models.Model):
    _inherit = "stock.picking.type"
    _description = "Stock Delivery Kanban"

    def _get_isCome(self):
        for obj in self:
            if obj.code == 'incoming':
                obj.isCome = True
            else:
                obj.isCome = False

    def _get_delivery_count(self):

        comco = self.env['res.company']._company_default_get('delivery.order').id

        sql = ("select count( DISTINCT h.dnnum)"
               "from delivery_pack_operation h "
               "where h.comco = %(comco)s and h.picking_type_id = %(picking_type_id)s ")
        for obj in self:
            param = {
                'comco': comco,
                'picking_type_id': obj.id
            }
            self._cr.execute(sql, param)
            obj.count_delivery_ready = int(self._cr.fetchall()[0][0])

    count_delivery_ready = fields.Integer("Delivery Ready Count", compute='_get_delivery_count')
    isCome = fields.Boolean('IsCome', compute='_get_isCome',default=False)

    def get_delivery_dnnums(self):
        comco = self.env['res.company']._company_default_get('delivery.order').id,
        sql = ("select DISTINCT h.dnnum "
               "from delivery_pack_operation h "
               "where h.comco = %(comco)s  and h.picking_type_id = %(picking_type_id)s ")
        param = {
            'comco': comco,
            'picking_type_id': self._ids['ids']
        }
        self._cr.execute(sql, param)
        return self._cr.fetchall()

    def open_jiaohuodan_interface(self):
        # return {
        #     'type': 'ir.actions.client',
        #     'name': '收货',
        #     'tag': 'deliveryMain'
        # }

        final_url = "/deliveryBarcode/web/#action=delivery.ui&picking_type_id=" + str(self._ids[0]) if len(self._ids) else '0'
        return {'type': 'ir.actions.act_url', 'url': final_url, 'target': 'self'}


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    delivery_line_ids = fields.One2many('delivery.pack.operation', 'picking_id', 'Delivery Line')


class delivery_pack_operation(models.Model):
    _name = "delivery.pack.operation"
    _auto = False

    dnnum = fields.Char('Delivery Order')
    comco = fields.Many2one('res.company', 'Company')
    ponum = fields.Char('Purchase Order')
    pline = fields.Many2one('purchase.order.line', 'Purchase Order Line')
    poitem = fields.Char('PO Item')
    matnr = fields.Many2one('product.product')
    matnr_name = fields.Char('Product')
    location_id = fields.Many2one('stock.location', 'Location')
    location_dest_id = fields.Many2one('stock.location', 'Location Dest')
    location_name = fields.Char('Location')
    location_dest_name = fields.Char('Location Dest')
    qty = fields.Integer('Qty')
    menge = fields.Integer('Mange')
    product_uom = fields.Many2one('uom.uom', 'Unit')
    product_uom_name = fields.Char('Unit')
    picking_id = fields.Many2one('stock.picking')
    delivery_po_line_id = fields.Many2one('delivery.purchase.orders')
    delivery_order_id = fields.Many2one('delivery.order')
    delivery_order_line_id = fields.Many2one('delivery.order.line')
    move_id = fields.Many2one('stock.move')

    def get_pack_operation_exist(self,vals):
        sql = ("select distinct sm.picking_id as picking_id FROM "
               "delivery_order h "
               "INNER JOIN delivery_order_line l ON h.ID = l.delivery_order_id "
               "INNER JOIN delivery_purchase_orders dpo ON l.ID = dpo.delivery_order_line_id "
               "INNER JOIN purchase_order po ON po.ID = dpo.ponum  "
               "INNER JOIN purchase_order_line pol ON  dpo.pline=pol.ID  "
               "INNER JOIN stock_move sm ON sm.purchase_line_id = pol.ID  "
               "where h.state='print' and h.dnnum = %(dnnum)s ")
        param = {
            'dnnum': vals,
        }
        self._cr.execute(sql, param)
        pickingIds = self._cr.fetchall()
        pickingIdArrya = []
        for pickingId in pickingIds:
            pickingIdArrya.append(pickingId[0])
        result = []
        picking_obj = self.env["stock.picking"]
        for pick in picking_obj.browse(pickingIdArrya):
            if pick.delivery_line_ids or pick.id in result:
                continue
            else:
                result.append(pick.id)
        return result

    @api.model
    def readDelivery(self,dnnum):
        comco = self.env['res.company']._company_default_get('delivery.order').id
        param = {}
        sql = (
            " select * from delivery_pack_operation where  comco = %(comco)s  ")
        param = {
            'comco': comco,
        }

        if self._ids:
            sql += " and picking_type_id = %(picking_type_id)s "
            param["picking_type_id"] = self._ids

        if dnnum:
            sql += " and dnnum= %(dnnum)s "
            param["dnnum"] = dnnum
        self._cr.execute(sql, param)
        datalist = self._cr.dictfetchall()
        return datalist

    def saveOperationQtydone(self,vals):
        if (len(vals) > 0):
            for val in vals:
                if val['qty'] == 0:
                    val['qty'] = val['menge']
        return vals

    def getDoneQty(self):
        return self.qty_done

    def init(self):
        tools.drop_view_if_exists(self._cr, 'delivery_pack_operation')
        self._cr.execute("""
            create or replace view delivery_pack_operation as (
                 select cast(t.id as integer) id,
                    t.dnnum,
                    t.comco,
                    t.ponum,
                    t.pline,
                    t.poitem,
                    t.matnr,
                    t.matnr_name,
                    t.location_id,
                    t.location_dest_id,
                    t.move_id,
                    t.location_name,
                    t.location_dest_name,
                    t.menge,
                    t.qty,
                    t.picking_id,
                    t.delivery_po_line_id,
                    t.delivery_order_id,
                    t.delivery_order_line_id,
                    t.product_uom,
                    t.product_uom_name,
                    t.picking_type_id 
                  from (SELECT
                    concat(substr(trim(to_char(dpo.id, '99999999999')),length(trim(to_char(dpo.id, '99999999999')))-2,3),
                           substr(trim(to_char(sm.id, '99999999999')),length(trim(to_char(sm.id, '99999999999')))-2,3)
                    ) id,
                    doh.dnnum,
                    doh.comco,
                    po.name as ponum,
                    dpo.pline,
                    pol.item AS poitem,
                    dol.matnr,
                    pp.default_code ||'['|| pt.name || ']' as matnr_name,
                    sm.location_id,
                    sm.location_dest_id,
                    sm.id as move_id,
                    sl.complete_name as location_name,
                    sl1.complete_name as location_dest_name,
                    dpo.menge,
                    dpo.menge - COALESCE(dpo.done_menge,0) qty,
                    sp.id as picking_id,
                    dpo.id as delivery_po_line_id,
                    doh.id as delivery_order_id,
                    dol.id as delivery_order_line_id,
                    sm.product_uom,
                    pu.name as product_uom_name,
                    sp.picking_type_id 
                FROM
                    delivery_order doh
                    INNER JOIN delivery_order_line dol ON doh.ID = dol.delivery_order_id
                    INNER JOIN delivery_purchase_orders dpo ON dpo.delivery_order_line_id = dol.ID 
                    LEFT JOIN stock_move sm ON sm.purchase_line_id = dpo.pline and sm.location_dest_id in (select id from stock_location where usage='internal')
                    LEFT JOIN stock_picking sp ON sp.ID = sm.picking_id
                    left join purchase_order po on po.id = dpo.ponum
                    LEFT JOIN purchase_order_line pol ON pol.ID = dpo.pline
                    left join product_product pp on pp.id = dol.matnr
                    left join product_template pt on pt.id = pp.product_tmpl_id
                    left join uom_uom pu on pu.id = sm.product_uom
                    left join stock_location sl on sl.id = sm.location_id
                    left join stock_location sl1 on sl1.id = sm.location_dest_id
                WHERE
                    doh.STATE = 'print' 
                    AND sp.STATE = 'assigned'
                    and dol.isinvalid = False
                    and dpo.menge - COALESCE(dpo.done_menge,0) > 0) t
            )""")

    def trans_to_sap(self, dnnum, trans_lines):

        #reload(sys)
        #sys.setdefaultencoding('utf8')
        patng_date = str(datetime.date.today()).replace('-', '')
        sapVouchaer = self.env["sap.voucher"]
        GOODSMVT_ITEM = []
        vouchaer_vals = []
        GOODSMVT_HEADER = {'PSTNG_DATE': patng_date,
                           'DOC_DATE': patng_date,
                           'REF_DOC_NO': dnnum,
                           'HEADER_TXT': '交货单' + dnnum,
                           'PR_UNAME': self.env['res.users'].browse(self._uid).login
                           }

        num = 0
        #sql = """update purchase_order_line set delivery_qty = coalesce(delivery_qty,0) + %s,the_po=product_qty-(coalesce(delivery_qty,0) + %s) where id = %s """
        sql = """update purchase_order_line set delivery_qty = coalesce(delivery_qty,0) + %s where id = %s """
        po_ids = []
        for line in trans_lines:
            self._cr.execute(sql, (line['ENTRY_QNT'],line['pline']))
            if line['ENTRY_QNT'] > 0:
                GOODSMVT_ITEM.append({
                    'MATERIAL': str(line['MATERIAL']),
                    'PLANT': str(line['PLANT']),
                    'MOVE_TYPE': '103',
                    'ENTRY_UOM': line['ENTRY_UOM'],
                    'ENTRY_QNT': line['ENTRY_QNT'],
                    'PO_NUMBER': str(line['PO_NUMBER']),
                    'PO_ITEM': str(line['PO_ITEM']),
                    'MVT_IND': 'B',
                })
                num += 1
                vouchaer_vals.append({
                    'ponum': line['PO_NUMBER'],
                    'pline': line['PO_ITEM'],
                    'dnnum': dnnum,
                    'matnr':line['matnr'],
                    'matnrcode': line['matnrcode'],
                    'matnrdesc':line['matnrdesc'],
                    'dline': line['dline'],
                    'movetype': '103',
                    'psingdate': patng_date,
                    'linemark': num,
                    'pickname': line['picking_name'],
                    'picking_id': line['picking_id'],
                    'move_id': line['move_id'],
                    'po_line_id': line['pline'],
                    'po_id': line['po_id'],
                    'qty': line['ENTRY_QNT'],
                    'printSendDate': line['printSendDate'],
                    'prnum':line['prnum']
                })

        # zbapi_goodsmvt_create = ZSRM_BAPI_GOODSMVT_CREATE.ZBAPI_GOODSMVT_CREATE()
        # result_rfc = zbapi_goodsmvt_create.BAPI_GOODSMVT_CREATE(self._cr, GOODSMVT_HEADER, GOODSMVT_ITEM, '01')
        # if result_rfc['code'] == 1 and 'message' in result_rfc:
        #     raise exceptions.ValidationError(" SAP收货过账失败，失败原因：%s" % (result_rfc['message']))
        # elif result_rfc['code'] == 1 and 'message' not in result_rfc:
        #     raise exceptions.ValidationError(" SAP收货过账失败.")
        # else:
        #     mat_doc = result_rfc['MAT_DOC']
        #     for line in vouchaer_vals:
        #         line['matdoc'] = mat_doc
        #         sapVouchaer.create(line)

        for line in vouchaer_vals:
            line['matdoc'] = str(int(time.time()))
            sapVouchaer.create(line)

    @api.model
    def action_done_from_ui(self, dnnum, change_lines):
        deliveryPickings = self.readDelivery(dnnum)
        picking_ids = []
        move_ids = []
        picking_obj = self.env['stock.picking']
        order_obj = self.env['delivery.order']
        spt_obj = self.env['stock.picking.type']
        stock_move_obj = self.env['stock.move']
        delivery_packs = []

        for line in change_lines:
            obj = self.browse(line['id'])
            delivery_packs.append({
                'id': line['id'],
                'matnr_id': obj.matnr.id,
                'picking_id': obj.picking_id.id,
                'move_id': obj.move_id.id,
                'product_uom_name': obj.product_uom_name,
                'ponum': obj.ponum,
                'poitem': obj.poitem,
                'pline': obj.pline.id,
                'po_id': obj.pline.order_id.id,
                'delivery_order_line_id': obj.delivery_order_line_id.id,
                'qty':line['qty']
            })

        for line in change_lines:
            obj = self.browse(line['id'])
            obj.delivery_po_line_id.done_menge = obj.delivery_po_line_id.done_menge + line['qty']

        for delivery in deliveryPickings:
            picking_id = delivery['picking_id']
            if picking_id not in picking_ids:
                picking_ids.append(picking_id)

        for delivery in deliveryPickings:
            move_id = delivery['move_id']
            if move_id not in move_ids:
                move_ids.append(move_id)

        for picking in picking_ids:
            picking_info = picking_obj.browse(picking)
            for move in picking_info.move_lines:
                if move.id in move_ids:
                    qty = 0
                    for delivery in deliveryPickings:
                        if move.id == delivery['move_id']:
                            delivery_id = delivery['id']
                            for v in change_lines:
                                if delivery_id == v['id']:
                                    qty += v['qty']
                    move_lines = move._get_move_lines()
                    if move_lines:
                        move_lines[0].qty_done = qty
                    else:
                        move_line = self.env['stock.move.line'].create(
                            dict(move._prepare_move_line_vals(), qty_done=qty))
                        move.write({'move_line_ids': [(4, move_line.id)]})

        trans_sap_lines = []
        deliveryorder_obj = order_obj.search([('dnnum', '=', dnnum)])
        for pack in delivery_packs:
            move = stock_move_obj.browse(pack['move_id'])
            trans_sap_lines.append({
                'MATERIAL': move.product_id.default_code,
                'matnr': move.product_id.id,
                'matnrcode': move.product_id.default_code,
                'matnrdesc': move.product_id.product_tmpl_id.name,
                'PLANT': move.picking_id.company_id.company_code,
                'picking_name': move.picking_id.name,
                'ENTRY_UOM': pack['product_uom_name'],
                'PO_NUMBER': pack['ponum'],
                'PO_ITEM': pack['poitem'],
                'dline': pack['delivery_order_line_id'],
                'ENTRY_QNT': pack['qty'],
                'picking_id': pack['picking_id'],
                'move_id': pack['move_id'],
                'pline': pack['pline'],
                'po_id': pack['po_id'],
                'printSendDate': deliveryorder_obj.printSendDate,
                'prnum': deliveryorder_obj.prnum
            })

        if len(picking_ids) > 0:
            for p in picking_obj.browse(picking_ids):
                p.action_done()
            self.trans_to_sap(dnnum, trans_sap_lines)

        order_dbobj = order_obj.search([('dnnum', '=', dnnum)])
        order_dbobj.write({'state': 'Finished', 'hstat': 'in_stock'})
        return True