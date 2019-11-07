# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, api, exceptions, fields


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    po_customer = fields.Char('客户PO/销售合同编号', copy=False)
    project_id = fields.Many2one('project.project', '项目编号', compute='_on_change_po_customer')
    final_customer = fields.Char('最终用户', compute='_on_change_po_customer')
    receiver = fields.Char('收货人')
    receiver_address = fields.Char('收货地址')

    @api.onchange('po_customer')
    def _on_change_po_customer(self):
        if self.po_customer:
            sale = self.env['sale.order'].search([('po_customer', '=', self.po_customer)])
            self.final_customer = sale.final_customer
            if sale.project_ids:
                self.project_id = sale.project_ids[0].id


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    @api.model
    def _calc_new_qty(self, request_line, po_line=None, new_pr_line=False):
        qty = super(PurchaseRequestLine, self)._calc_new_qty(request_line, po_line, new_pr_line)
        # 处理：如果算出来的新数量大于po的数量，就使用po的数量，不改变数量。
        qty = min(po_line.product_qty, qty)
        return qty


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    @api.multi
    def make_purchase_order(self):
        res = super(PurchaseRequestLineMakePurchaseOrder, self).make_purchase_order()
        for item in self.item_ids:
            line = item.line_id
            request_id = item.request_id
            line.purchase_lines.mapped('order_id').write({'project_id': request_id.project_id.id, 'final_customer': request_id.final_customer,
                                                          'receiver': request_id.receiver, 'receiver_address': request_id.receiver_address})
            line.purchase_lines.mapped('order_id').onchange_project_id()
            # line.qty_in_progress
            if line.qty_in_progress > line.product_qty:
                raise exceptions.Warning('采购请求：%s，物料：%s，转采购订单数量超过采购请求数量，请检查数据!' % (line.request_id.name, line.product_id.name))

            # qty_to_buy = sum(purchase_lines.mapped('product_qty'))
            # if line.product_qty < qty_to_buy:
            #     raise exceptions.Warning('采购请求：%s，物料：%s，转PO数量超过PR数量，请检查数据!' % (line.request_id.name, line.product_id.name))
        return res
