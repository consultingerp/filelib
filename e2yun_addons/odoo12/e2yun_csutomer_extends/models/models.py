# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class E2yunCsutomerExtends(models.Model):
    _inherit = 'res.partner'

    app_code = fields.Char(string='', copy=False, readonly=True, default=lambda self: _('New'))
    shop_code = fields.Char(string='')
    shop_name = fields.Char(string='')
    referrer = fields.Many2one('res.users', string='')
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

    @api.model
    def create(self, vals):
        if vals.get('app_code', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['app_code'] = self.env['ir.sequence'].with_context(force_company=vals['company_id'])\
                                   .next_by_code('app.code') or _('New')
            else:
                vals['app_code'] = self.env['ir.sequence'].next_by_code('app.code') or _('New')

        result = super(E2yunCsutomerExtends, self).create(vals)
        return result

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100