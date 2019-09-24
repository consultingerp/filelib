# -*- coding: utf-8 -*-

from odoo import models, fields

class res_users(models.Model):
    _inherit = 'res.users'

    vat = fields.Char('统一社会信用代码')
    company_name = fields.Char('公司名称')
