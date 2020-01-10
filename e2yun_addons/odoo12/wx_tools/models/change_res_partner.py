# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ChangeResPartner(models.Model):
    _name = 'change.partner'
    _description = '更改客户向导'

    partner_id = fields.Many2one('res.partner', '新客户')

    def userschangepartner(self):
        new_partnerid = self.partner_id.id

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')
        will_change = self.env[active_model].browse(active_ids)

        try:
            for need_change_id in will_change:
                old_partner = need_change_id.partner_id
                need_change_id.update({'partner_id': new_partnerid,
                                       'wx_user_id': need_change_id.wx_user_id})
                old_partner.wx_user_id = None
        except Exception as e:
            raise e
