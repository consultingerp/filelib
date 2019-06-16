# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    parent_account = fields.Many2one('res.partner',string='Parent Account',domain="[('customer','=',True)]")
    is_strategic = fields.Boolean('Is Strategic')

    @api.onchange("is_strategic")
    def onchange_is_strategic(self):
        is_head = False
        if self.user_has_groups('crm.group_crm_head'):
            is_head = True
        if not is_head:
            if self.is_strategic:
                self.is_strategic = False
            else:
                self.is_strategic = True

    _sql_constraints = [
        ('name_unique', 'unique(name)', "The name you entered already exists"),
    ]
