# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api
import datetime
import suds.client
import json


class SaleOrder_BU(models.Model):
    _name = 'sale.order.bu'
    _description = 'sale order bu'

    code = fields.Char('Code')
    name = fields.Char('Name')
    remark = fields.Char('Remark')

    @api.multi
    def name_get(self):
        return [(record.id, "%s:%s" % (record.code, record.name)) for record in self]


class SaleOrder_Project_type(models.Model):
    _name = 'sale.order.project.type'
    _description = 'sale order project type'

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
    po_customer = fields.Char('客户PO/销售合同编号', copy=False)
    project_name = fields.Char('项目名称')
    project_owner = fields.Char('项目负责人')
    sales_manager = fields.Char('销售经理')
    final_customer = fields.Char('最终用户')

    _sql_constraints = [
        ('po_customer_unique', 'unique(po_customer)', "客户PO/销售合同编号不能重复！"),
    ]

    @api.model
    def create(self, vals):
        needrename = False
        if 'name' not in vals:
            needrename = True
        res = super(SaleOrder, self).create(vals)
        if res:
            if needrename:
                prefix = '%s%s' % (res.bu.code, res.project_type.code)
                name = self.env['ir.sequence'].get_next_code_info_if_no_create('sale_order', prefix, '', 6)
                res.name = name
                # res.project_name = name
            else:
                res.name = vals['name']
                # res.project_name = vals['name']
            # if res.project_ids:
            #     res.project_ids.name = name
        return res
