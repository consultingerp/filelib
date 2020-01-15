# -*- coding: utf-8 -*-
from odoo import models, fields, api

class company_code(models.Model):
    _inherit = 'res.company'

    company_code = fields.Char(string='Company code')


