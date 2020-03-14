# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo import exceptions
import datetime
from odoo.exceptions import UserError
class Agreement(models.Model):
    _inherit = "agreement"

    agreement_code=fields.Char('Agreement Code',default="/") #合同编码
    plan_sign_time=fields.Date('Plan Sign Time') # 计划回签时间
    signed_time = fields.Date('Signed Time')  # 合同签订时间
    sales_department = fields.Many2one('crm.team', string='Sales department')  # 合同签订时间

    x_studio_partner_id = fields.Many2one('res.partner', string='Customer Name')  # 客户名称
    x_studio_order_type1 = fields.Char(string='Order Type')  # 订单类型
    #销售合同的缔约流程
    sales_c_c_process=fields.Selection(	[["一般缔约流程","一般缔约流程"],["绿色通道类 Fast Pass","绿色通道（有模板备案）"],["不可协商类 Non-negotiable","不可协商类"],["事后合同类 After-fact","事后合同"]],string='Sales C C Process')

    x_studio_copy=fields.Char(string='备案号')  # 备案号
    x_studio_cytkh=fields.Char(string='差异条款号')  # 差异条款号
    x_studio_scjd=fields.Selection([["交付未完成","交付未完成"],["已验收，未付款","已验收，未付款"]],string='截至提交审核时， 项目所处阶段')  # 截至提交审核时

    x_studio_xmmc= fields.Char(string='Project Name')  # 项目名称

    #x_studio_jhhm_id = fields.Many2one('crm.lead', string='Opportunity Number')  # 机会号码OPP ID

    x_studio_jhhm_id = fields.Char(string='Opportunity Number')  # 机会号码OPP ID

    original_agreement_no= fields.Char(string='Original Agreement No')  # 原协议编号

    x_studio_customer_bu = fields.Many2one('crm.team', string='Customer Bu')  # 客户所属部门

    x_studio_jfssbu1 = fields.Many2one('crm.team', string='Delivery Bu')  # 交付所属部门


    property_product_pricelist = fields.Many2one('product.pricelist', string='Pricelist',default=1,)  #价格表

    income_type = fields.Many2many('agreement.income.type', string='Income Type')  #收入类型

    #产品线
    x_studio_cpx = fields.Selection(
        [["DGT", "DGT"], ["DTL", "DTL"], ["DVE", "DVE"], ["CHM", "CHM"], ["INN", "INN"], ["ERP", "ERP"], ["OCS", "OCS"],
         ["SIC", "SIC"], ["ADM", "ADM"], ["EMB", "EMB"], ["DPE", "DPE"], ["CRM", "CRM"], ["BDP", "BDP"], ["CLD", "CLD"],
         ["MSS", "MSS"], ["DVI", "DVI"], ["APT", "APT"], ["PRS", "PRS"], ["SIT", "SIT"], ["UXD", "UXD"], ["CMS", "CMS"],
         ["ECM", "ECM"], ["MOB", "MOB"], ["NXE", "NXE"], ["ONM", "ONM"], ["ACP", "ACP"], ["PGS", "PGS"], ["BIS", "BIS"],
         ["IMS", "IMS"], ["SPT", "SPT"], ["HDT", "HDT"], ["BPO", "BPO"], ["SIO", "SIO"], ["TRS", "TRS"], ["SIB", "SIB"]], string='Product line')

    x_studio_signing_entity = fields.Char(string='Pactera Contract Entity')  # 文思海辉签约实体

    x_studio_htbz = fields.Many2one('res.currency', string='Contract Currency')  #合同币种

    x_studio_htje = fields.Float(string='Contract Amount')

    x_studio_usd = fields.Char(string='美金合同币种',default='USD',readonly='True')

    x_studio_mjhtje = fields.Float(string='美金合同金额')

    x_studio_chco  = fields.Selection([["固定金额+计时计件","固定金额+计时计件"],["不涉及收费","不涉及收费"],["固定金额","固定金额"],["计时计件","计时计件"]],string='收费方式')  #收费方式

    x_studio_cgmpd = fields.Char(string='CGM')

    x_studio_eatpygsj = fields.Char(string='Front log相关数据') # Front log相关数据

    x_studio_pjhtlrl = fields.Char(string='平均合同利润率')  # 平均合同利润率

    x_studio_jfrys = fields.Char(string='平均合同利润率')  # 交付人员数

    x_studio_fkfs = fields.Selection([["月结 Monthly","月结 Monthly"],["每两月结算 Bimonthly","每两月结算 Bimonthly"],
                                          ["季结 Quarterly","季结 Quarterly"],
                                          ["按合同里程碑 Based on the Contract Milestone",
                                           "按合同里程碑 Based on the Contract Milestone"],
                                          ["项目全部验收后 After Project Completion Acceptance",
                                           "项目全部验收后 After Project Completion Acceptance"],["其他 Others","其他 Others"]],string='付款方式')

    x_studio_hkzl = fields.Char(string='回款账龄（自然日）')  # 回款账龄（自然日）

    #免税类型
    x_studio_mslx = fields.Selection([["离岸免税-offshore","离岸免税-offshore"],["四技免税-4T","四技免税-4T"],["海外实体-oversea LE","海外实体-oversea LE"],["不可免税-NA","不可免税-NA"],["无税合同-NA","无税合同-NA"]],string='免税类型')

    x_studio__dso_dayyg = fields.Char(string='预估 DSO Day')  #预估 DSO Day

    x_studio_dso_daypd = fields.Char(string='DSO Day判断')  # DSO Day判断

    x_studio_wwyzrsxtk = fields.Selection([["是","是"],["否","否"]],string='是否包含“无违约责任上限”条款')  # 是否包含“无违约责任上限”条款

    x_studio_hmdkh = fields.Selection([["是","是"],["否","否"]],string='是否为“黑名单”中的客户')  # 是否为“黑名单”中的客户

    x_studio_hmdyy = fields.Char(string='黑名单原因')  # DSO Day判断

    x_studio_xmjl1=fields.Many2one('res.users',string='项目经理')

    x_studio_xsdb1 = fields.Many2one('res.users', string='	销售代表')

    is_email_contract_text = fields.Boolean("Is Email Contract Text",default=True)

    is_email_sign_time = fields.Boolean("Is Email Sign time",default=True)

    pdfswy = fields.Many2one('ir.attachment', string='Pdfswy',readonly='True')
    pdfqw = fields.Many2one('ir.attachment', string='Pdfqw',readonly='True' )
    fktj = fields.Many2one('ir.attachment', string='Fktj',readonly='True')

    contract_text_attachment_ids = fields.Many2many(
        'ir.attachment', 'agreement_contract_text_ir_attachments_rel',
        'id', 'attachment_id', 'Contract Text End')   #合同文本最终版

    contract_text_clean_attachment_ids = fields.Many2many(
        'ir.attachment', 'agreement_contract_text_clean_ir_attachments_rel',
        'id', 'attachment_id', 'Contract Text Clean')  #清洁版

    contract_text_process_attachment_ids = fields.Many2many(
        'ir.attachment', 'agreement_contract_text_process_ir_attachments_rel',
        'id', 'attachment_id', 'Contract Text Process') #审批过程版


    pws_attachment_ids = fields.Many2many(
        'ir.attachment', 'agreement_pws_ir_attachments_rel',
        'id', 'attachment_id', 'pws')

    email_approval_attachment_ids = fields.Many2many(
        'ir.attachment', 'agreement_email_approval_ir_attachments_rel',
        'id', 'attachment_id', 'Email Approval')

    pdfswy_attachment_ids = fields.Many2many(
        'ir.attachment', 'agreement_pdfswy_ir_attachments_rel',
        'id', 'attachment_id', 'PDF SWY')

    pdfqw_attachment_ids = fields.Many2many(
        'ir.attachment', 'agreement_pdfqw_ir_attachments_rel',
        'id', 'attachment_id', 'PDF QW')

    fktj_attachment_ids = fields.Many2many(
        'ir.attachment', 'agreement_fktj_attachments_rel',
        'id', 'attachment_id', 'Payment Clause')

    pws_line_ids = fields.One2many(
        "agreement.pws.line",
        "agreement_id",
        string="PWS",
        copy=False)


    @api.onchange("agreement_subtype_id")
    def onchange_agreement_subtype_id(self):
        # 验证 MAD+SOW（主服务协议+工作说明书） 必须上传 PWS
        if self.agreement_subtype_id.name == 'MAD+SOW（主服务协议+工作说明书）':
            if not self.pws_line_ids and not self.pws_line_ids.pws_line_attachment_ids:
                raise UserError("合同子类型：MAD+SOW（主服务协议+工作说明书），请上传PWS导入")


    @api.onchange("assigned_user_id")
    def onchange_assigned_user_id(self):
        # 销售所属团队取自销售的团队 sale_team_id
        if self.assigned_user_id.sale_team_id:
            self.sales_department=self.assigned_user_id.sale_team_id

    @api.onchange("x_studio_htbz")
    def onchange_x_studio_htbz(self):
        oldhtbz = self.env['agreement'].search([('id', '=', self._origin.id)])
        if self.x_studio_htbz and oldhtbz and self.x_studio_htje:
            company_id = self.company_id or self.env.user.company_id
            create_date = self.create_date or fields.Date.today()
            currency = self.env['res.currency'].search([('name', '=', self.x_studio_htbz.name)])
            property_product_pricelist = self.env['product.pricelist'].search(
                [('name', 'like', '%' + oldhtbz.x_studio_htbz.name)])
            if currency and property_product_pricelist:
                currency_rate = self.env['res.currency']._get_conversion_rate(
                        property_product_pricelist.currency_id,currency,
                        company_id, create_date)
                self.x_studio_htje = round(float(self.x_studio_htje) * currency_rate, 2)
            else:
                raise exceptions.UserError("价格表没有维护的币别")

    @api.onchange('x_studio_htje')
    def _onchange_x_studio_htje(self):
        if self.x_studio_htbz and self.x_studio_htje:
            company_id = self.company_id or self.env.user.company_id
            create_date = self.create_date or fields.Date.today()
            currency = self.env['res.currency'].search([('name', 'like', '%USD%')])
            property_product_pricelist = self.env['product.pricelist'].search(
                [('name', 'like', '%' + self.x_studio_htbz.name + '%')])
            if currency and property_product_pricelist:
                currency_rate = self.env['res.currency']._get_conversion_rate(
                    property_product_pricelist.currency_id, currency,
                    company_id, create_date)
                self.x_studio_mjhtje = round(float(self.x_studio_htje) * currency_rate, 2)

    @api.onchange('x_studio_mjhtje')
    def _onchange_x_studio_mjhtje(self):
      if self.x_studio_htbz:
        company_id = self.company_id or self.env.user.company_id
        create_date = self.create_date or fields.Date.today()
        currency = self.env['res.currency'].search([('name', 'like', '%'+self.x_studio_htbz.name+'%')])
        property_product_pricelist = self.env['product.pricelist'].search(
            [('name', 'like', '%USD%')])
        if currency and property_product_pricelist:
            currency_rate = self.env['res.currency']._get_conversion_rate(
                property_product_pricelist.currency_id, currency,
                company_id, create_date)
            if not self.x_studio_htje:
                self.x_studio_htje = round(float(self.x_studio_mjhtje) * currency_rate, 2)



    @api.model
    def create(self, vals):
        vals['code'] = ""
        if 'agreement_subtype_id' in vals.keys() and vals['agreement_subtype_id']:
          agreement_subtype_obj = self.env['agreement.subtype'].browse(vals['agreement_subtype_id'])

          if agreement_subtype_obj.for_code and not (agreement_subtype_obj.name in '集团转包'
                                                     or agreement_subtype_obj.name in 'Other（其他）'):

            sequence_obj = self.env['ir.sequence']
            if 'agreement_type_id' in vals.keys():
                agreement_type_id=vals['agreement_type_id']
            else:
                agreement_type_id=self.agreement_type_id.id

            if agreement_type_id==1:
                agreement_code=sequence_obj.next_by_code('agreement.sale.code')
            elif agreement_type_id==2:
                agreement_code = sequence_obj.next_by_code('agreement.purchase.code')
            if agreement_code:
                verse_one=agreement_code[0:len(agreement_code)-4]
                verse_two=agreement_code[-4:]
                vals['agreement_code'] =verse_one+agreement_subtype_obj.for_code+verse_two
                vals['code'] = vals['agreement_code']

        if 'x_studio_htje' in vals.keys() or 'x_studio_mjhtje' in vals.keys():
            company_id = self.company_id or self.env.user.company_id
            create_date = self.create_date or fields.Date.today()
            queryCurrency=''
            queryPriceList=''
            if 'x_studio_mjhtje' in vals.keys() and vals['x_studio_mjhtje'] :
                queryCurrency='CNY'
                queryPriceList='USD'
                x_studio_htje = 'x_studio_mjhtje'
            elif 'x_studio_htje' in vals.keys() and vals['x_studio_htje'] :
                queryCurrency = 'USD'
                queryPriceList = 'CNY'
                x_studio_htje = 'x_studio_htje'

            currency = self.env['res.currency'].search([('name', 'like', '%'+queryCurrency+'%')])
            property_product_pricelist = self.env['product.pricelist'].search([('name', 'like', '%'+queryPriceList+'%')])

            if currency and property_product_pricelist:
                usd_currency_rate = self.env['res.currency']._get_conversion_rate(
                    property_product_pricelist.currency_id, currency,
                    company_id, create_date)
                if x_studio_htje=='x_studio_htje':
                    vals['x_studio_mjhtje']= round(float(vals['x_studio_htje']) * usd_currency_rate,2)
                elif x_studio_htje=='x_studio_mjhtje':
                    vals['x_studio_htje'] = round(float(vals['x_studio_mjhtje']) * usd_currency_rate, 2)

                if 'x_studio_mjhtje' in vals.keys() and vals['x_studio_mjhtje']:
                    vals['x_studio_mjhtje'] = ("%.2f" % float(vals['x_studio_mjhtje']))
                if 'x_studio_htje' in vals.keys() and vals['x_studio_htje']:
                    vals['x_studio_htje'] = ("%.2f" % float(vals['x_studio_htje']))

        if  not 'x_studio_htbz' in vals.keys():
            vals['x_studio_htbz'] = 'CNY'

        vals['x_studio_usd'] = 'USD'
        return super(Agreement, self).create(vals)

    def write(self, vals):
        if 'agreement_subtype_id' in vals.keys() and vals['agreement_subtype_id']:
          agreement_subtype_obj = self.env['agreement.subtype'].browse(vals['agreement_subtype_id'])

          if agreement_subtype_obj.for_code and not (agreement_subtype_obj.name in'集团转包'
                                                  or agreement_subtype_obj.name in '其他' ):
            sequence_obj = self.env['ir.sequence']
            if 'agreement_type_id' in vals.keys():
                agreement_type_id=vals['agreement_type_id']
            else:
                agreement_type_id=self.agreement_type_id.id

            if agreement_type_id==1:
                agreement_code=sequence_obj.next_by_code('agreement.sale.code')
            elif agreement_type_id==2:
                agreement_code = sequence_obj.next_by_code('agreement.purchase.code')
            if agreement_code:
                verse_one=agreement_code[0:len(agreement_code)-4]
                verse_two=agreement_code[-4:]
                vals['agreement_code'] =verse_one+agreement_subtype_obj.for_code+verse_two
                vals['code'] = vals['agreement_code']

        # if 'x_studio_htje' in vals.keys():
        #     company_id = self.company_id or self.env.user.company_id
        #     create_date = self.create_date or fields.Date.today()
        #     usd_currency = self.env['res.currency'].search([('name', '=', 'USD')])
        #     property_product_pricelist = self.env['product.pricelist'].search([('name', 'like', '%CNY%')])
        #     usd_currency_rate = self.env['res.currency']._get_conversion_rate(
        #         property_product_pricelist.currency_id, usd_currency,
        #         company_id, create_date)
        #     vals['x_studio_mjhtje'] = round(float(vals['x_studio_htje']) * usd_currency_rate, 2)
        #
        # elif 'x_studio_mjhtje' in vals.keys():
        #     company_id = self.company_id or self.env.user.company_id
        #     create_date = self.create_date or fields.Date.today()
        #     usd_currency = self.env['res.currency'].search([('name', '=', 'CNY')])
        #     property_product_pricelist = self.env['product.pricelist'].search([('name', 'like', '%USD%')])
        #     usd_currency_rate = self.env['res.currency']._get_conversion_rate(
        #         property_product_pricelist.currency_id, usd_currency,
        #         company_id, create_date)
        #     vals['x_studio_htje'] = round(float(vals['x_studio_mjhtje']) * usd_currency_rate, 2)

        if 'x_studio_mjhtje' in vals.keys() and vals['x_studio_mjhtje']:
            vals['x_studio_mjhtje'] = ("%.2f" % float(vals['x_studio_mjhtje']))
        if 'x_studio_htje' in vals.keys() and vals['x_studio_htje']:
            vals['x_studio_htje'] = ("%.2f" % float(vals['x_studio_htje']))

        if 'stage_id' in vals.keys():
            #回写机会 订单
            if vals['stage_id']==7 and self.x_studio_htje\
                    and self.x_studio_partner_id and self.x_studio_jhhm_id:
                sql='update crm_lead set agreement_amount=%s,agreement_amount_usd=%s,agreement_code=%s,agreement_partner_id=%s where code=%s'
                self._cr.execute(sql,(self.x_studio_htje,self.x_studio_mjhtje,self.id,self.x_studio_partner_id.id,self.x_studio_jhhm_id))

        if 'pws_line_ids' in vals.keys():
            super(Agreement, self).write(vals)

            sum_cgm = 0
            sum_amount = 0

            if self.pws_line_ids:
                for pwsObj in self.pws_line_ids:
                    if pwsObj.cgm and pwsObj.x_studio_htje:
                        cgm = pwsObj.cgm.strip('%')
                        sum_cgm = sum_cgm + (pwsObj.x_studio_htje * (float(cgm) / 100))
                        sum_amount = sum_amount + pwsObj.x_studio_htje

            if sum_cgm != 0 and sum_amount != 0:
                x_studio_cgmpd = str(round((sum_cgm / sum_amount) * 100)) + "%"
                x_studio_mjhtje=0
                #计算汇总后的美金金额
                if self.x_studio_htbz:
                    company_id = self.company_id or self.env.user.company_id
                    create_date = self.create_date or fields.Date.today()
                    currency = self.env['res.currency'].search([('name', 'like', '%USD%')])
                    property_product_pricelist = self.env['product.pricelist'].search(
                        [('name', 'like', '%' + self.x_studio_htbz.name + '%')])
                    if currency and property_product_pricelist:
                        currency_rate = self.env['res.currency']._get_conversion_rate(
                            property_product_pricelist.currency_id, currency,
                            company_id, create_date)
                        x_studio_mjhtje = round(float(sum_amount) * currency_rate, 2)

                sql = "update agreement set x_studio_cgmpd=%s,x_studio_htje=%s,x_studio_mjhtje=%s where id=%s"
                self._cr.execute(sql, (x_studio_cgmpd, sum_amount,x_studio_mjhtje, self.id))

            return True
        else:
            return super(Agreement, self).write(vals)




    def send_approval_warn_emlil(self,interval_time):
        #mail.template / name_search
        #查找阶段为 待审批与审批中的数据
        agreement_obj=self.env['agreement']
        tier_review_obj = self.env['tier.review']
        agreement_datas = agreement_obj.search(
            [('stage_id', '<', 5)])
        day = datetime.timedelta(days=interval_time)
        for agreement_data in agreement_datas:
            tier_review_datas=tier_review_obj.search(
            [('res_id', '=', agreement_data.id)],  order="sequence asc" )
            i=0
            while i< len(tier_review_datas):
                tier_review_data=tier_review_datas[i]
                if tier_review_data.status!='approved':
                    if i==0:
                        now = datetime.datetime.now()
                        if (tier_review_data.write_date+day)<now:
                            partner_ids = []
                            if tier_review_data.w_approver_id:
                                partner_idsids=[]
                                partner_idsids.append(tier_review_data.w_approver_id.partner_id.id)
                               #partner_ids.append([6, False, partner_idsids])
                                partner_ids.append(tier_review_data.w_approver_id.partner_id.email)
                                self.emil_temp(agreement_data.id,partner_ids)
                            else:
                                #审批组、找到团队祖负责人
                                if agreement_data.assigned_user_id:
                                    partner_idsids = []
                                    partner_idsids.append(agreement_data.assigned_user_id.sale_team_id.user_id.id)
                                    #partner_ids.append([6, False, partner_idsids])
                                    partner_ids.append(agreement_data.assigned_user_id.sale_team_id.user_id.partner_id.email)
                                    self.emil_temp(agreement_data.id, partner_ids)
                            break
                    else:
                        tier_review_data_temp = tier_review_datas[i-1]
                        now = datetime.datetime.now()
                        if (tier_review_data_temp.write_date + day) < now:
                            partner_ids = []
                            if tier_review_data.w_approver_id:
                                partner_idsids = []
                                partner_idsids.append(tier_review_data.w_approver_id.partner_id.id)
                                #partner_ids.append([6, False, partner_idsids])
                                partner_ids.append(tier_review_data.w_approver_id.partner_id.email)
                                self.emil_temp(agreement_data.id, partner_ids)
                            else:
                                # 审批组、找到团队祖负责人
                                if agreement_data.assigned_user_id:
                                    partner_idsids = []
                                    partner_idsids.append(agreement_data.assigned_user_id.sale_team_id.user_id.id)
                                    #partner_ids.append([6, False, partner_idsids])
                                    partner_ids.append(agreement_data.assigned_user_id.sale_team_id.user_id.partner_id.email)
                                    self.emil_temp(agreement_data.id, partner_ids)
                            break

                i=i+1

        #验证最后一次的审批时
        return  True

    def emil_temp(self,id,partner_ids):
        ir_model_data = self.env['ir.model.data']
        template_ids = ir_model_data.get_object_reference('e2yun_agreement_extend', 'email_template_rocp_agreement')[1]
        email_template_obj_message = self.env['mail.compose.message']
        if template_ids:
            attachment_ids_value = email_template_obj_message.onchange_template_id(template_ids, 'comment',
                                                                                   'agreement', id)
            # vals = {}
            # vals['composition_mode'] = 'mass_mail'
            # vals['template_id'] = template_ids
            # vals['parent_id'] = False
            # vals['notify'] = False
            # vals['no_auto_thread'] = False
            # vals['reply_to'] = False
            # vals['model'] = 'agreement'
            # vals['partner_ids'] =partner_ids
            # vals['body'] = attachment_ids_value['value']['body']
            # vals['res_id'] = id
            # #vals['email_from'] = attachment_ids_value['value']['email_from']
            # vals['email_from'] = 'postmaster-odoo@e2yun.com'
            # vals['subject'] = attachment_ids_value['value']['subject']

            #attachment_ids = []

            #attachmentObj = self.env['ir.attachment']  # 附件

            #attachmentData = attachmentObj.search([('res_model', '=', 'agreement.file.upload'),
            #                                             ('res_id', '=', self.id), ('res_name', '=', 'pdfswy')])

            #attachment_ids = []
            #attachment_ids.append([6, False, [4097]])
            #vals['attachment_ids'] = attachment_ids

            # mail_compose=self.env['mail.compose.message'].create(vals)
            #
            # mail_compose.action_send_mail()
            if not partner_ids:
                return
            mails = self.env['mail.mail']
            mail_values = {
                'email_from': 'postmaster-odoo@e2yun.com',
                # 'reply_to': '981274333@qq.com',
                'email_to': partner_ids[0],
                'subject': attachment_ids_value['value']['subject'],
                'body_html': attachment_ids_value['value']['body'],
                'notification': True,
                # 'mailing_id': mailing.id,
                'auto_delete': True,
            }
            mail = self.env['mail.mail'].create(mail_values)
            mails |= mail
        mails.send()


    def send_approval_emil(self):
        #阶段待处理审批邮件
        agreement_obj = self.env['agreement']
        agreement_datas = agreement_obj.search(
            [('stage_id', '<', 7)])
        tier_review_obj = self.env['tier.review']

        up_sequence={}
        for agreement_data in agreement_datas:
            #阶段审批邮件提醒
          if int(agreement_data.stage_id)<4:
            tier_review_datas = tier_review_obj.search(
                [('res_id', '=', agreement_data.id)], order="sequence asc")

            i = 0
            while i < len(tier_review_datas):
                tier_review_data = tier_review_datas[i]
                up_sequence[tier_review_data.cp_sequence]=tier_review_data
                if tier_review_data.status != 'approved' and tier_review_data.is_send_email==False:
                    if i == 0:
                            partner_ids = []
                            if tier_review_data.w_approver_id:
                                partner_ids.append(tier_review_data.w_approver_id.partner_id.email)
                            else:
                                # 审批组、找到团队祖负责人
                                if agreement_data.assigned_user_id:
                                    partner_ids.append(
                                        agreement_data.assigned_user_id.sale_team_id.user_id.partner_id.email)
                            self.send_approval_emil_temp(agreement_data.id, partner_ids,'email_template_check_agreement')
                            tier_review_data.is_send_email=True
                            break
                    else:
                        partner_ids = []
                        if tier_review_data.status == 'rejected':
                            if tier_review_data.requested_by:
                                partner_ids.append(tier_review_data.requested_by.partner_id.email)
                                self.send_approval_emil_temp(agreement_data.id, partner_ids,'email_template_rejected_agreement')
                                tier_review_data.is_send_email = True
                                break

                        if up_sequence.get(tier_review_data.up_sequence):
                            tier_review_data_temp=up_sequence[tier_review_data.up_sequence]
                            #上级平行审批情况下处理
                            for datatemp in tier_review_datas:
                                if datatemp.definition_id.sequence==tier_review_data.up_sequence:
                                    if datatemp.status != 'approved':
                                        tier_review_data_temp=datatemp
                                        break
                        else:
                            tier_review_data_temp = tier_review_datas[i - 1]
                        if tier_review_data_temp.status == 'approved':
                            if tier_review_data.w_approver_id:
                                partner_ids.append(tier_review_data.w_approver_id.partner_id.email)
                            else:
                                # 审批组、找到团队祖负责人
                                if agreement_data.assigned_user_id:
                                    partner_ids.append(
                                        agreement_data.assigned_user_id.sale_team_id.user_id.partner_id.email)
                            self.send_approval_emil_temp(agreement_data.id,partner_ids,'email_template_check_agreement')
                            tier_review_data.is_send_email = True



                i = i + 1

          elif int(agreement_data.stage_id)==4 and \
                  agreement_data.is_email_contract_text==False:
              partner_ids=[]
              sql="select reviewer_id from tier_definition where  model='agreement' and name like '%法务%' limit 1 ";

              self._cr.execute(sql)
              partner_id=self._cr.fetchone()
              if partner_id:
                reviewer_user=self.env['res.users'].browse(partner_id[0])
                partner_ids.append(reviewer_user.partner_id.email)
                self.send_approval_emil_temp(agreement_data.id, partner_ids, 'email_template_upload_contract_agreement')
                sql = "UPDATE  agreement set is_email_contract_text=%s where id=%s"
                self._cr.execute(sql, ('t', agreement_data.id))
          elif int(agreement_data.stage_id)==5 and agreement_data.is_email_sign_time==False:
              partner_ids = []
              if agreement_data.assigned_user_id:
                  partner_ids.append(agreement_data.assigned_user_id.partner_id.email)
                  self.send_approval_emil_temp(agreement_data.id, partner_ids,
                                               'email_template_signing_back_agreement')
                  sql = "UPDATE  agreement set is_email_sign_time=%s where id=%s"
                  self._cr.execute(sql, ('t', agreement_data.id))

    def send_approval_emil_temp(self,id,partner_ids,emil_template):
        if not partner_ids:
            return
        ir_model_data = self.env['ir.model.data']
        template_ids = ir_model_data.get_object_reference('e2yun_agreement_extend', emil_template)[1]
        email_template_obj_message = self.env['mail.compose.message']
        if template_ids:
            attachment_ids_value = email_template_obj_message.onchange_template_id(template_ids, 'comment',
                                                                                   'agreement', id)

            agreement_data=self.env['agreement'].browse(id)
            # if agreement_data and agreement_data.fktj_attachment_ids:
            #     # 带附件
            #     sqld = "delete  from email_template_attachment_rel where email_template_id=%s "
            #     self._cr.execute(sqld, (template_ids,))
            #     for fktj_attachment_id in agreement_data.fktj_attachment_ids:
            #         sql = "insert into email_template_attachment_rel(email_template_id,attachment_id)values (%s,%s)"
            #         self._cr.execute(sql, (template_ids, fktj_attachment_id.id))

            mails = self.env['mail.mail']
            mail_values = {
                'email_from': 'postmaster-odoo@e2yun.com',
                'email_to': partner_ids[0],
                'subject': attachment_ids_value['value']['subject'],
                'body_html': attachment_ids_value['value']['body'],
               # 'attachment_ids': [(4, attachment.id) for attachment in agreement_data.fktj_attachment_ids],
                'notification': True,
                'auto_delete': True,
            }
            mail = self.env['mail.mail'].create(mail_values)
            mails |= mail
        mails.send()

    def import_file(self):
        print(self.id)
        wizard = self.env.ref(
            'e2yun_agreement_extend.view_agreement_file_import')
        return {
            'name': '导入文件',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'agreement.file.upload',
            'views': [(wizard.id, 'form')],
            'view_id': wizard.id,
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    @api.multi
    def download_pdfswy(self):

        attachmentObj = self.env['ir.attachment']  # 附件

        # attachmentData = attachmentObj.search([('res_model', '=', 'agreement.file.upload'),
        #                                              ('res_id', '=', self.id), ('res_name', '=', 'pdfswy')])

        sql="select id  from ir_attachment where  res_id = %s  and res_name = %s and res_model = %s "
        self._cr.execute(sql, (self.id, 'pdfswy','agreement.file.upload'))
        attachmentSqlData = self._cr.fetchone()
        if not attachmentSqlData:
            return  False
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/%s?download=true' % (attachmentSqlData[0]),
        }

    @api.multi
    def download_pdfqw(self):

        attachmentObj = self.env['ir.attachment']  # 附件

        # attachmentData = attachmentObj.search([('res_model', '=', 'agreement.file.upload'),
        #                                              ('res_id', '=', self.id), ('res_name', '=', 'pdfswy')])

        sql = "select id  from ir_attachment where  res_id = %s  and res_name = %s and res_model = %s "
        self._cr.execute(sql, (self.id, 'pdfqw', 'agreement.file.upload'))
        attachmentSqlData = self._cr.fetchone()
        if not attachmentSqlData:
            return False
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/%s?download=true' % (attachmentSqlData[0]),
        }

    @api.multi
    def download_fktj(self):

        attachmentObj = self.env['ir.attachment']  # 附件

        # attachmentData = attachmentObj.search([('res_model', '=', 'agreement.file.upload'),
        #                                              ('res_id', '=', self.id), ('res_name', '=', 'pdfswy')])

        sql = "select id  from ir_attachment where  res_id = %s  and res_name = %s and res_model = %s "
        self._cr.execute(sql, (self.id, 'fktj', 'agreement.file.upload'))
        attachmentSqlData = self._cr.fetchone()
        if not attachmentSqlData:
            return False
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/%s?download=true' % (attachmentSqlData[0]),
        }

    @api.multi
    def action_emil_send1(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('e2yun_agreement_extend', 'email_template_temp_agreement')[1]

            sqld="delete  from email_template_attachment_rel where email_template_id=%s "
            self._cr.execute(sqld,(template_id,))

            sql = "insert into email_template_attachment_rel(email_template_id,attachment_id)values (%s,%s)"
            if self.pdfswy:
                self._cr.execute(sql, (template_id,self.pdfswy.id))
            if self.pdfqw:
                self._cr.execute(sql, (template_id, self.pdfqw.id))
            if self.fktj:
                self._cr.execute(sql, (template_id, self.fktj.id))

        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'agreement',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })

        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_template(template.lang, ctx['default_model'], ctx['default_res_id'])


        ctx['model_description'] = 'TEST'

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_emil_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('e2yun_agreement_extend', 'email_template_temp_agreement')[1]

            sqld="delete  from email_template_attachment_rel where email_template_id=%s "
            self._cr.execute(sqld,(template_id,))

            sql = "insert into email_template_attachment_rel(email_template_id,attachment_id)values (%s,%s)"
            if self.pdfswy:
                self._cr.execute(sql, (template_id,self.pdfswy.id))
            if self.pdfqw:
                self._cr.execute(sql, (template_id, self.pdfqw.id))
            if self.fktj:
                self._cr.execute(sql, (template_id, self.fktj.id))

        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'agreement',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })

        # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
        # object. Therefore, we pass the model description in the context, in the language in which
        # the template is rendered.
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_template(template.lang, ctx['default_model'], ctx['default_res_id'])

        self = self.with_context(lang=lang)

        ctx['model_description'] = _('Purchase Order')

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def unlink(self):
        for agree in self:
            if int(agree.stage_id)>1 and self._uid!=2:
                raise UserError(("进入过BO审阅的合同申请记录都不能自行删除"))
            super(Agreement,agree).unlink()



