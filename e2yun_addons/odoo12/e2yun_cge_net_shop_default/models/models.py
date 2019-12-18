# -*- coding: utf-8 -*-

from odoo import models, fields, api

class e2yun_cge_net_shop_default(models.Model):
    _inherit = 'res.partner'

    is_company = fields.Boolean(default=True)

    # @api.model
    # def _set_cge_user_id(self):
    #     flag = self.env.context.get('cge_set_default_user_id', False)
    #     if flag == 439901:
    #         now_user = self.env.user.id
    #         return now_user
    #
    # user_id = fields.Many2one('res.users', string='Salesperson',
    #   help='The internal user in charge of this contact.', default=_set_cge_user_id)

    @api.model
    def default_get(self, fields_list):
        flag = self.env.context.get('cge_set_default_user_id', False)
        if flag == 439901:
            res = super(e2yun_cge_net_shop_default, self).default_get(fields_list)
            res.update({'user_id': self.env.user.id})
            return res
        else:
            return super(e2yun_cge_net_shop_default, self).default_get(fields_list)
