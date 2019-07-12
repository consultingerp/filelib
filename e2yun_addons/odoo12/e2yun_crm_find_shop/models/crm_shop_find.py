# -*- coding: utf-8 -*-

from odoo import api, fields, models, _,exceptions
import werkzeug.utils
from odoo import http

class CrmTeamADDinformation(models.Model):
    _inherit = ['crm.team']

    color = fields.Integer('Color Index')

    # user_city = fields.Char(compute='the_same_city')



    # @api.model
    # def _get_the_user_city(self):
    #     context = self._context.copy()
    #     uid = context.get('uid')
    #     user = self.env['res.users'].search([('uid', '=', uid)])
    #     city = user.partner_id.city
    #     self.env.context.update({"user_city": city})

    def button_navigation(self):
        # raise exceptions.Warning(_("hhhhhhhhhhh！"))
        # return werkzeug.utils.redirect('/map')
        return {
            'type': 'ir.actions.act_url',
            'url': '/map',
            'target': 'self',
            'res_id': self.id,
        }

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        new_context = self.env.context.copy()
        uid = new_context.get('uid')
        user = self.env['res.users'].search([('id', '=', uid)])
        city = user.partner_id.city

        new_context.update({"user_city": city})
        self.with_context(new_context)
        return super(CrmTeamADDinformation, self).search_read(domain, fields, offset, limit, order)