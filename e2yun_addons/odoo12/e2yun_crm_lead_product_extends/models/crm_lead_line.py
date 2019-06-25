# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api

class CrmLeadLine(models.Model):
    _inherit = "crm.lead.line"

    #含税金额
    price_tax = fields.Float(string='Total Tax',store=True)

    #税率
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    #不含税金额
    price_subtotal = fields.Float(string='Subtotal', readonly=True, store=True)


    @api.onchange('price_tax')
    def _onchange_price_tax(self):
        for line in self:
            taxes = line.price_tax / (line.tax_id.amount / 100 + 1)
            line.update({
                'price_subtotal': taxes  # 不含税金额
            })
    @api.onchange('tax_id')
    def _onchange_tax_id(self):
        for line in self:
            taxes = line.price_tax / (line.tax_id.amount / 100 + 1)
            line.update({
                'price_subtotal': taxes  # 不含税金额
            })



