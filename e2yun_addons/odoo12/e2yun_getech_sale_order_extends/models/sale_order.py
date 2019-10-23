# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api
import datetime
import suds.client
import json


class SaleOrder_BU(models.Model):
    _name = 'sale.order.bu'

    code = fields.Char('Code')
    name = fields.Char('Name')
    remark = fields.Char('Remark')

    @api.multi
    def name_get(self):
        return [(record.id, "%s:%s" % (record.code, record.name)) for record in self]


class SaleOrder_Project_type(models.Model):
    _name = 'sale.order.project.type'

    code = fields.Char('Code')
    name = fields.Char('Name')
    remark = fields.Char('Remark')

    @api.multi
    def name_get(self):
        return [(record.id, "%s:%s" % (record.code, record.name)) for record in self]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bu = fields.Many2one('sale.order.bu', '产业/BU')
    project_type = fields.Many2one('sale.order.project.type', '项目大类')

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res:
            prefix = '%s%s' % (res.bu.code, res.project_type.code)
            name = self.env['ir.sequence'].get_next_code_info_if_no_create('sale_order', prefix, '', 6)
            res.name = name
            if res.project_ids:
                res.project_ids.name = name
        return res
