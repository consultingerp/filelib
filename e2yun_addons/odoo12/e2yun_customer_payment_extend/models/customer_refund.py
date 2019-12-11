# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import suds.client, time, logging

_logger = logging.getLogger(__name__)


class E2yunCustomerRefund(models.Model):
    _name = 'customer_refund.report'
    _description = '客户退款查询报表'

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
    # refund_num = fields.Char('退款单编号')

    mobile_phone = fields.Char('手机号')
    huming = fields.Char('户名')
    refund_status = fields.Selection([
        ('draft', '草稿'), ('checked', '已审核'), ('posted', '已过帐'), ('cancelled', '取消')],
        '状态', default='draft')
    shop_code = fields.Char('门店编码')
    app_code = fields.Char('客户编码')
    voucher_status = fields.Char('凭证状态')
    related_shop = fields.Many2one('crm.team', compute='get_crm_team', store=True)

    @api.model
    def get_crm_team(self):
        for r in self:
            if not r.shop_code:
                r.shop_code = self.env['crm.team'].search([('name', '=', self.shop_id)]).shop_code
            r.related_shop = self.env['crm.team'].search([('shop_code', '=', r.shop_code)])

    def write(self, vals):
        previous_state = self.refund_status
        new_state = vals.get('refund_status')
        res = super(E2yunCustomerRefund, self).write(vals)
        shop = self.env['crm.team'].search([('name', '=', self.shop_id)])

        if shop.sent_wx_message:
            _logger.info("推送门店")
            if self.refund_id == '第三方退款' and previous_state == 'draft' and new_state == 'checked':
                _logger.info("第三方退款推送")
                self.transport_wechat_message_refund(res)
            if self.refund_id != '第三方退款' and previous_state == 'checked' and new_state == 'posted':
                _logger.info("其他退款推送")
                self.transport_wechat_message_refund(res)
        return res

    def transport_wechat_message_refund(self, res):  # 微信消息推送--客户退款
        flag = self.env['crm.team'].search([('shop_code', '=', self.shop_code)]).show_accept_amount
        # partner_id0 = self.env['res.partner'].search([('app_code', '=', self.app_code)]).app_code

        if flag:
            trans_amount = self.customer_refund_amount
        else:
            trans_amount = self.refund_amount01
        if self.customer_po:
            # cpo = "客户PO号:%s" % self.customer_po
            cpo = self.customer_po
        else:
            cpo = ''
        if self.thrrd_receipt_num:
            # trn = "第三方退款编号:%s" % self.thrrd_receipt_num
            trn = self.thrrd_receipt_num

        else:
            trn = ''

        user_data = {
            "first": {
                "value": "退款成功通知"
            },
            "keyword1": {
                "value": time.strftime('%Y.%m.%d', time.localtime(time.time()))
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
                "value": "%s" % cpo + ' ' + "%s" % trn
            }
        }

        get_wx_user_id = self.env['res.partner'].search([('app_code', '=', self.app_code)])
        if get_wx_user_id.wx_user_id:  # 判断当前用户是否关联微信，关联发送微信信息
            _logger.info("进入推送")
            get_wx_user_id.wx_user_id.send_template_message(
                user_data, template_name='客户退款提醒', partner=get_wx_user_id)
            _logger.info("完成推送")
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
