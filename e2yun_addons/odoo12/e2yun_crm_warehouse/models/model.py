# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class model(models.Model):
    _name = 'crm.warehouse'
    _description = '仓库'

    company_id = fields.Many2one('res.company', string='工厂')
    name = fields.Char('仓库')
    code = fields.Char('仓库代码')







