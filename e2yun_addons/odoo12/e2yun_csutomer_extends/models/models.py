# -*- coding: utf-8 -*-

from odoo import models, fields, api

class E2yunCsutomerExtends(models.Model):
    _inherit = 'res.partner'

    app_code = fields.Char(string='')
    shop_code = fields.Char(string='')
    shop_name = fields.Char(string='')
    referrer = fields.Many2one('res.user', string='')
    occupation = fields.Char(string='')
    car_brand = fields.Char(string='')
    user_nick_name = fields.Char(string='')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ], string='')
    customer_source = fields.Selection([
        ('barcode', 'Barcode'),
        ('manual', 'Manual'),
    ], string='', default='manual')

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100