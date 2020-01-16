# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_supplierinfo(models.Model):

    _inherit = "product.supplierinfo"

    delivery_overdue_days = fields.Integer(string='Supplier Delivery Overdue days',required=True)
    the_quota = fields.Float(string='Supplier The Quota',required=True)
    automatic_selection= fields.Boolean('Delivery Automatic Selection PO',default=True)
    min_pack = fields.Integer('Min Package',default=0)
    time_tolerance = fields.Integer(string='Time Tolerance',required=True)
    number_tolerance = fields.Integer(string='Number Tolerance')
