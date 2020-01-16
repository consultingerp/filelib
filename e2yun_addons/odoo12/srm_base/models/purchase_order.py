# -*- coding: utf-8 -*-
from odoo import models, fields, api

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    location_id = fields.Many2one('stock.location', '交货到', domain=[('usage', '=', 'internal')])


