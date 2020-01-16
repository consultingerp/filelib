# -*- coding: utf-8 -*-
from odoo import models, fields, api

class factory_code(models.Model):
    _inherit = 'stock.warehouse'
    factory_code = fields.Char(string='Factory code',required=True)


