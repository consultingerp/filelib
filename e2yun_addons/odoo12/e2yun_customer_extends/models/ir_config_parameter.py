# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.tools.translate import _

PARAMS = [
    ('e2yun.sync_pos_member_webservice_url', 'http://127.0.0.1:8080/lhjc/esb/webservice/SyncMember?wsdl'),
    ('crm.intention_customer_msg_day', 1),
    ('crm.target_customer_msg_day', 2),
]


def get_e2yun_parameters_env(env):
    res = {}
    for param, default in PARAMS:
        value = env['ir.config_parameter'].sudo().get_param(param, default)
        res[param] = value.strip()
    return res


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def get_e2yun_parameters(self):
        return get_e2yun_parameters_env(self.env)

    @api.model
    def create_e2yun_parameters(self):
        for param, default in PARAMS:
            if not self.env['ir.config_parameter'].sudo().get_param(param):
                self.env['ir.config_parameter'].sudo().set_param(param, default or ' ')
