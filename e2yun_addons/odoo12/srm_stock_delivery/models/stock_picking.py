from odoo import models,api,exceptions
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare, float_round
import datetime
import time
try:
    from odoo.addons.srm_pyrfc import ZSRM_BAPI_GOODSMVT_CREATE
except:
    pass
class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        for s in self:
            if s.picking_type_id.code == 'incoming':
                raise exceptions.ValidationError("收货作业必须通过交货单操作")

        return super(stock_picking, self).button_validate()
    
    def sapdo_po_transfer(self):
        patng_date = str(datetime.date.today()).replace('-', '')
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
        des_loc_usage = self.move_lines[0].location_dest_id.usage
        if des_loc_usage == 'supplier':
            transfer_type = '104'

        po_ids = []

        sql = """update purchase_order_line set delivery_qty = coalesce(delivery_qty,0) + %s where id = %s """#,the_po=product_qty-(coalesce(delivery_qty,0) + %s)
        done_sql = """update delivery_purchase_orders set done_menge = coalesce(done_menge,0) + %s where delivery_order_line_id = %s and pline = %s """

        if transfer_type == '104':
            sql = """update purchase_order_line set delivery_qty = coalesce(delivery_qty,0) - %s where id = %s """ #,the_po=product_qty-(coalesce(delivery_qty) - %s)
            done_sql = """update delivery_purchase_orders set done_menge = coalesce(done_menge,0) - %s where delivery_order_line_id = %s and pline = %s """

        self = self.with_context(lang='en_US')
        for item in self.move_lines:
            if transfer_type == '104' and not item.move_reason:
                raise exceptions.ValidationError("反向调拨必须输入移动原因")

            num += 1
            voucher_id = []
            offset_ids = []
            quantity = item.quantity_done
            if transfer_type == '104':
                voucher_id = vouchaer_obj.search([
                    ('picking_id', '=', item.origin_returned_move_id.picking_id.id),
                    ('move_id', '=', item.origin_returned_move_id.id),
                    ('po_line_id', '=', item.purchase_line_id.id)
                ])

                if len(voucher_id) > 1:
                    for voucher in voucher_id:
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
                    voucher = voucher_id
                    offset_ids.append({'origin_matdoc': voucher.matdoc, 'origin_linemark': voucher.linemark,
                                       'qty': item.quantity_done})
                voucher = voucher_id[0]


            if voucher.po_id not in po_ids:
                po_ids.append(voucher.po_id)

            self._cr.execute(sql, (item.quantity_done,item.purchase_line_id.id))
            if voucher:
                self._cr.execute(done_sql, (item.quantity_done, voucher.dline,voucher.po_line_id))

            val = {
                'ponum': item.origin_returned_move_id.purchase_line_id.order_id.name,
                'pline': str(item.origin_returned_move_id.purchase_line_id.item),
                'dnnum': voucher.dnnum,
                'dline': voucher.dline,
               # 'operation_id': item.packop_id.id,
                'movetype': transfer_type,
                'psingdate': patng_date,
                'linemark': num,
                'pickname': self.name,
                'picking_id': self.id,
                'move_id': item.id,
                'po_line_id': voucher.po_line_id,
                'move_reason' : item.move_reason,
                'po_id' : voucher.po_id,
                'qty' : item.quantity_done,
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
                        'MATERIAL': item.product_id.default_code,
                         'PLANT': self.company_id.company_code,
                         'MOVE_TYPE': str(transfer_type),
                         'ENTRY_UOM': item.product_uom.name,
                         'ENTRY_QNT': offset['qty'],
                         'PO_NUMBER': str(val['ponum']),
                         'PO_ITEM': str(val['pline']),
                         'MVT_IND': 'B',
                         'REF_DOC': str(offset['origin_matdoc']),
                         'REF_DOC_IT': str(offset['origin_linemark']),
                         'MOVE_REAS': item.move_reason or ''
                     }
                    GOODSMVT_ITEM.append(GOODSMVT_ITEM_MAP)

            else:
                GOODSMVT_ITEM_MAP = {
                    'MATERIAL': item.product_id.default_code,
                     'PLANT': self.company_id.company_code,
                     'MOVE_TYPE': str(transfer_type),
                     'ENTRY_UOM': item.product_uom.name,
                     'ENTRY_QNT': item.quantity_done,
                     'PO_NUMBER': str(val['ponum']),
                     'PO_ITEM': str(val['pline']),
                     'MVT_IND': 'B',
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
                    return_moves = move_obj.browse(self.move_lines.ids)
                    for m in return_moves:
                        move_id = move_obj.search([('picking_id','=',picking_obj.id),('purchase_line_id','=',m.purchase_line_id.id)])
                        if move_id:
                            move = move_id[0]
                            move.product_uom_qty = move.product_uom_qty + m.product_uom_qty
                            #move.product_uos_qty = move.product_uos_qty + m.product_uos_qty
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
                    return_moves = move_obj.browse(self.move_lines.ids)

                    new_picking_id = self.copy({
                        'state': 'assigned',
                        'picking_type_id': self.picking_type_id.return_picking_type_id.id,
                        'origin': (self.origin + '-' + self.name)
                        #'invoice_state': self.invoice_state,
                    })
                    new_moves = new_picking_id.move_lines

                    i = 0
                    for return_move in return_moves:
                        if new_moves[i]:
                            new_moves[i].write({
                                'location_id': return_move.location_dest_id.id,
                                'location_dest_id': return_move.location_id.id,
                                'state': 'waiting',
                                # 'move_dest_id': return_move.origin_returned_move_id.move_dest_id.id or
                                #                 return_move.origin_returned_move_id.move_dest_id,
                                'origin_returned_move_id': return_move.origin_returned_move_id.id,
                                #'procure_method': return_move.origin_returned_move_id.procure_method,
                                'picking_type_id': return_move.origin_returned_move_id.picking_type_id.id,
                                'purchase_line_id': return_move.origin_returned_move_id.purchase_line_id.id,
                            })

                        i = i + 1
                    new_picking_id.action_assign()
        elif transfer_type == '103':
            for order in order_obj.browse(po_ids):
                picking_obj = None
                for picking in order.picking_ids:
                    if picking.state != 'done':
                        picking_obj = picking
                        break
                if picking_obj:
                    return_moves = self.move_lines
                    for m in return_moves:
                        move_id = move_obj.search([('picking_id','=',picking_obj.id),('purchase_line_id','=',m.purchase_line_id.id)])
                        if move_id:
                            move = move_id[0]
                            move.product_uom_qty = move.product_uom_qty - m.product_uom_qty
                            move.product_uos_qty = move.product_uos_qty - m.product_uos_qty

        GOODSMVT_HEADER['HEADER_TXT'] = '交货单'+ GOODSMVT_HEADER.get('REF_DOC_NO','')
        # zbapi_goodsmvt_create = ZSRM_BAPI_GOODSMVT_CREATE.ZBAPI_GOODSMVT_CREATE()
        # result_rfc = zbapi_goodsmvt_create.BAPI_GOODSMVT_CREATE(self._cr,GOODSMVT_HEADER, GOODSMVT_ITEM,'01')
        result_rfc = {
            'code':0,
            'MAT_DOC':int(time.time())
        }

        if result_rfc['code'] == 1:
            msg = result_rfc['message']
            raise exceptions.ValidationError(" SAP调拨过账失败，失败原因：%s" % (msg))
        else:
            msg = result_rfc['MAT_DOC']
            for val in vals:
                val['matdoc'] = msg
                vouchaer_obj.create(val)
            if offset_ids and len(offset_ids):
                for offset in offset_ids:
                    offset['matdoc'] = msg
                    offset_sap_voucher.create(offset)
        return result_rfc

    @api.multi
    def action_done(self):
        super(stock_picking,self).action_done()

        if self.purchase_id.order_line[0].ret_item:
            return self.sapdo_po_ref()
        if self.purchase_id.order_line[0].item_cat:
            return self.sapdo_po_outsourcing()

        transfer_type = '103'
        des_loc_usage = self.move_lines[0].location_dest_id.usage
        if des_loc_usage == 'supplier':
            transfer_type = '104'
        if transfer_type == '104':
            return self.sapdo_po_transfer()
        else:
            return True


    def sapdo_po_ref(self):
        # 退货订单退货
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
        transfer_type = '101'
        movetype='161'

        des_loc_usage = self.move_lines[0].location_dest_id.usage

        sql = "update purchase_order_line set delivery_qty = coalesce(delivery_qty,0) + %s,the_po=product_qty-(coalesce(delivery_qty,0) + %s) where id = %s "
        # if des_loc_usage == 'internal':
        #     transfer_type = '102'
        #     movetype=162
        #     sql = "update purchase_order_line set delivery_qty = coalesce(delivery_qty,0) - %s,the_po=product_qty-(coalesce(delivery_qty,0) - %s) where id = %s "

        po_ids = []

        self = self.with_context(lang='en_US')
        for item in self.move_lines:
            if item.quantity_done <= 0:
                continue

            num += 1
            voucher_id = []
            offset_ids = []
            quantity = item.quantity_done

            po_object=item.purchase_line_id

            val = {
                'ponum': po_object.order_id.name,
                'pline': str(po_object.item),
                'movetype': movetype,
                'psingdate': patng_date,
                'linemark': num,
                'pickname': self.name,
                'picking_id': self.id,
                'move_id': item.id,
                'po_line_id': po_object.id,
                'move_reason': item.move_reason or '',
                'po_id': po_object.order_id.id,
                'qty': quantity,
                'matnr': po_object.product_id.id,
                'matnrcode': po_object.product_id.code,
                'matnrdesc': ''
            }
            vals.append(val)
            GOODSMVT_HEADER['REF_DOC_NO'] = '00000'
            werks=''
            lgort=''
            if transfer_type=='102':
                if item.location_dest_id.barcode:
                 loc_barcode=item.location_dest_id.barcode.split('-')
                 werks=loc_barcode[0]
                 lgort=loc_barcode[1]
                else:
                  raise exceptions.ValidationError("调拨请配置工厂与库存地点")
            else:
                if item.location_id.barcode:
                    loc_barcode = item.location_id.barcode.split('-')
                    werks = loc_barcode[0]
                    lgort = loc_barcode[1]
                else:
                    raise exceptions.ValidationError("调拨请配置工厂与库存地点")

            if transfer_type == '102':
                for offset in offset_ids:
                    GOODSMVT_ITEM_MAP = {
                        'MATERIAL':item.product_id.code,
                        'PLANT': werks,
                        'STGE_LOC': lgort,
                        'MOVE_TYPE': str(transfer_type),
                        'ENTRY_UOM': item.product_uom.name,
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
                    'MATERIAL': item.product_id.code,
                    'PLANT': werks,
                    'STGE_LOC':lgort,
                    'MOVE_TYPE': str(transfer_type),
                    'ENTRY_UOM': item.product_uom.name,
                    'ENTRY_QNT': item.quantity_done,
                    'PO_NUMBER': item.purchase_line_id.order_id.name,
                    'PO_ITEM': item.purchase_line_id.item,
                    'MVT_IND': str('B'),
                    'MOVE_REAS': item.move_reason or ''
                }

                GOODSMVT_ITEM.append(GOODSMVT_ITEM_MAP)
            #self._cr.execute(sql, (item.quantity_done, item.quantity_done, item.purchase_line_id.id))
        self = self.with_context(lang='zh_CN')

        if transfer_type == '102':
            for id in po_ids:
                self._cr.execute("""update purchase_order set state = 'supply_confirm' where id = %(id)s """,
                                 {'id': id})
        else:
            order_line_obj = self.env['purchase.order.line']
            for order in order_line_obj.browse(po_ids):
                is_done = True
                for line in order.order_line:
                    if line.product_qty > line.delivery_qty:
                        is_done = False
                if is_done:
                    order.state = 'outgoing'

        GOODSMVT_HEADER['HEADER_TXT'] = '退货订单' + GOODSMVT_HEADER.get('REF_DOC_NO','')
        # zbapi_goodsmvt_create = ZSRM_BAPI_GOODSMVT_CREATE.ZBAPI_GOODSMVT_CREATE()
        # result_rfc = zbapi_goodsmvt_create.BAPI_GOODSMVT_CREATE(self._cr, GOODSMVT_HEADER, GOODSMVT_ITEM, '01')
        result_rfc = {
            'code':0,
            'MAT_DOC':int(time.time())
        }

        if result_rfc['code'] == 1:
            msg = result_rfc['message']
            raise exceptions.ValidationError(" SAP调拨过账失败，失败原因：%s" % (msg))
        else:
            msg = result_rfc['MAT_DOC']
            for val in vals:
                val['matdoc'] = msg
                vouchaer_obj.create(val)
            if offset_ids and len(offset_ids):
                for offset in offset_ids:
                    offset['matdoc'] = msg
                    offset_sap_voucher.create(offset)



    def sapdo_po_outsourcing(self):
        # 外协订单收货
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
        transfer_type = '101'
        movetype='101'
        des_loc_usage = self.move_lines[0].location_dest_id.usage
        gm_code='01'

        # 更新PO剩余数量
        sql = "update purchase_order_line set delivery_qty = coalesce(delivery_qty,0) + %s,the_po=product_qty-(coalesce(delivery_qty,0) + %s) where id = %s "

        if 'supplier' == des_loc_usage:
            #反调拨
            transfer_type=542
            movetype=542
            gm_code='04'
            sql = "update purchase_order_line set delivery_qty = coalesce(delivery_qty,0) - %s,the_po=product_qty-(coalesce(delivery_qty,0) - %s) where id = %s "

        order_id=self.move_lines[0].purchase_line_id.order_id
        po_ids=[]
        po_ids.append(order_id)
        self = self.with_context(lang='en_US')
        for item in self.move_lines:
            quantity = item.quantity_done
            if quantity<=0:
                continue
            num += 1
            voucher_id = []
            offset_ids = []

            #退回找原凭证
            if transfer_type == '102':
                voucher_id = vouchaer_obj.search(self._cr, self._uid, [
                    ('picking_id', '=', item.move_id.origin_returned_move_id.picking_id.id),
                    ('move_id', '=', item.move_id.origin_returned_move_id.id),
                    ('po_line_id', '=', item.move_id.purchase_line_id.id)
                ])
                if len(voucher_id) > 1:
                    for voucher in vouchaer_obj.browse(self._cr, self._uid, voucher_id):
                        offset_id = offset_sap_voucher.search(self._cr, self._uid, [
                            ('origin_matdoc', '=', voucher.matdoc),
                            ('orging_linemark', '=', voucher.linemark)
                        ])
                        offset_qty = 0
                        for offset in offset_sap_voucher.browse(self._cr, self._uid, offset_id):
                            offset_qty += offset.qty

                        if quantity <= voucher.qty - offset_qty:
                            offset_ids.append(
                                {'origin_matdoc': voucher.matdoc, 'origin_linemark': voucher.linemark, 'qty': quantity})
                            quantity = 0
                        else:
                            offset_ids.append(
                                {'origin_matdoc': voucher.matdoc, 'origin_linemark': voucher.linemark,
                                 'qty': voucher.qty - offset_qty})

                            quantity = quantity - voucher.qty - offset_qty

                        if quantity <= 0:
                            break;
                else:
                    voucher = vouchaer_obj.browse(self._cr, self._uid, voucher_id)
                    offset_ids.append({'origin_matdoc': voucher.matdoc, 'origin_linemark': voucher.linemark,
                                       'qty': item.quantity})
                voucher = vouchaer_obj.browse(self._cr, self._uid, voucher_id[0])

            po_object=item.purchase_line_id
            val = {
                'ponum': po_object.order_id.name,
                'pline': str(po_object.item),
               # 'operation_id': item.packop_id.id,
                'movetype': movetype,
                'psingdate': patng_date,
                'linemark': num,
                'pickname': self.name,
                'picking_id': self.id,
                'move_id': item.id,
                'po_line_id': po_object.id,
                'move_reason': item.move_reason,
                'po_id': po_object.order_id.id,
                'qty': item.quantity_done,
                'matnr': po_object.product_id.id,
                'matnrcode': po_object.product_id.code,
                'matnrdesc': ''
            }
            vals.append(val)

            GOODSMVT_HEADER['REF_DOC_NO'] = '00000'

            werks=''
            lgort=''

            if transfer_type=='101':
                if item.location_dest_id.barcode:
                    loc_barcode = item.location_dest_id.barcode.split('-')
                    werks = loc_barcode[0]
                    lgort = loc_barcode[1]
                else:
                  raise exceptions.ValidationError("调拨请配置工厂与库存地点")
            else:
                if item.sourceloc_id.loc_barcode:
                    loc_barcode = item.sourceloc_id.loc_barcode.split('-')
                    werks = loc_barcode[0]
                    lgort = loc_barcode[1]
                else:
                    raise exceptions.ValidationError("调拨请配置工厂与库存地点")

            if transfer_type == '102':
                for offset in offset_ids:
                    GOODSMVT_ITEM_MAP = {
                        'MATERIAL': item.product_id.code,
                        'PLANT': werks,
                        'STGE_LOC': lgort,
                        'MOVE_TYPE': str(transfer_type),
                        'ENTRY_UOM': item.product_uom.name,
                        'ENTRY_QNT': offset['qty'],
                        'PO_NUMBER': str(val['ponum']),
                        'PO_ITEM': str(val['pline']),
                        'MVT_IND': 'B',
                        'REF_DOC': str(offset['origin_matdoc']),
                        'REF_DOC_IT': str(offset['origin_linemark']),
                        'MOVE_REAS': item.move_reason or ''
                    }
                    GOODSMVT_ITEM.append(GOODSMVT_ITEM_MAP)
            else:
                GOODSMVT_ITEM_MAP = {
                   'MATERIAL': item.product_id.code,
                    'PLANT': werks,
                    'STGE_LOC':lgort,
                    'MOVE_TYPE': str(transfer_type),
                    'ENTRY_UOM': item.product_uom.name,
                    'ENTRY_QNT': item.quantity_done,
                    'PO_NUMBER': item.purchase_line_id.order_id.name,
                    'PO_ITEM': item.purchase_line_id.item,
                    'MOVE_REAS': item.move_reason or ''
                }
                if transfer_type=='101':
                    GOODSMVT_ITEM_MAP['MVT_IND']='B'

                GOODSMVT_ITEM.append(GOODSMVT_ITEM_MAP)
           #self._cr.execute(sql, (item.quantity, item.quantity, item.move_id.purchase_line_id.id))
        self = self.with_context(lang='zh_CN')
        # if transfer_type == '102':
        #     for id in po_ids:
        #         self._cr.execute("""update purchase_order set state = 'supply_confirm' where id = %(id)s """,
        #                          {'id': id})
        # else:
        #     for order in order_obj.browse( po_ids):
        #         is_done = True
        #         for line in order.order_line:
        #             if line.product_qty > line.delivery_qty:
        #                 is_done = False
        #         if is_done:
        #             order.state = 'outgoing'


        GOODSMVT_HEADER['HEADER_TXT'] = '外协订单' + GOODSMVT_HEADER.get('REF_DOC_NO','')
        # zbapi_goodsmvt_create = ZSRM_BAPI_GOODSMVT_CREATE.ZBAPI_GOODSMVT_CREATE()
        # result_rfc = zbapi_goodsmvt_create.BAPI_GOODSMVT_CREATE(self._cr, GOODSMVT_HEADER, GOODSMVT_ITEM, gm_code)

        result_rfc = {
            'code':0,
            'MAT_DOC':int(time.time())
        }
        if result_rfc['code'] == 1:
            msg = result_rfc['message']
            raise exceptions.ValidationError(" SAP调拨过账失败，失败原因：%s" % (msg))
        else:
            msg = result_rfc['MAT_DOC']
            for val in vals:
                val['matdoc'] = msg
                vouchaer_obj.create( val)
            if offset_ids and len(offset_ids):
                for offset in offset_ids:
                    offset['matdoc'] = msg
                    offset_sap_voucher.create(offset)
        return result_rfc;
