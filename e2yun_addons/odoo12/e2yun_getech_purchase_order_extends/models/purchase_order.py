# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import fields, models, api, exceptions


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.order"

    project_id = fields.Many2one('project.project', '项目编号')
    bu = fields.Many2one('sale.order.bu', '产业/BU')
    project_type = fields.Many2one('sale.order.project.type', '项目大类')
    # po_customer = fields.Char('客户订单号')
    project_name = fields.Char('项目名称')
    project_owner = fields.Char('项目负责人')
    final_customer = fields.Char('最终用户')
    receiver = fields.Char('收货人')
    receiver_address = fields.Char('收货地址')

    @api.onchange('project_id')
    def onchange_project_id(self):
        for item in self:
            if item.project_id:
                item.bu = item.project_id.sale_order_id.bu
                item.project_type = item.project_id.sale_order_id.project_type
                try:
                    item.po_customer = item.project_id.sale_order_id.po_customer
                    item.project_name = item.project_id.sale_order_id.project_name
                    item.project_owner = item.project_id.sale_order_id.project_owner
                except Exception:
                    pass
