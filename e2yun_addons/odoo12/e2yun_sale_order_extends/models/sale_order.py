# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, readonly=True,
                    states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                    help="Pricelist for current sales order.",default=lambda self: self.env['res.company']._company_default_get('sale.order').partner_id.property_product_pricelist)
