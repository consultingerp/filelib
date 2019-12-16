# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_commission = fields.Boolean("Apply Global Commission", default=False)
    commission_value = fields.Integer("Commission", default=0)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        is_commission = ICPSudo.get_param('odoo_website_marketplace.is_commission')
        commission_value = int(ICPSudo.get_param('odoo_website_marketplace.commission_value', default=0))
        res.update(
            is_commission=is_commission,
            commission_value=commission_value,)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('odoo_website_marketplace.is_commission',self.is_commission)
        ICPSudo.set_param('odoo_website_marketplace.commission_value',str(self.commission_value))