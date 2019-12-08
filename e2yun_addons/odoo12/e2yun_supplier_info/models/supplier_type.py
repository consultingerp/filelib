from odoo import models, fields, api

class SupplierType(models.Model):
    _name = 'supplier.type'
    _description = 'Supplier Type'

    name = fields.Char(string='供应商类型名称')
    active = fields.Boolean('Active', default=True)