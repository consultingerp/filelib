# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import fields, models, api, exceptions


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.order"

    project_id = fields.Many2one('project.project', '项目编号')
    bu = fields.Many2one('sale.order.bu', '产业/BU')
    project_type = fields.Many2one('sale.order.project.type', '项目大类')
    po_customer = fields.Char('客户订单号')
    project_name = fields.Char('项目名称')
    project_owner = fields.Char('项目负责人')
    project_owner = fields.Char('项目负责人')

    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id:
            self.bu = self.project_id.sale_order_id.bu
            self.project_type = self.project_id.sale_order_id.project_type
            try:
                self.po_customer = self.project_id.sale_order_id.x_studio_po_customer
                self.project_name = self.project_id.sale_order_id.x_studio_project_name
                self.project_owner = self.project_id.sale_order_id.x_studio_project_owner
            except Exception:
                pass
