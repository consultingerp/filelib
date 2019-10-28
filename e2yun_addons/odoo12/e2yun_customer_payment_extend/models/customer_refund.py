# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import suds.client
import datetime


class E2yunCustomerRefund(models.Model):
    _name = 'customer_refund.report'

    def transport_wechat_message_refund(self):  # 微信消息推送--客户退款
        flag = self.env['crm.team'].browse(self.id).show_accept_amount
        if flag:
            trans_amount = self.customer_refund_amount
        else:
            trans_amount = self.refund_amount01

        user_data = {
            "first": {
                "value": "%退款成功通知"
            },
            "keyword1": {
                "value": "time.strftime('%Y.%m.%d',time.localtime(time.time()))"
            },
            "keyword2": {
                "value": trans_amount,
                "color": "#173177"
            },
            "keyword3": {
                "value": self.refund_amount02
            },
            "keyword4": {
                "value": self.shop_id
            },
            "keyword5": {
                "value": self.partner_id
            },
            "remark": {
                "value": "客户PO号:%s" % self.customer_po,
                "value": "第三方退款编号:%s" % self.thrrd_receipt_num,
            }
        }
        if self.env.user.wx_user_id:  # 判断当前用户是否关联微信，关联发送微信信息
            self.env.user.wx_user_id.send_template_message(
                user_data, template_name='客户退款提醒', partner=self.env.user.partner_id)

    company_id = fields.Char('公司名称')
    shop_id = fields.Char('门店')
    partner_id = fields.Char('终端客户')
    refund_id = fields.Char('退款方')
    refund_num = fields.Char('退款单编号')
    receipt_doc_num = fields.Char('收款单编号')
    thrrd_receipt_num = fields.Char('第三方退款编号')
    refund_amount01 = fields.Char('应退款金额')
    refund_amount02 = fields.Char('实际退款金额')
    apply_date = fields.Date('申请日期')
    handing_cost = fields.Char('扣刷卡手续费')
    others_cost = fields.Char('其他扣费')
    tax_cost = fields.Char('扣税费')
    return_situation = fields.Char('退货情况')
    refund_reason = fields.Char('退款原因')
    invoice_situation = fields.Char('实际发票情况')
    refund_account = fields.Char('退款账户')
    apply_user = fields.Char('申请人')
    communication = fields.Char('备注')
    account_bank = fields.Char('开户行')
    account_name = fields.Char('银行账号')
    receipt_num = fields.Char('收据号')
    customer_po = fields.Char('客户PO号')
    customer_refund_amount = fields.Char('客户退款金额')
    refund_num = fields.Char('退款单编号')

    # date_from = fields.Date('日期从')
    # date_end = fields.Date('日期到')
    shop_name = fields.Char('门店名称')
    customer_name = fields.Char('客户名称')
    mobile_phone = fields.Char('手机号')

    # def init_date(self, ctx):
    #
    #     rq_from = str(ctx['date_from']) or ''
    #     rq_end = str(ctx['date_end']) or ''
    #     md_name = ctx['shop_name'].name or ''
    #     ku_name = ctx['customer_name'].name or ''
    #     dianhua = ctx['mobile_phone'] or ''
    #
    #     search_key = rq_from + '_' + rq_end + '_' + md_name + '_' + ku_name + '_' + str(self._uid) + '_' + dianhua
    #
    #     del_sql = "delete from customer_refund_report where to_char(create_date,'yyyymmdd') < to_char(CURRENT_DATE,'yyyymmdd')"
    #     self._cr.execute(del_sql)
    #     del_sql = "delete from stock_query_report where search_key = %s "
    #     self._cr.execute(del_sql, [search_key])
    #
    #     # 调用POS接口
    #     ICPSudo = self.env['ir.config_parameter'].sudo()
    #
    #     url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncReport?wsdl'  # webservice调用地址
    #     client = suds.client.Client(url)
    #     result = client.service.SyncReport(rq_from, rq_end, md_name, ku_name, dianhua, search_key)
    #
    #     if result != 'S':
    #         raise exceptions.Warning('查询数据异常:' + result)
    #
    # def open_table(self):
    #
    #     data = self.read()[0]
    #
    #     ctx = self._context.copy()
    #     ctx['date_from'] = self.date_from
    #     ctx['date_end'] = self.date_end
    #     ctx['shop_name'] = self.shop_name
    #     ctx['customer_name'] = self.customer_name
    #     ctx['mobile_phone'] = self.mobile_phone
    #
    #     return {
    #         'name': '库存查询',
    #         'view_type': 'form',
    #         'view_mode': 'tree',
    #         'res_model': 'customer_refund.report',
    #         'type': 'ir.actions.act_window',
    #         'context': ctx,
    #     }

