# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions

class stock_package(models.Model):
    _inherit = 'stock.quant.package'

    lifnr = fields.Many2one('res.partner', 'Supplier', required=False, readonly=True, domain=[('supplier', '=', True)])

    def search(self,args, offset=0, limit=None, order=None, count=False):
        if self._context is None:
            context = {}
        lifnr= self.env['res.users']._get_default_supplier()
        if lifnr > 0:
            args += [('lifnr', '=', lifnr)]

        return super(stock_package, self).search(
            args, offset=offset, limit=limit, order=order,
            count=count)

class stock_pack_operation(models.Model):
    _inherit = 'stock.pack.operation'

    prnum = fields.Char('Produce Order')
    dnnum = fields.Many2one('delivery.order', 'Delivery Order', readonly=True)
    lifnr = fields.Many2one('res.partner', 'Supplier', required=False, readonly=True, domain=[('supplier', '=', True)])
