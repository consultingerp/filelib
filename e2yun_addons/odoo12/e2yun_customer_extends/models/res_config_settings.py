# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    intention_customer_msg_day = fields.Integer('Intention Customer Message Day',default=1)
    target_customer_msg_day = fields.Integer('Target Customer Message Day',default=2)

    @api.model
    def _get_intention_customer_msg_day(self):
        intention_customer_msg_day = self.env['ir.config_parameter'].sudo().get_param('crm.intention_customer_msg_day',1)
        return intention_customer_msg_day

    @api.model
    def _get_target_customer_msg_day(self):
        target_customer = self.env['ir.config_parameter'].sudo().get_param('crm.target_customer_msg_day',2)
        return target_customer

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        intention_customer_msg_day = self.intention_customer_msg_day
        target_customer_msg_day = self.target_customer_msg_day
        self.env['ir.config_parameter'].sudo().set_param('crm.intention_customer_msg_day',intention_customer_msg_day)
        self.env['ir.config_parameter'].sudo().set_param('crm.target_customer_msg_day',target_customer_msg_day)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            intention_customer_msg_day = int(self.env['ir.config_parameter'].sudo().get_param('crm.intention_customer_msg_day','1')),
            target_customer_msg_day = int(self.env['ir.config_parameter'].sudo().get_param('crm.target_customer_msg_day','2')),
        )
        return res
