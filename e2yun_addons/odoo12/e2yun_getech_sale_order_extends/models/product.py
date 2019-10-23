# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api
import datetime
import suds.client
import json


class ProductCategory(models.Model):
    _inherit = 'product.category'

    code = fields.Char('Code')

    @api.multi
    def name_get(self):
        return [(record.id, "%s:%s" % (record.code, record.name)) for record in self]


class Product(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        res = super(Product, self).create(vals)
        if res:
            if res.categ_id:
                default_code = self.env['ir.sequence'].get_next_code_info_if_no_create('product', res.categ_id.code, '', 7)
                res.default_code = default_code
        return res
