# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, Warning
import uuid
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

    company_id = fields.Many2one('res.company', string='Company', related=None, index=True, default=lambda self: self.env.user.company_id)

    def defalut_payment_company_id(self):
        company_id = self.env.user.company_id.id
        return company_id
    # company_id_ex = fields.Many2one('res.company', string='公司名称', default=defalut_payment_company_id)

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
    payment_attachments = fields.One2many('ir.attachment', 'res_id',
                                          domain=[('res_model', '=', 'account.payment')], string="付款附件")

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
    tel = fields.Char('手机号', related='partner_id.mobile')

    accept_amount000 = fields.Boolean(related='related_shop.show_accept_amount')
    sent_wx_message = fields.Boolean(related='related_shop.sent_wx_message')
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

            # attachments = []
            # for a in r.payment_attachments:
            #     attachments.append({
            #         'name': a["name"],
            #         'datas': a["datas"].decode('utf-8'),
            #         'file_size': a['file_size']
            #     })
            # json_attachments = json.dumps(attachments)

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
                                                     r.accept_amount, #客户交款金额
                                                     #json_attachments #附件
                                                     )
            except Exception as e:
                raise e
            r.receipt_Num = result[1:]
            if result[0] != 'S':
                raise exceptions.Warning('同步到POS系统出现错误，请检查输入的数据'+result)
        return True

    # 微信消息推送--客户付款
    def transport_wechat_message(self, res):  # 微信消息推送--客户付款
        if res.accept_amount:
            trans_amount = '%.2f' % res.accept_amount
        else:
            trans_amount = '%.2f' % res.amount

        if res.customer_po:
            # cpo = "客户PO号:%s" % res.customer_po
            cpo = res.customer_po
        else:
            cpo = ''
        if res.po_num:
            # po = "市场合同号:%s" % res.po_num
            po = res.po_num

        else:
            po = ''
        if res.payment_voucher:
            # pv = "交款凭证:%s" % res.payment_voucher
            pv = res.payment_voucher
        else:
            pv = ''

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
                "value": res.related_shop.name
            },
            "keyword4": {
                "value": res.partner_id.name
            },
            "keyword5": {
                "value": dic[res.payment_type2]
            },
            "remark": {
                "value": "%s" % cpo + ' ' +
                         "%s" % po + ' ' +
                         "%s" % pv,
            }
        }

        # action_xmlid = 'e2yun_customer_payment_extend.account_payment_form_view_extend'
        #             /web?#id=150&action=209&model=account.payment&view_type=form&menu_id=138
        # action_url = '/web#id=%s&action=209&model=account.payment&view_type=form&menu_id=138' % (str(res.id))
        if res.partner_id.wx_user_id:  # 判断当前用户是否关联微信，关联发送微信信息
            try:
                res.partner_id.wx_user_id.send_template_message(
                    user_data, template_name='客户收款提醒', partner=res.partner_id)
            except Exception as e:
                res.wx_message_error = e

    # 微信消息推送--删除客户付款
    def transport_wechat_message2(self): # 微信消息推送--删除客户付款
        if self.accept_amount:
            trans_amount = '%.2f' % self.accept_amount
        else:
            trans_amount = '%.2f' % self.amount

        if self.customer_po:
            # cpo = "客户PO号:%s" % res.customer_po
            cpo = self.customer_po
        else:
            cpo = ''
        if self.po_num:
            # po = "市场合同号:%s" % res.po_num
            po = self.po_num

        else:
            po = ''
        if self.payment_voucher:
            # pv = "交款凭证:%s" % res.payment_voucher
            pv = self.payment_voucher
        else:
            pv = ''

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
                "value": "取消付款成功通知"
            },
            "keyword1": {
                "value": time.strftime('%Y.%m.%d', time.localtime(time.time()))
            },
            "keyword2": {
                "value": trans_amount,
                "color": "#173177"
            },
            "keyword3": {
                "value": self.related_shop.name
            },
            "keyword4": {
                "value": self.partner_id.name
            },
            "keyword5": {
                "value": dic[self.payment_type2]
            },
            "remark": {
                "value": "取消客户付款:" +
                         "%s" % cpo + ' ' +
                         "%s" % po + ' ' +
                         "%s" % pv,
            }
        }

        # action_xmlid = 'e2yun_customer_payment_extend.account_payment_form_view_extend'
        #             /web?#id=150&action=209&model=account.payment&view_type=form&menu_id=138
        # action_url = '/web#id=%s&action=209&model=account.payment&view_type=form&menu_id=138' % (str(res.id))
        if self.partner_id.wx_user_id:  # 判断当前用户是否关联微信，关联发送微信信息
            try:
                self.partner_id.wx_user_id.send_template_message(
                    user_data, template_name='客户收款提醒', partner=self.partner_id)
            except Exception as e:
                self.wx_message_error = e

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

        if self.partner_id.wx_user_id:  # 判断当前用户是否关联微信，关联发送微信信息
            self.partner_id.wx_user_id.send_template_message(
                user_data, template_name='客户退款提醒', partner=self.partner_id)
            _logger.info("退款推送测试--4，用户id%s" % self.partner_id)

    @api.model
    def default_get(self, fields_list):
        ctx = self._context.copy()
        a = ctx.get('partner_id')
        if a:
            idd = ctx['partner_id']
            res = super(e2yun_customer_payment_extend, self).default_get(fields_list)
            res.update({'partner_id': idd})
            return res
        else:
            return super(e2yun_customer_payment_extend, self).default_get(fields_list)

    @api.model
    def create(self, vals_list):
        vals_list['name'] = self.env['ir.sequence'].next_by_code('seq_account_payment.seq_customer') or '/'
        ctx = self._context.copy()
        a = vals_list.get('payment_attachments')

        pos_flag = vals_list.get('pos_flag', False)
        if pos_flag:
            del vals_list['pos_flag']

        if not a and not pos_flag:
            raise Warning(
                _("付款附件不能为空!"))

        #检查客户的pos状态是否已经同步SAP
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncMember?wsdl'  # webservice调用地址
        client = suds.client.Client(url)
        partner_code = self.env['res.partner'].browse(vals_list['partner_id']).app_code
        result = client.service.getSAPState(partner_code or '')
        if result != 'S':
            raise Warning(_('客户状态不正确，请检查pos状态-%s') % result)
        # del result

        atch = vals_list['payment_attachments']  # [[],[]]
        for r in atch:  # [0,'virtual', {}]
            # r[2]['res_name'] = r[2]['datas_fname']
            r[2]['res_model'] = 'account.payment'
            r[2]['name'] = uuid.uuid4()
            r[2]['active'] = True

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

        check_accept_amount = self.env['crm.team'].browse(vals_list['related_shop']).show_accept_amount
        if not check_accept_amount:
            vals_list['accept_amount'] = 0

        res = super(e2yun_customer_payment_extend, self).create(vals_list)

        #检查公司为集团是不允许保存
        if res.company_id.id == 1:
            raise Warning(
                _("请选择其他公司!"))
        # for a in res.payment_attachments:
        #     a.res_name = a.display_name
        self.env.cr.commit()
        if pos_flag and vals_list.get('create_uid',False):
            sql = """update account_payment set create_uid = """ + str(vals_list.get('create_uid')) + """ where id = """ + str(res.id)
            self._cr.execute(sql)

        #pos同步的不要再次同步回去
        if(not pos_flag):
            self.sync_customer_payment_to_pos(res)

        if res.sent_wx_message:
            self.transport_wechat_message(res)
            _logger.info("退款推送测试--5用户id%s" % res.partner_id)
        return res

    @api.one
    def write(self, vals):
        previous_state = self.state
        # vals['state'] = 'cancelled'
        new_state = vals.get('state')
        _logger.info("退款推送测试--1")

        res = super(e2yun_customer_payment_extend, self).write(vals)
        if self.sent_wx_message:
            if previous_state == 'draft':
                if new_state == 'cancelled':
                    _logger.info("退款推送测试--2")
                    self.transport_wechat_message2()
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

    # @api.depends('datas')
    # @api.onchange('datas')
    # def _onchange_name(self):
    #     self.name = self.datas_fname

    name = fields.Char('Name', required=False)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super(e2yun_customer_payment_extend2, self).create(vals_list)
    #     return res


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

class e2yun_customer_payment_crm_team(models.Model):
    _inherit = 'crm.team'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        flag = self.env.context.get('show_user_shops', False)
        user_shop = self.env.user.teams.ids
        shops =self.search([('id', 'in', user_shop)])
        # res = super(e2yun_customer_payment_crm_team, self).name_search(name, args, operator, limit)
        if flag == 4399:
            return shops.name_get()
        else:
            return super(e2yun_customer_payment_crm_team, self).name_search(name, args, operator, limit)

class e2yun_customer_payment_bank_info(models.Model):
    _name = 'payment_bank.info'
    _description = '银行帐号信息管理'

    name = fields.Char(related='bank_describe')
    shop_code = fields.Char('门店代码')
    bank_accont = fields.Char('银行账户科目编码')
    bank_describe = fields.Char('银行账户科目描述')
