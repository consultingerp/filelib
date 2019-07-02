# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api


class CrmLeadLine(models.Model):
    _inherit = "crm.lead.line"

    # 含税金额
    price_tax = fields.Float(string='Total Tax', store=True)

    # 税率
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    # 不含税金额
    price_subtotal = fields.Float(string='Subtotal',compute='_onchange_tax_id', redonly='True', store=True)

    cgm = fields.Float(string='CGM%')
    pid = fields.Char(string='PID')
    contract_number = fields.Char(string='Contract Number')

    @api.onchange('tax_id','price_tax')
    def _onchange_tax_id(self):
        for line in self:
            taxes = line.price_tax / (line.tax_id.amount / 100 + 1)
            line.price_subtotal = taxes



    def write(self, vals):
        super(CrmLeadLine,self).write(vals)
        taxes=self.price_tax / (self.tax_id.amount / 100 + 1)
        if not taxes:
            taxes=self.price_tax
        vals['price_subtotal'] = taxes
        super(CrmLeadLine, self).write(vals)

    def create(self, vals_list):
        crmlead=super(CrmLeadLine, self).create(vals_list)
        for leadlin in crmlead:
            taxes = leadlin.price_tax / (leadlin.tax_id.amount / 100 + 1)
            if not taxes:
                taxes = leadlin.price_tax
            vals={}
            vals['price_subtotal'] = taxes
            super(CrmLeadLine, leadlin).write(vals)