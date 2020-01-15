# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api, exceptions

import logging


class sap_voucher(models.Model):
    _name = "sap.voucher"
    # _description = "SAP凭证"

    ponum = fields.Char("Purchase Order")
    pline = fields.Char("Purchase Order Line")
    dnnum = fields.Char("Delivery Order")
    dline = fields.Char("Delivery Order Line")
    matnr = fields.Many2one('product.product', 'Material', required=True, domain=[('purchase_ok', '=', True)],
                            readonly=True)
    matnrcode = fields.Char("Material Code")
    matnrdesc = fields.Char("Material Desc")
    operation_id = fields.Integer("Operation ID")
    matdoc = fields.Char('Mat Doc')
    movetype = fields.Char('Move type')
    psingdate = fields.Char('PSTNG DATE')
    linemark = fields.Integer("Line Mark")
    pickname = fields.Char("Picking Name")
    refpickname = fields.Char("Reference Picking Name")
    picking_id = fields.Many2one('stock.picking', 'Pick')
    move_id = fields.Integer('Move')
    po_line_id = fields.Integer('Purchase Order Line')
    po_id = fields.Integer('Purchase Order')
    qty = fields.Float('Qty')
    printSendDate = fields.Char('Send Date', readonly=True)
    prnum = fields.Char('Product Order')
    _order = "write_date desc"
    handleQty = fields.Float('Qty',compute="_compute_qty")

    @api.multi
    def _compute_qty(self):
        for s in self:
            if s.movetype=='104':
                s.handleQty = -s.qty
            else:
                s.handleQty = s.qty

class offset_sap_voucher(models.Model):
    _name = "offset.sap.voucher"
    matdoc = fields.Char('Mat Doc')
    origin_matdoc = fields.Char('Origin Mat Doc')
    orging_linemark = fields.Integer("Origin Line Mark")
    qty = fields.Float('Qty')