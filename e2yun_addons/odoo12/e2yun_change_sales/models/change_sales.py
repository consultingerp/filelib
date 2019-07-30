# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class E2yuncChangeSales(models.TransientModel):
    _name = 'change.sales'

    newsale = fields.Many2one('res.users', string='新导购')

    def old_sale_has_gone(self):

        new = self.newsale.id

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')
        will_change = self.env[active_model].browse(active_ids)

        try:
            for need_change_id in will_change:
                need_change_id.update({'user_id': new})
        except Exception as e:
            raise e
