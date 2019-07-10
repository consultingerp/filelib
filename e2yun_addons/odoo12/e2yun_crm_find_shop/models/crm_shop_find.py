# -*- coding: utf-8 -*-

from odoo import api, fields, models, _,exceptions
import werkzeug.utils
from odoo import http

class CrmTeamADDinformation(models.Model):
    _inherit = ['crm.team']

    color = fields.Integer('Color Index')

    user_city = fields.Char(compute='the_same_city')

    @api.one
    def the_same_city(self):
        user = self.env.user
        partner_of_user = user.partner_id
        city = partner_of_user.city
        self.user_city = city

    def button_navigation(self):
        # raise exceptions.Warning(_("hhhhhhhhhhh！"))
        # return werkzeug.utils.redirect('/map')
        return {
            'type': 'ir.actions.act_url',
            'url': '/map',
            'target': 'self',
            'res_id': self.id,
        }