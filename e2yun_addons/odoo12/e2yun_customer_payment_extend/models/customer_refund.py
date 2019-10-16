# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class E2yunCustomerRefund(models.Model):
    _name = 'customer_refund.report'

    company_id = fields.Char('公司名称')
    shop_id = fields.Char('门店')
    partner_id = fields.Char('终端客户')
    refund_id = fields.Char('退款方')
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
    customer_refund_amount = fields.Char('客户交款金额')

    date_from = fields.Date('日期从')
    date_end = fields.Date('日期到')
    shop_name = fields.Char('门店名称')
    customer_name = fields.Char('客户名称')
    mobile_phone = fields.Char('手机号')

    def open_table(self):
        return {
            'name': '库存查询',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'customer_refund.report',
            'type': 'ir.actions.act_window',
        }