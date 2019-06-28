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

    customer = fields.Boolean(string='Is a Customer', default=False,
                              help="Check this box if this contact is a customer. It can be selected in sales orders.")
    register_no = fields.Char('Registration number')


    _sql_constraints = [
        ('name_unique', 'unique(name)', "The name you entered already exists"),
        ('register_no_unique', 'unique(register_no)', "The Duty paragraph you entered already exists"),
    ]

    @api.onchange('name')
    def onchange_name(self):
        name = self.name
        count = self.env['e2yun.customer.info'].sudo().search_count([('name','=',name)])
        if count > 0:
            self.name = False
            msg = _("The name you entered already exists for potential customers.")
            return {
                'warning': {
                    'title': _('Tips'),
                    'message': msg
                }
            }

    @api.onchange('register_no')
    def onchange_register_no(self):
        register_no = self.register_no
        if register_no:
            count = self.env['e2yun.customer.info'].sudo().search_count([('register_no', '=', register_no)])
            if count > 0:
                self.register_no = False
                msg = _("The Duty paragraph you entered already exists for potential customers.")
                return {
                    'warning': {
                        'title': _('Tips'),
                        'message': msg
                    }
                }