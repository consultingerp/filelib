# -*- coding: utf-8 -*-

from odoo import models, fields, api

class crm_address_format(models.Model):
    # _name = 'crm_address_format.crm_address_format'
    _inherit = 'crm.lead'
    city_id = fields.Many2one('res.state.city', string='City')
    area_id = fields.Many2one('res.city.area', string='Area')
    street = fields.Char('Street')
    # value2 = fields.Float(compute="_value_pc", store=True)
    # description = fields.Text()

#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100