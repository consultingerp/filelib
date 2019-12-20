# -*-coding:utf-8-*-
import logging
from datetime import datetime

from odoo import api, models

_logger = logging.getLogger(__name__)


class WXSaleOrder(models.AbstractModel):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        for order in self:
            title = '销售订单'
            if order.partner_id.wx_user_id.openid:
                data = {
                    "first": {
                        "value": '您好，你的销售订单已创建'
                    },
                    "keyword1": {
                        "value": order.name,
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": "订单确认",
                        "color": "#173177"
                    },
                    "remark": {
                        "value": "产品：" + '：'.join(order.order_line.mapped('product_id.display_name'))

                    }
                }
                if order.partner_id.wx_user_id:
                    self.partner_id.wx_user_id.send_template_message(data, url=order.access_url, partner=order.partner_id,
                                                                     usercode='saleorder', template_name="订单确认通知")
            if order.partner_id.user_id:  # 需要通知销售人员
                data = {
                    "first": {
                        "value": '您好，%s创建了一张销售订单。' % order.partner_id.name
                    },
                    "keyword1": {
                        "value": order.name,
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": "订单确认",
                        "color": "#173177"
                    },
                    "remark": {
                        "value": "产品：" + '：'.join(order.order_line.mapped('product_id.display_name'))
                    }
                }
                action = self.env.ref('sale.action_orders').id
                menu_id = self.env.ref('sale.menu_sale_order').id
                redirect_order = '/web#id=%s&action=%s&model=sale.order&view_type=form&menu_id=%s' % (order.id, action, menu_id)
                if order.partner_id.user_id.wx_user_id:
                   self.partner_id.wx_user_id.send_template_message(data, url=redirect_order, user=order.partner_id.user_id,
                                                                 usercode='saleorder', template_name="订单确认通知")

            logging.info(order)
        res = super(WXSaleOrder, self).action_confirm()
        return res

    @api.multi
    def write(self, values):
        result = super(WXSaleOrder, self).write(values)
        if values.get('state') and values.get('state') == 'sent':
            title = '销售订单'
            if self.partner_id.wx_user_id.openid:
                data = {
                    "first": {
                        "value": '您好，你的销售订单已创建'
                    },
                    "keyword1": {
                        "value": self.name,
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": "订单创建",
                        "color": "#173177"
                    },
                    "remark": {
                        "value": "产品：" + '：'.join(self.order_line.mapped('product_id.display_name'))
                    }
                }
                if self.partner_id.wx_user_id:
                    self.partner_id.wx_user_id.send_template_message(data, url=self.access_url, partner=self.partner_id,
                                                                     usercode='saleorder', template_name="订单确认通知")
            if self.partner_id.user_id:  # 需要通知销售人员
                data = {
                    "first": {
                        "value": '您好，%s创建了一张销售订单。' % self.partner_id.name
                    },
                    "keyword1": {
                        "value": self.name,
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": "订单创建",
                        "color": "#173177"
                    },
                    "remark": {
                        "value": "产品：" + '：'.join(self.order_line.mapped('product_id.display_name'))
                    }
                }
                action = self.env.ref('sale.action_orders').id
                menu_id = self.env.ref('sale.menu_sale_order').id
                redirect_order = '/web#id=%s&action=%s&model=sale.order&view_type=form&menu_id=%s' % (self.id, action, menu_id)
                if self.partner_id.user_id.wx_user_id:
                    self.partner_id.wx_user_id.send_template_message(data, url=redirect_order, user=self.partner_id.user_id,
                                                                     usercode='saleorder', template_name="订单确认通知")

        return result
