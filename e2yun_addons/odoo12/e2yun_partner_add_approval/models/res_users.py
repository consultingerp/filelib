# -*- coding: utf-8 -*-
from odoo import models,fields,api,exceptions

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _signup_create_user(self, values):
        new_user = super(ResUsers, self)._signup_create_user(values)
        new_user.partner_id.new_signup = 'new_signup'
        return new_user

