#!/usr/bin/python
# -*- coding: UTF-8 -*-
from odoo import models, fields, tools, api, exceptions
from odoo.tools.translate import _

import logging
#from odoo.addons.srm_pyrfc import ZSRM_BAPI_GOODSMVT_CREATE
import sys
import datetime
import odoo.addons.decimal_precision as dp
import time

class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'

    def default_get(self,fields):
        if self._context is None: context = {}
        res = super(stock_transfer_details, self).default_get(fields)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.picking'), 'Bad context propagation'
        picking_id, = picking_ids
        picking = self.env['stock.picking'].browse(picking_id)
        items = []
        packs = []
        if not picking.pack_operation_ids:
            picking.do_prepare_partial()
        for op in picking.pack_operation_ids:
            if op.product_id:
                for link in op.linked_move_operation_ids:
                    item = {
                        'packop_id': op.id,
                        'product_id': op.product_id.id,
                        'product_uom_id': op.product_uom_id.id,
                        'quantity': link.qty,
                        'package_id': op.package_id.id,
                        'lot_id': op.lot_id.id,
                        'sourceloc_id': op.location_id.id,
                        'destinationloc_id': op.location_dest_id.id,
                        'result_package_id': op.result_package_id.id,
                        'date': op.date,
                        'owner_id': op.owner_id.id,
                        'move_id' : link.move_id.id
                    }
                    items.append(item)
            elif op.package_id:
                item = {
                    'packop_id': op.id,
                    'product_id': op.product_id.id,
                    'product_uom_id': op.product_uom_id.id,
                    'quantity': op.product_qty,
                    'package_id': op.package_id.id,
                    'lot_id': op.lot_id.id,
                    'sourceloc_id': op.location_id.id,
                    'destinationloc_id': op.location_dest_id.id,
                    'result_package_id': op.result_package_id.id,
                    'date': op.date,
                    'owner_id': op.owner_id.id,
                }
                packs.append(item)
        res.update(item_ids=items)
        res.update(packop_ids=packs)
        return res

    @api.one
    def do_detailed_transfer(self):

        # sql=("	select count(1) from stock_picking where name =( "
			# " select origin from stock_picking where id= %(picking_id)s )  ")
        # param = {}
        # param["picking_id"] = self.picking_id.id
        # cr = self.env.cr
        # self._cr.execute(sql, param)
        # count = cr.fetchone();
        # if count[0] == 0:
        #     raise exceptions.ValidationError("采购订单不允许直接收货，请通过交货单收货！ ")

        if self.picking_id.state not in ['assigned', 'partially_available']:
            raise Warning(_('You cannot transfer a picking in state \'%s\'.') % self.picking_id.state)

        processed_ids = []
        # Create new and update existing pack operations
        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                qty = prod.quantity

                pack_datas = {
                    'product_id': prod.product_id.id,
                    'product_uom_id': prod.product_uom_id.id,
                    #'product_qty': qty,
                    'package_id': prod.package_id.id,
                    'lot_id': prod.lot_id.id,
                    'location_id': prod.sourceloc_id.id,
                    'location_dest_id': prod.destinationloc_id.id,
                    'result_package_id': prod.result_package_id.id,
                    'date': prod.date if prod.date else datetime.now(),
                    'owner_id': prod.owner_id.id,
                }
                if prod.packop_id:
                    prod.packop_id.with_context(no_recompute=True).write(pack_datas)
                    processed_ids.append(prod.packop_id.id)
                else:
                    pack_datas['product_qty'] = qty
                    pack_datas['picking_id'] = self.picking_id.id
                    packop_id = self.env['stock.pack.operation'].create(pack_datas)
                    processed_ids.append(packop_id.id)
        # Delete the others
        packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', self.picking_id.id), '!', ('id', 'in', processed_ids)])
        packops.unlink()

        #Execute the transfer of the picking
        self.picking_id.action_done()
        #super(stock_transfer_details, self).do_detailed_transfer()

        self.sapdo_po_transfer();
        return True

    def sapdo_po_transfer(self):
        #reload(sys)
        sys.setdefaultencoding('utf8')
        patng_date = str(datetime.date.today()).replace('-', '');
        vouchaer_obj = self.env["sap.voucher"]
        offset_sap_voucher = self.env["offset.sap.voucher"]
        order_obj = self.env['purchase.order']
        move_obj = self.env['stock.move']
        vals = []
        GOODSMVT_ITEM = []
        GOODSMVT_HEADER = {'PSTNG_DATE': patng_date,
                           'DOC_DATE': patng_date,
                           'PR_UNAME': self.env['res.users'].browse(self._uid).login
                           }
        num = 0
        transfer_type = '103'
        des_loc_usage = self.item_ids[0].destinationloc_id.usage
        if des_loc_usage == 'supplier':
            transfer_type = '104'

        po_ids = []

        sql = """update purchase_order_line set delivery_qty = coalesce(delivery_qty,0) + %s,the_po=product_qty-(coalesce(delivery_qty,0) + %s) where id = %s """
        done_sql = """update delivery_purchase_orders set done_menge = coalesce(done_menge,0) + %s where delivery_order_line_id = %s and pline = %s """

        if transfer_type == '104':
            sql = """update purchase_order_line set delivery_qty = coalesce(delivery_qty,0) - %s,the_po=product_qty-(coalesce(delivery_qty) - %s) where id = %s """
            done_sql = """update delivery_purchase_orders set done_menge = coalesce(done_menge,0) - %s where delivery_order_line_id = %s and pline = %s """

        self = self.with_context(lang='en_US')
        for item in self.item_ids:
            if transfer_type == '104' and not item.move_reason:
                raise exceptions.ValidationError("反向调拨必须输入移动原因")

            num += 1
            voucher_id = []
            offset_ids = []
            quantity = item.quantity
            if transfer_type == '104':
                voucher_id = vouchaer_obj.search([
                    ('picking_id', '=', item.move_id.origin_returned_move_id.picking_id.id),
                    ('move_id', '=', item.move_id.origin_returned_move_id.id),
                    ('po_line_id', '=', item.move_id.purchase_line_id.id)
                ])

                if len(voucher_id) > 1:
                    for voucher in vouchaer_obj.browse(voucher_id):
                        offset_id = offset_sap_voucher.search([
                            ('origin_matdoc','=',voucher.matdoc),
                            ('orging_linemark','=',voucher.linemark)
                        ])
                        offset_qty = 0
                        for offset in offset_id:
                            offset_qty += offset.qty


                        if quantity <= voucher.qty - offset_qty:
                            offset_ids.append({'origin_matdoc': voucher.matdoc, 'origin_linemark': voucher.linemark,'qty': quantity})
                            quantity = 0
                        else:
                            offset_ids.append(
                                {'origin_matdoc': voucher.matdoc, 'origin_linemark': voucher.linemark, 'qty': voucher.qty - offset_qty})

                            quantity = quantity - voucher.qty - offset_qty

                        if quantity <= 0:
                            break

                else:
                    voucher = vouchaer_obj.browse(voucher_id)
                    offset_ids.append({'origin_matdoc': voucher.matdoc, 'origin_linemark': voucher.linemark,
                                       'qty': item.quantity})
                voucher = vouchaer_obj.browse(voucher_id[0])


            if voucher.po_id not in po_ids:
                po_ids.append(voucher.po_id)

            self._cr.execute(sql, (item.quantity, item.quantity,item.move_id.purchase_line_id.id))
            if voucher:
                self._cr.execute(done_sql, (item.quantity, voucher.dline,voucher.po_line_id))

            val = {
                'ponum': item.move_id.origin_returned_move_id.purchase_line_id.order_id.name,
                'pline': str(item.move_id.origin_returned_move_id.purchase_line_id.item),
                'dnnum': voucher.dnnum,
                'dline': voucher.dline,
                'operation_id': item.packop_id.id,
                'movetype': transfer_type,
                'psingdate': patng_date,
                'linemark': num,
                'pickname': self.picking_id.name,
                'picking_id': self.picking_id.id,
                'move_id': item.move_id.id,
                'po_line_id': voucher.po_line_id,
                'move_reason' : item.move_reason,
                'po_id' : voucher.po_id,
                'qty' : item.quantity,
                'matnr': voucher.matnr.id,
                'matnrcode': voucher.matnrcode,
                'matnrdesc': voucher.matnrdesc,
                'printSendDate': voucher.printSendDate,
                'prnum':voucher.prnum
            }
            vals.append(val)

            GOODSMVT_HEADER['REF_DOC_NO'] = voucher.dnnum or '00000'

            if transfer_type == '104':
                for offset in offset_ids:

                    GOODSMVT_ITEM_MAP = {
                        'MATERIAL': item.product_id.product_tmpl_id.prefix_code,
                         'PLANT': self.picking_id.company_id.company_code,
                         'MOVE_TYPE': str(transfer_type),
                         'ENTRY_UOM': item.move_id.product_uom.name,
                         'ENTRY_QNT': offset['qty'],
                         'PO_NUMBER': str(val['ponum']),
                         'PO_ITEM': str(val['pline']),
                         'MVT_IND': str.encode('B'),
                         'REF_DOC': str(offset['origin_matdoc']),
                         'REF_DOC_IT': str(offset['origin_linemark']),
                         'MOVE_REAS': item.move_reason or ''
                     }
                    GOODSMVT_ITEM.append(GOODSMVT_ITEM_MAP)

            else:
                GOODSMVT_ITEM_MAP = {
                    'MATERIAL': item.product_id.product_tmpl_id.prefix_code,
                     'PLANT': self.picking_id.company_id.company_code,
                     'MOVE_TYPE': str(transfer_type),
                     'ENTRY_UOM': item.move_id.product_uom.name,
                     'ENTRY_QNT': item.quantity,
                     'PO_NUMBER': str(val['ponum']),
                     'PO_ITEM': str(val['pline']),
                     'MVT_IND': str.encode('B'),
                     'MOVE_REAS': item.move_reason or ''
                 }

                GOODSMVT_ITEM.append(GOODSMVT_ITEM_MAP)
        self = self.with_context(lang='zh_CN')
        if transfer_type == '104':
            for id in po_ids:
                self._cr.execute("""update purchase_order set state = 'supply_confirm' where id = %(id)s """,{'id':id})
        else:
            order_line_obj = self.env['purchase.order.line']
            for order in order_obj.browse(po_ids):
                is_done = True
                for line in order.order_line:
                    if line.product_qty > line.delivery_qty:
                        is_done = False
                if is_done:
                    order.state = 'outgoing'

        #如果是104更新欠单信息
        if transfer_type == '104':
            for order in order_obj.browse(po_ids):
                picking_obj = None
                for picking in order.picking_ids:
                    move_ids = move_obj.search([('picking_id','=',picking.id)])
                    location_dest_ids = move_ids.read(['location_dest_id'])
                    location_results=[]
                    location_ids = []
                    for location_dest_id in  location_dest_ids:
                        location_ids.append(location_dest_id['location_dest_id'][0])
                    if len(location_ids)>0:
                        location_results = self.env['stock.location'].search([('id','in',location_ids),('usage','=','internal')])

                    if picking.state == 'assigned' and len(location_results)>0:
                        picking_obj = picking
                        break
                if picking_obj:
                    return_moves = move_obj.browse(self.picking_id.move_lines.ids)
                    for m in return_moves:
                        move_id = move_obj.search([('picking_id','=',picking_obj.id),('purchase_line_id','=',m.purchase_line_id.id)])
                        if move_id:
                            move = move_id[0]
                            move.product_uom_qty = move.product_uom_qty + m.product_uom_qty
                            move.product_uos_qty = move.product_uos_qty + m.product_uos_qty
                            if not move.origin_returned_move_id:
                                move.origin_returned_move_id = m.origin_returned_move_id.id
                                move.procure_method = m.origin_returned_move_id.procure_method
                        else:
                            new_move_id = move_obj.copy(m.id)

                            move_obj.browse(new_move_id).write({
                                'state': 'assigned',
                                'picking_id': picking_obj.id,
                                'location_id': m.location_dest_id.id,
                                'location_dest_id': m.location_id.id,
                                'move_dest_id': m.origin_returned_move_id.move_dest_id.id or
                                                m.origin_returned_move_id.move_dest_id,
                                'origin_returned_move_id': m.origin_returned_move_id.id,
                                'procure_method': m.origin_returned_move_id.procure_method,
                                'picking_type_id': picking_obj.picking_type_id.id,
                                'purchase_line_id': m.origin_returned_move_id.purchase_line_id.id,
                            })
                else:
                    picking_model = self.env['stock.picking']
                    return_moves = move_obj.browse(self.picking_id.move_lines.ids)

                    new_picking_id = picking_model.copy(self.picking_id.id, {
                        'state': 'assigned',
                        'picking_type_id': self.picking_id.picking_type_id.id,
                        'origin': self.picking_id.origin + '-' + self.picking_id.name,
                        'invoice_state': self.picking_id.invoice_state,
                    })
                    new_pick = picking_model.browse(new_picking_id)
                    new_moves = move_obj.browse(new_pick.move_lines.ids)

                    i = 0
                    for return_move in return_moves:
                        if new_moves[i]:
                            new_moves[i].write({
                                'location_id': return_move.location_dest_id.id,
                                'location_dest_id': return_move.location_id.id,
                                'state': 'waiting',
                                'move_dest_id': return_move.origin_returned_move_id.move_dest_id.id or
                                                return_move.origin_returned_move_id.move_dest_id,
                                'origin_returned_move_id': return_move.origin_returned_move_id.id,
                                'procure_method': return_move.origin_returned_move_id.procure_method,
                                'picking_type_id': return_move.origin_returned_move_id.picking_type_id.id,
                                'purchase_line_id': return_move.origin_returned_move_id.purchase_line_id.id,
                            })

                        i = i + 1
                    new_pick.rereserve_pick()
        elif transfer_type == '103':
            for order in order_obj.browse(po_ids):
                picking_obj = None
                for picking in order.picking_ids:
                    if picking.state != 'done':
                        picking_obj = picking
                        break
                if picking_obj:
                    return_moves = move_obj.browse(self.picking_id.move_lines.ids)
                    for m in return_moves:
                        move_id = move_obj.search([('picking_id','=',picking_obj.id),('purchase_line_id','=',m.purchase_line_id.id)])
                        if move_id:
                            move = move_id[0]
                            move.product_uom_qty = move.product_uom_qty - m.product_uom_qty
                            move.product_uos_qty = move.product_uos_qty - m.product_uos_qty

        GOODSMVT_HEADER['HEADER_TXT'] = '交货单'+GOODSMVT_HEADER['REF_DOC_NO']
        # zbapi_goodsmvt_create = None #ZSRM_BAPI_GOODSMVT_CREATE.ZBAPI_GOODSMVT_CREATE()
        # result_rfc = zbapi_goodsmvt_create.BAPI_GOODSMVT_CREATE(self._cr,GOODSMVT_HEADER, GOODSMVT_ITEM,'01')
        # if result_rfc['code'] == 1:
        #     msg = result_rfc['message']
        #     raise exceptions.ValidationError(" SAP调拨过账失败，失败原因：%s" % (msg))
        # else:
        #     msg = result_rfc['MAT_DOC']
        #     for val in vals:
        #         val['matdoc'] = msg
        #         vouchaer_obj.create(val)
        #     if offset_ids and len(offset_ids):
        #         for offset in offset_ids:
        #             offset['matdoc'] = msg
        #             offset_sap_voucher.create(offset)

        msg = str(int(time.time()))
        for val in vals:
            val['matdoc'] = msg
            vouchaer_obj.create(val)
        if offset_ids and len(offset_ids):
            for offset in offset_ids:
                offset['matdoc'] = msg
                offset_sap_voucher.create(offset)
        return True