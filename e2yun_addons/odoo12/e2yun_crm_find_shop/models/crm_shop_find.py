# -*- coding: utf-8 -*-

from odoo import api, fields, models, _,exceptions
import werkzeug.utils
from odoo import http

class CrmTeamADDinformation(models.Model):
    _inherit = ['crm.team']

    color = fields.Integer('Color Index')

    # user_city = fields.Char(compute='the_same_city')

    def button_navigation(self):
        # raise exceptions.Warning(_("hhhhhhhhhhh！"))
        # return werkzeug.utils.redirect('/map')
        return {
            'type': 'ir.actions.act_url',
            'url': '/map',
            'target': 'self',
            'res_id': self.id,
        }

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     new_context = self.env.context.copy()
    #     uid = new_context.get('uid')
    #     user = self.env['res.users'].search([('id', '=', uid)])
    #     city = user.partner_id.city
    #
    #     new_context.update({"user_city": city})
    #     self.with_context(new_context)
    #     return super(CrmTeamADDinformation, self).search_read(domain, fields, offset, limit, order)

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='kanban', toolbar=False, submenu=False):
    #     res = super(CrmTeamADDinformation, self).fields_view_get(view_id, view_type, toolbar, submenu)
    #     new_ctx = self.env.context.copy()
    #     view_id = res.get('view_id')
    #     new_ctx.update({'view_id': view_id})
    #     self.with_context(new_ctx)
    #     return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain:
            if ['id', '!=', None] in domain:
                domain.remove(['id', '!=', None])
                domain.append(('city', '=', self.env.user.partner_id.city))
        #     serach_read = super(CrmTeamADDinformation, self).search_read(domain, fields, offset, limit, order)
        #     user = self.env.user
        #     user_city = user.partner_id.city
        #     crm_team_pool = self.env['crm.team'].search([('city', '=', user_city)])
        #     team_id = []
        #     search_read_new = []
        #     for crm_team in crm_team_pool:
        #         team_id.append(crm_team.id)
        #     for item in serach_read:
        #         if item.get('id') in team_id:
        #             search_read_new.append(item)
        #         else:
        #             continue
        #     return search_read_new
        # else:
        return super(CrmTeamADDinformation, self).search_read(domain, fields, offset, limit, order)