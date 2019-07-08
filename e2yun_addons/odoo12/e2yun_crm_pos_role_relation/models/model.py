# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class model(models.Model):
    _name = 'crm.pos.role.relation'

    def _default_company_id(self):
        return self.env['res.company']._company_default_get('crm.pos.role.relation')

    crm_role = fields.Many2one('res.groups',string='CRM Role')
    pos_role = fields.Char(String='POS Role')
    company_id = fields.Many2one('res.company',string='Company',default=_default_company_id)




