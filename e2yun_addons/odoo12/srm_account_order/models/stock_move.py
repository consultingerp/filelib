# -*- coding: utf-8 -*-

from odoo import models,fields
import odoo.addons.decimal_precision as dp


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    confirm_transfer = fields.Boolean('确认收货', copy=False,default=False)



class StockMove(models.Model):
    _inherit = 'stock.move'

    account_qty= fields.Float('已开票数量', digits=dp.get_precision('Product Unit of Measure'), copy=False,default=0)
    tax_id= fields.Integer('税')
    remark= fields.Char('备注')
    picking_partner= fields.Many2one('res.partner', 'Partner', related='picking_id.partner_id')
    confirm_transfer= fields.Boolean('confirm_transfer', related='picking_id.confirm_transfer', copy=False)
    picking_state= fields.Selection([('draft', 'New'),
                                       ('cancel', 'Cancelled'),
                                       ('waiting', 'Waiting Another Move'),
                                       ('confirmed', 'Waiting Availability'),
                                       ('assigned', 'Available'),
                                       ('done', 'Done'),
                                       ], 'Picking Status', related='picking_id.state')
    def _get_invoice_line_vals(self,move, partner, inv_type):

        rtn = super(StockMove, self)._get_invoice_line_vals(move, partner, inv_type)
        partial_quantity_lines = self._context['partial_quantity_lines']
        quantity = partial_quantity_lines.get(move.id)
        rtn['quantity'] = quantity
        rtn['move_id'] = move.id
        return rtn

    def _get_taxes(self,move):
        if move.origin_returned_move_id.purchase_line_id.taxes_id:
            return [tax.id for tax in move.origin_returned_move_id.purchase_line_id.taxes_id]
        elif move.purchase_line_id.taxes_id:
            return [tax.id for tax in move.purchase_line_id.taxes_id]
        elif move.tax_id:
            return [move.tax_id]
        return super(StockMove, self)._get_taxes(move)