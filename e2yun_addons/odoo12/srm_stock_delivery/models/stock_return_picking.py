# -*- encoding: utf-8 -*-
##############################################################################
#
#    Stock picking return module for Odoo
#    Copyright (C) 2015-2017 e2yun (http://www.e2yun.cn)
#    @author liqiang
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api,models, fields
from odoo import exceptions

class stock_transfer_details_items(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    move_reason = fields.Selection([('0001','来料不良'),('0002','输错冲销')],'移动原因')

class stock_move(models.Model):
    _inherit = 'stock.move'

    move_reason = fields.Selection([('0001','来料不良'),('0002','输错冲销')],'移动原因')

class stock_picking_return(models.TransientModel):
    _inherit =   'stock.return.picking'

    @api.model
    def default_get(self,fields):
        res = super(stock_picking_return, self).default_get(fields)
        if 'product_return_moves' in res:
            move_obj = self.env['stock.move']
            for return_move in res['product_return_moves']:
                for product_return_move in return_move:
                    if isinstance(product_return_move,dict):
                        return_move_id = product_return_move['move_id']
                        sql = """select id from stock_move where state !='cancel' and origin_returned_move_id = %s and
                            location_dest_id in (select id from stock_location where usage='supplier')""" %(return_move_id)
                        self._cr.execute(sql)
                        origin_ids = self._cr.dictfetchall();
                        ids = []
                        for origin_id in origin_ids:
                            ids.append(origin_id['id'])
                        qty = 0
                        for move in move_obj.browse(ids):
                            qty += move.product_uom_qty
                        move_qty = self.env['stock.move'].browse(product_return_move['move_id']).product_uom_qty
                        product_return_move['quantity'] = move_qty - qty
        return res


    def _create_returns(self):

        for rm in self.product_return_moves:
            if not rm['move_reason']:
                raise exceptions.ValidationError("退回移动原因不能为空")
        pick_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        return_picking_id, pick_type_id =super(stock_picking_return,self)._create_returns()
        record_id = self._context and self._context.get('active_id', False) or False
        old_pick = pick_obj.browse(record_id)

        return_pick = pick_obj.browse(return_picking_id)
        origin = ''
        if old_pick.origin:
            origin = origin + old_pick.origin
        origin = origin + old_pick.name
        return_pick.write({'origin': origin})

        return_moves = return_pick.move_lines

        if old_pick.group_id:
            return_pick.write({"group_id": old_pick.group_id.id})  # sale picking relation

        for return_move in return_moves:

            origin_id = return_move.origin_returned_move_id

            for rm in self.product_return_moves:
                if rm.move_id.id == origin_id.id:
                    return_move.move_reason = rm.move_reason

            # return_move_id = move_obj.search(cr, uid,
            #                 [('origin_returned_move_id', '=', origin_id.id), ('state', '!=', 'cancel'), ('id', '!=', return_move.id),('invoice_state','=', '2binvoiced')])
            #
            sql = """select id from stock_move where state !='cancel' and origin_returned_move_id = %s and 
                                location_dest_id in (select id from stock_location where usage='supplier')""" % (
                origin_id.id)
            self._cr.execute(sql)
            m_ids = self._cr.dictfetchall();
            ids = []
            for m in m_ids:
                ids.append(m['id'])

            qty = 0
            for move in move_obj.browse(ids):
                qty += move.product_uom_qty
            qty = origin_id.product_uom_qty - qty

            if qty<0:
                raise exceptions.ValidationError("反向调拨数量不是超过源单据可调拨数量.")

            purchase_line_id = return_move.origin_returned_move_id.purchase_line_id
            if return_move and purchase_line_id:
                return_move.write(
                    {"purchase_line_id": purchase_line_id.id})  # purchase picking relation

        return return_picking_id, pick_type_id