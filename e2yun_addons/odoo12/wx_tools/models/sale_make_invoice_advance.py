# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import logging
from datetime import timedelta

from odoo import api, models
from ..controllers import client
from ..rpc import corp_client

_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        date_ref = (datetime.datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for order in sale_orders:
            menu_id = ''
            paras_menu = self.env["wx.paraconfig"].sudo().search([('paraconfig_name', '=', 'invoice_menu_id')])
            if paras_menu:
                menu_id = paras_menu[0].paraconfig_value
            paras_action = self.env["wx.paraconfig"].sudo().search([('paraconfig_name', '=', 'invoice_action')])
            action = ''
            if paras_action:
                action = paras_action[0].paraconfig_value

            # redirectur = '#id='+str(order.invoice_ids.id)+'&view_type=form&model=account.invoice&menu_id=145&action=226'
            redirectur = '/web#id=' + str(
                order.invoice_ids[-1].id) + '&view_type=form&model=account.invoice&menu_id=' + menu_id + '&action=' + action + ''
            title = '发票审核'


            if order.create_uid.wxcorp_user_id.userid:
                data_body = "订单号:" + order.name
                description = "<div class=\"gray\">" + date_ref + "</div> <div class=\"normal\">" + data_body + "</div>" \
                                                                                                                "<div class=\"highlight\"> 时间:" + order.date_order + \
                              "\n产品:" + '：'.join(order.order_line.mapped('product_id.display_name')) + \
                              "\n联系:" + order.create_uid.name + "</div>"
                url = corp_client.corpenv(
                    self.env).server_url + '/web/login?usercode=saleorder&codetype=corp&redirect=' + redirectur
                url = corp_client.authorize_url(self, url, 'saleorderinvoice')
                corp_client.send_text_card(self, order.create_uid.wxcorp_user_id.userid, title, description, url, "详情")
            if order.create_uid.wx_user_id.openid:

                data = {
                    "first": {
                        "value": date_ref,
                        "color": "#173177"
                    },
                    "keyword1": {
                        "value": '待审核',
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": "订单号:" + order.name,
                        "color": "#173177"
                    },
                    "keyword3": {
                        "value": order.amount_total
                    },
                    "keyword4": {
                        "value": str(order.date_order)
                    },
                    "remark": {
                        "value": "产品：" + '：'.join(order.order_line.mapped('product_id.display_name')) +
                                 "\n联系:" + order.create_uid.name
                    }
                }
                template_id = ''
                configer_para = self.env["wx.paraconfig"].sudo().search([('paraconfig_name', '=', '发票状态通知')])
                if configer_para:
                    template_id = configer_para[0].paraconfig_value
                url = client.wxenv(
                    self.env).server_url + '/web/login?usercode=saleorderwx&codetype=wx&redirect=' + redirectur
                client.send_template_message(self, order.user_id.wx_user_id.openid, template_id, data, url,
                                             'saleorder')

        return res
