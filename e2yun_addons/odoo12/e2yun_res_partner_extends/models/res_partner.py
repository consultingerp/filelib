# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    @api.multi
    def _compute_strategic_edit(self):
        is_edit = False
        if self.user_has_groups('e2yun_customer_info.group_crm_sale_lead'):
            is_edit = True
        for s in self:
            s.strategic_edit = is_edit

    parent_account = fields.Many2one('res.partner',string='Parent Account',domain="[('customer','=',True)]")
    is_strategic = fields.Boolean(string='Is Strategic')
    strategic_edit = fields.Boolean(string='Strategic Edit',compute=_compute_strategic_edit)


    _sql_constraints = [
        ('name_unique', 'unique(name)', "The name you entered already exists"),
        ('vat_unique', 'unique(vat)', "The Duty paragraph you entered already exists"),
    ]

    @api.onchange('name')
    def onchange_name(self):
        name = self.name
        count = self.env['e2yun.customer.info'].search_count([('name','=',name)])
        if count > 0:
            self.name = False
            msg = _("The name you entered already exists for potential customers.")
            return {
                'warning': {
                    'title': _('Tips'),
                    'message': msg
                }
            }

    @api.onchange('vat')
    def onchange_vat(self):
        vat = self.vat
        if vat:
            count = self.env['e2yun.customer.info'].search_count([('vat', '=', vat)])
            if count > 0:
                self.vat = False
                msg = _("The Duty paragraph you entered already exists for potential customers.")
                return {
                    'warning': {
                        'title': _('Tips'),
                        'message': msg
                    }
                }