class AgreementSubtype(models.Model):
    _inherit = "agreement.subtype"

    for_code = fields.Char(string="For Code", required=True)


class AgreementLine(models.Model):
    _inherit = "agreement.line"

    price_unit = fields.Float(string='单价', required=True)
    taxes_id = fields.Many2many('account.tax', string='税率', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_subtotal = fields.Float(compute='_compute_amount', string='小计', store=True)


    @api.depends('qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            if line.taxes_id:
                vals = line._prepare_compute_all_values()
                line.update({
                    'price_subtotal': (vals['price_unit']*vals['qty'])-(vals['price_unit']*vals['qty']*vals['amount']),
                })

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'qty': self.qty,
            'amount':self.taxes_id[0].amount/100,
        }


class AgreementPwsLine(models.Model):
    _name = "agreement.pws.line"
    _description = "Agreement Pws Lines"

    pid = fields.Char(
        string="PID")

    cgm = fields.Char(
        string="CGM")

    pws_line_attachment_ids = fields.Many2many(
        'ir.attachment', 'agreement_pws_line_ir_attachments_rel',
        'id', 'attachment_id', 'PWS')

    agreement_id = fields.Many2one(
        "agreement",
        string="Agreement",
        ondelete="cascade")

    taxes_id = fields.Many2many('account.tax', string='税率', domain=['|', ('active', '=', False), ('active', '=', True)])
    x_studio_htje = fields.Float('htjr')
    x_studio_jfssbu = fields.Many2one('crm.team', '交付所属部门')
    x_studio_htbz= fields.Many2one('res.currency', '币种')
    x_studio_mjhtje = fields.Float('mjhtjr')


class AgreementIncomeType(models.Model):
    _name = "agreement.income.type"
    _description = "Agreement Income Type"

    name=fields.Char(string='收入类型')