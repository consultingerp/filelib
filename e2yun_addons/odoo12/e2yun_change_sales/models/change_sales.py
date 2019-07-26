# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class E2yuncChangeSales(models.Model):

    _name = 'change.sales'

    originsale = fields.Many2one('res.users', string='离职导购')
    newsale = fields.Many2one('res.users', string='新导购')

    @api.one
    def old_sale_has_gone(self):
        ori = self.originsale.id
        new = self.newsale.id
        need_change_customers = self.env['res.partner'].search([('user_id', '=', ori)])
        try:
            for need_change_cus in need_change_customers:
                need_change_cus.update({'user_id': new})
        except Exception as e:
            raise e
