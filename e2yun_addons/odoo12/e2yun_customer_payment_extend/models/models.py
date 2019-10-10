# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError, Warning
import suds.client

class e2yun_customer_payment_extend(models.Model):
    _inherit = 'account.payment'

    payment_type2 = fields.Selection(
        [('D11', '公司收现金'), ('D12', '刷卡'),
         ('D13', '公司微信'), ('D16', '公司支付宝'),
         ('C11', '第三方现金'), ('C12', '第三方刷卡'),
         ('C13', '第三方支票'), ('C14', '第三方优惠券'),
         ('C15', '第三方微信'), ('C16', '第三方支付宝'),
         ('D14', '第三方电商O2O'), ('D15', '第三方厂家O2O'),
         ('K11', '电商支付宝'), ('G11', '公司收支票'),
         ('G13', '门店现金'), ('G12', '转账'), ('D17', '分销商定制货款')], '支付方式', required=True)
    currency = fields.Char('货币')
    payment_voucher =  fields.Char('交款凭证')
    marketing_activity = fields.Char('参与市场活动')
    bank_num = fields.Char('银行帐号')
    payment_attachments = fields.Many2many('ir.attachment', string="付款附件",
                                           domain=[('res_model', '=', 'account.payment')])

    related_shop = fields.Many2one('crm.team', '门店', required=True)
    receipt_Num = fields.Char('收据编号', required=True)
    sales_num = fields.Char('销售单号')
    handing_cost = fields.Monetary('手续费')
    po_num = fields.Char('市场合同号PO')
    customer_po = fields.Char('客户PO号')
    payment_status = fields.Selection([('A1', '定金'), ('A2', '中期款'),
                                       ('A3', '尾款'), ('A4', '全款')], '交款类型', required=True)
    payment_serirs_no = fields.Char('No.')

    customer_pay_amount = fields.Monetary(string='客户交款金额')
    accept_amount = fields.Monetary(string='收款结算金额')

    def sync_customer_payment_to_pos(self):
        for r in self:
            if r.state == 'draft':
                raise exceptions.Warning('状态为草稿单据，不能同步到POS系统')

            ICPSudo = self.env['ir.config_parameter'].sudo()
            url = ICPSudo.get_param('e2yun.sync_pos_payment_webservice_url')  # webservice调用地址
            client = suds.client.Client(url)

            now = self.create_date.replace(microsecond=0)

            result = client.service.createPayment(r.company_id.company_code,  # 公司
                                                 r.receipt_Num or '',  # 收款编号
                                                 r.company_id.name or '',  # 公司名称
                                                 r.po_num or '',  # PO
                                                 r.amount or '',  # 收款金额

                                                 '',  # 支票号
                                                 r.sales_num or '',  # 销售单号
                                                 r.payment_voucher or '',  # 交款凭证
                                                 r.related_shop.shop_code or '',  # 门店
                                                 r.partner_id.app_code,  # 终端客户

                                                 '',  # 旺旺号
                                                 r.payment_date or '',  # 交款日期
                                                 r.handing_cost or '',  # 手续费
                                                 'CNY',  # 货币
                                                 r.communication or '',  # 备注
                                                 r.marketing_activity or '',  # 参与市场活动
                                                 '',  # 到期日期

                                                 r.payment_type2 or '',  # 支付方式
                                                 r.payment_status or '',  # 交款类型
                                                 self.env.user.name,  # 经手人
                                                 r.sales_num or '',  # 收据单号
                                                 '',  # 支票状态
                                                 '',  # 收据日期
                                                 r.bank_num or '',  # 银行账户
                                                 r.customer_po or '',  # 客户PO

                                                 self.env.user.name,  # 创建人
                                                 now,  # 创建日期
                                                 )


    @api.model
    def create(self, vals_list):
        atch = vals_list['payment_attachments'] #[[6, false, [11077, 11022]]]
        temp = []
        for r in atch:  #[6,0,[11077]]
            if type(r) is list:

                for r1 in r:
                    if type(r1) is list:  #6, 0, [11077, 11022]
                        temp.extend(r1)

        for ids in temp:
            # atch_id = ids
            atch_line = self.env['ir.attachment'].browse(ids)
            atch_line.write({'res_model': 'account.payment'})

        res = super(e2yun_customer_payment_extend, self).create(vals_list)
        return res

    @api.one
    def write(self, vals):
        if vals.get('payment_attachments'):
            atch = vals['payment_attachments']
            temp = []
            for r in atch:
                if type(r) is list:

                    for r1 in r:
                        if type(r1) is list:
                            temp.extend(r1)

            for ids in temp:
                # atch_id = ids
                atch_line = self.env['ir.attachment'].browse(ids)
                atch_line.write({'res_model': 'account.payment'})
            return super(e2yun_customer_payment_extend, self).write(vals)
        else:
            return super(e2yun_customer_payment_extend, self).write(vals)

class e2yun_customer_payment_extend2(models.Model):
    _inherit = 'ir.attachment'

    @api.depends('datas')
    @api.onchange('datas')
    def _onchange_name(self):
        self.name = self.datas_fname

class e2yun_customer_payment_res_partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if name:
            teams = self.search(['|', ('app_code', operator, name), ('name', operator, name)])
            return teams.name_get()
        else:
            return super(e2yun_customer_payment_res_partner, self).name_search(name, args, operator, limit)