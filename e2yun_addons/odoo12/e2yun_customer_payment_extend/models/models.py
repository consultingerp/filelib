# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, Warning
import suds.client, time, logging

_logger = logging.getLogger(__name__)


class e2yun_customer_payment_extend(models.Model):
    _inherit = 'account.payment'

    @api.depends('related_shop')
    @api.onchange('related_shop')
    def _onchange_banknum(self):
        code = self.related_shop.shop_code
        domain = [('shop_code', '=', code)]
        return {
            'domain': {'bank_num': domain}
        }

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
    payment_voucher = fields.Char('交款凭证')
    marketing_activity = fields.Char('参与市场活动')
    bank_num = fields.Many2one('payment_bank.info', '银行帐号')
    payment_attachments = fields.Many2many('ir.attachment', string="付款附件",
                                           domain=[('res_model', '=', 'account.payment')])

    related_shop = fields.Many2one('crm.team', '门店', required=True)
    receipt_Num = fields.Char('收款编号', readonly=True)
    sales_num = fields.Char('销售单号')
    handing_cost = fields.Monetary('手续费')
    po_num = fields.Char('市场合同号PO')
    customer_po = fields.Char('客户PO号')
    payment_status = fields.Selection([('A1', '定金'), ('A2', '中期款'),
                                       ('A3', '尾款'), ('A4', '全款')], '交款类型', required=True)
    payment_serirs_no = fields.Char('No.')

    accept_amount = fields.Monetary(string='客户交款金额')

    accept_amount000 = fields.Boolean(related='related_shop.show_accept_amount')
    wx_message_error = fields.Char('推送消息状况', default=1)

    @api.multi
    def _compute_show_amount(self):
        self.env['crm.team'].browse('related_shop')

    def sync_customer_payment_to_pos(self, res):
        for r in res:
            # if r.state == 'draft':
            #     raise exceptions.Warning('状态为草稿单据，不能同步到POS系统')

            ICPSudo = self.env['ir.config_parameter'].sudo()
            url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/CreatePayment?wsdl'  # webservice调用地址
            client = suds.client.Client(url)

            now = r.create_date.replace(microsecond=0)

            try:
                result = client.service.createPayment(r.company_id.company_code,  # 公司
                                                     r.receipt_Num or '',  # 收款编号
                                                     r.company_id.name or '',  # 公司名称
                                                     r.po_num or '',  # PO
                                                     r.amount or '',  # 收款金额(收款结算金额

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
                                                     r.bank_num.bank_accont or '',  # 银行账户
                                                     r.customer_po or '',  # 客户PO

                                                     self.env.user.name,  # 创建人
                                                     now,  # 创建日期
                                                     r.id,
                                                     r.accept_amount #客户交款金额
                                                     )
            except Exception as e:
                raise e
            r.receipt_Num = result[1:]
            if result[0] != 'S':
                raise exceptions.Warning('同步到POS系统出现错误，请检查输入的数据'+result)
        return True

    def transport_wechat_message(self, res):  # 微信消息推送--客户付款
        if res.accept_amount:
            trans_amount = '%.2f' % res.accept_amount
        else:
            trans_amount = '%.2f' % res.amount

        if res.customer_po:
            cpo = res.customer_po
        else:
            cpo = '无'
        if res.po_num:
            po = res.po_num
        else:
            po = '无'
        if res.payment_voucher:
            pv = res.payment_voucher
        else:
            pv = '无'

        dic = {'D11': '公司收现金',
               'D12': '刷卡',
               'D13': '公司微信',
               'D16': '公司支付宝',
               'C11': '第三方现金',
               'C12': '第三方刷卡',
               'C13': '第三方支票',
               'C14': '第三方优惠券',
               'C15': '第三方微信',
               'C16': '第三方支付宝',
               'D14': '第三方电商O2O',
               'D15': '第三方厂家O2O',
               'K11': '电商支付宝',
               'G11': '公司收支票',
               'G13': '门店现金',
               'G12': '转账',
               'D17': '分销商定制货款'}

        user_data = {
            "first": {
                "value": "付款成功通知"
            },
            "keyword1": {
                "value": time.strftime('%Y.%m.%d', time.localtime(time.time()))
            },
            "keyword2": {
                "value": trans_amount,
                "color": "#173177"
            },
            "keyword3": {
                "value": res.related_shop.display_name
            },
            "keyword4": {
                "value": res.partner_id.name
            },
            "keyword5": {
                "value": dic[res.payment_type2]
            },
            "remark": {
                "value": "客户PO号:%s" % cpo + ' ' +
                         "市场合同号:%s" % po + ' ' +
                         "交款凭证:%s" % pv,

            }
        }
        if self.env.user.wx_user_id:  # 判断当前用户是否关联微信，关联发送微信信息
            try:
                self.env.user.wx_user_id.send_template_message(
                    user_data, template_name='客户收款提醒', partner=self.env.user.partner_id)
            except Exception as e:
                res.wx_message_error = e

    def transport_wechat_message_refund(self, res):  # 微信消息推送--客户退款
        _logger.info("退款推送测试--3")
        flag = self.related_shop.show_accept_amount
        refund = self.env['customer_refund.report'].search([('refund_num', '=', self.receipt_Num)])

        if flag:
            trans_amount = refund.customer_refund_amount
        else:
            trans_amount = refund.refund_amount01
        if refund.customer_po:
            cpo = refund.customer_po
        else:
            cpo = '无'
        if refund.thrrd_receipt_num:
            trn = refund.thrrd_receipt_num
        else:
            trn = '无'

        user_data = {
            "first": {
                "value": "%退款成功通知"
            },
            "keyword1": {
                "value": time.strftime('%Y.%m.%d', time.localtime(time.time()))
            },
            "keyword2": {
                "value": trans_amount,
                "color": "#173177"
            },
            "keyword3": {
                "value": refund.refund_amount02
            },
            "keyword4": {
                "value": refund.shop_id
            },
            "keyword5": {
                "value": refund.partner_id
            },
            "remark": {
                "value": "客户PO号:%s" % cpo + ' ' + "第三方退款编号:%s" % trn
            }
        }

        if self.env.user.wx_user_id:  # 判断当前用户是否关联微信，关联发送微信信息
            self.env.user.wx_user_id.send_template_message(
                user_data, template_name='客户退款提醒', partner=self.env.user.partner_id)
            _logger.info("退款推送测试--4，用户id%s" % self.env.user.id)

    @api.model
    def create(self, vals_list):
        atch = vals_list['payment_attachments']  # [[6, false, [11077, 11022]]] 展开多层list
        temp = []
        for r in atch:  # [6,0,[11077]]
            if type(r) is list:
                for r1 in r:
                    if type(r1) is list:  # 6, 0, [11077, 11022]
                        temp.extend(r1)
        for ids in temp:
            # atch_id = ids
            atch_line = self.env['ir.attachment'].browse(ids)
            atch_line.write({'res_model': 'account.payment'})

        if vals_list['amount'] == 0:
            raise Warning(
                _("付款金额不能为0!"))

        if not vals_list.get('journal_id', False):
            # currency_id = self.env['res.company'].browse(vals_list.get('company_id', False)).currency_id.id
            # journal = self.env['account.journal'].search(
            #     [('type', 'in', ('bank', 'cash')), ('currency_id', '=', currency_id)], limit=1)
            journal = self.env['account.journal'].search(
                [('type', 'in', ('bank', 'cash')), ('company_id', '=', vals_list.get('company_id', False))], limit=1)
            if journal:
                vals_list['journal_id'] = journal.id
            else:
                journal = self.env['account.journal'].search([], limit=1)
                if journal:
                    vals_list['journal_id'] = journal.id

        pos_flag = vals_list.get('pos_flag',False)
        if pos_flag:
            del vals_list['pos_flag']
        res = super(e2yun_customer_payment_extend, self).create(vals_list)

        #pos同步的不要再次同步回去
        if(not pos_flag):
            self.sync_customer_payment_to_pos(res)

        self.transport_wechat_message(res)
        _logger.info("退款推送测试--5用户id%s" % self.env.user.id)
        return res

    @api.one
    def write(self, vals):
        previous_state = self.state
        # vals['state'] = 'cancelled'
        new_state = vals.get('state')
        _logger.info("退款推送测试--1")

        res = super(e2yun_customer_payment_extend, self).write(vals)
        if previous_state == 'draft':
            if new_state == 'cancelled':
                _logger.info("退款推送测试--2")
                self.transport_wechat_message_refund(res)
        return res

    @api.model
    def get_payment_attachments(self, payment_id):
        payment = self.browse(int(payment_id))
        attachments = []
        for a in payment.payment_attachments:
            attachments.append({
                'name':a["name"],
                'datas':a["datas"],
                'file_size':a['file_size']
            })

        return attachments

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

    @api.multi
    def name_get(self):
        flag = self.env.context.get('show_custom_name', False)
        if flag == 8:
            res = []
            for res_partner in self:
                name = str(res_partner.app_code) + ' ' + str(res_partner.name)
                res.append((res_partner.id, name))
            return res
        # elif flag == 2:
        #     res = []
        #     for res_partner in self:
        #         name = str(res_partner.app_code)
        #         res.append((res_partner.id, name))
        #     return res
        else:
            return super(e2yun_customer_payment_res_partner, self).name_get()

class e2yun_customer_payment_bank_info(models.Model):
    _name = 'payment_bank.info'

    name = fields.Char(related='bank_describe')
    shop_code = fields.Char('门店代码')
    bank_accont = fields.Char('银行账户科目编码')
    bank_describe = fields.Char('银行账户科目描述')
