# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api

class Partner(models.Model):
    _inherit = 'res.partner'

    customer_id = fields.Char('Customer Id',copy=False, required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('customer.sequence'))



