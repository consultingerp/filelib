# -*-coding:utf-8-*-
import datetime
import logging
from datetime import timedelta

from odoo import api, models
from ..controllers import client
from ..rpc import corp_client

_logger = logging.getLogger(__name__)


class WXAccountInvoice(models.AbstractModel):
    _inherit = "account.invoice"

    @api.multi
    def action_invoice_open(self):
        res = super(WXAccountInvoice, self).action_invoice_open()
        for order in self:
            title = '订单发票'
            if self.partner_id.wxcorp_user_id.userid:
                date_ref = (datetime.datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                data_body = "发票:" + order.number
                description = "<div class=\"gray\">" + date_ref + "</div> <div class=\"normal\">" + data_body + "</div>" \
                                                                                                                "\n<div class=\"highlight\"> 时间:" + order.date_invoice + "" \
                                                                                                                                                                         "\n 金额:%f" % order.amount_total + "" \
                                                                                                                                                                                                           "\n Tax:%f" % order.amount_tax + "" \
                                                                                                                                                                                                                                            "\n 联系:" + order.create_uid.name + "(" + order.create_uid.email + ")</div>"
                url = corp_client.corpenv(
                    self.env).server_url + '/web/login?usercode=saleorder&codetype=corp&redirect=' + order.portal_url
                url = corp_client.authorize_url(self, url, 'saleorderinvoice')
                corp_client.send_text_card(self, order.partner_id.wxcorp_user_id.userid, title, description, url, "详情")

            if self.partner_id.wx_user_id.openid:
                data = {
                    "first": {
                        "value": '你收到了一张新发票',
                        "color": "#173177"
                    },
                    "keyword1": {
                        "value": '已审核',
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
                        "value": order.date_invoice
                    },
                    "remark": {
                        "value": "联系:" + order.create_uid.name
                    }
                }
                #template_id = 'xdZchgSs4JoTpu8vOl8VW-7aBF8N3zwTCe8xOtWqsIQ'
                template_id = ''
                configer_para = self.env["wx.paraconfig"].sudo().search([('paraconfig_name', '=', '发票状态通知')])
                url = client.wxenv(
                    self.env).server_url + '/web/login?usercode=saleorder&codetype=wx&redirect=' + order.access_url
                client.send_template_message(self, self.partner_id.wx_user_id.openid, template_id, data, url,
                                             'saleorderinvoice')
            logging.info("order")
        return res
