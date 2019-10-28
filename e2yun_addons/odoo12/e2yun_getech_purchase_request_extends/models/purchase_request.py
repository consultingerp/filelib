# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, api, exceptions


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    @api.model
    def _calc_new_qty(self, request_line, po_line=None,
                      new_pr_line=False):
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
            # purchase_lines = line.purchase_lines
            line.qty_in_progress
            if line.qty_in_progress > line.product_qty:
                raise exceptions.Warning('采购请求：%s，物料：%s，转采购订单数量超过采购请求数量，请检查数据!' % (line.request_id.name, line.product_id.name))

            # qty_to_buy = sum(purchase_lines.mapped('product_qty'))
            # if line.product_qty < qty_to_buy:
            #     raise exceptions.Warning('采购请求：%s，物料：%s，转PO数量超过PR数量，请检查数据!' % (line.request_id.name, line.product_id.name))
        return res
