# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo import exceptions
import datetime
class Agreement(models.Model):
    _inherit = "agreement"

    agreement_code=fields.Char('Agreement Code',default="/") #合同编码
    plan_sign_time=fields.Datetime('Plan Sign Time') # 计划回签时间
    property_product_pricelist = fields.Many2one('product.pricelist', string='Pricelist',default=1,)

    pdfswy = fields.Many2one('ir.attachment', string='Pdfswy',readonly='True')
    pdfqw = fields.Many2one('ir.attachment', string='Pdfqw',readonly='True' )
    fktj = fields.Many2one('ir.attachment', string='Fktj',readonly='True')

    @api.onchange("x_studio_htbz")
    def onchange_x_studio_htbz(self):
        oldhtbz = self.env['agreement'].search([('id', '=', self._origin.id)])
        if self.x_studio_htbz and oldhtbz:
            company_id = self.company_id or self.env.user.company_id
            create_date = self.create_date or fields.Date.today()
            currency = self.env['res.currency'].search([('name', '=', self.x_studio_htbz)])
            property_product_pricelist = self.env['product.pricelist'].search(
                [('name', 'like', '%' + oldhtbz.x_studio_htbz)])
            if currency and property_product_pricelist:
                currency_rate = self.env['res.currency']._get_conversion_rate(
                        property_product_pricelist.currency_id,currency,
                        company_id, create_date)
                self.x_studio_htje = round(float(self.x_studio_htje) * currency_rate, 2)
            else:
                raise exceptions.UserError("价格表没有维护的币别")

    @api.onchange('x_studio_htje')
    def _onchange_x_studio_htje(self):
            company_id = self.company_id or self.env.user.company_id
            create_date = self.create_date or fields.Date.today()
            currency = self.env['res.currency'].search([('name', 'like', '%USD%')])
            property_product_pricelist = self.env['product.pricelist'].search(
                [('name', 'like', '%' + self.x_studio_htbz + '%')])
            if currency and property_product_pricelist:
                currency_rate = self.env['res.currency']._get_conversion_rate(
                    property_product_pricelist.currency_id, currency,
                    company_id, create_date)
                self.x_studio_mjhtje = round(float(self.x_studio_htje) * currency_rate, 2)

    @api.onchange('x_studio_mjhtje')
    def _onchange_x_studio_mjhtje(self):
        company_id = self.company_id or self.env.user.company_id
        create_date = self.create_date or fields.Date.today()
        currency = self.env['res.currency'].search([('name', 'like', '%CNY%')])
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


        vals['x_studio_usd'] = 'USD'
        vals['x_studio_htbz'] = 'CNY'
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
            if vals['stage_id']==7 and self.x_studio_htje\
                    and self.partner_id and self.x_studio_jhhm_id:
                sql='update crm_lead set agreement_amount=%s,agreement_amount_usd=%s,agreement_code=%s,agreement_partner_id=%s where code=%s'
                self._cr.execute(sql,(self.x_studio_htje,self.x_studio_mjhtje,self.id,self.partner_id.id,self.x_studio_jhhm_id))

        return super(Agreement,self).write(vals)

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
        agreement_obj = self.env['agreement']
        agreement_datas = agreement_obj.search(
            [('stage_id', '<', 5)])
        tier_review_obj = self.env['tier.review']

        up_sequence={}
        for agreement_data in agreement_datas:
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
                            self.send_approval_emil_temp(agreement_data.id, partner_ids)
                            tier_review_data.is_send_email=True
                            break
                    else:
                        if up_sequence.get(tier_review_data.up_sequence):
                            tier_review_data_temp=up_sequence[tier_review_data.up_sequence]
                        else:
                            tier_review_data_temp = tier_review_datas[i - 1]
                        if tier_review_data_temp.status == 'approved':
                            partner_ids = []
                            if tier_review_data.w_approver_id:
                                partner_ids.append(tier_review_data.w_approver_id.partner_id.email)
                            else:
                                # 审批组、找到团队祖负责人
                                if agreement_data.assigned_user_id:
                                    partner_ids.append(
                                        agreement_data.assigned_user_id.sale_team_id.user_id.partner_id.email)
                            self.send_approval_emil_temp(agreement_data.id,partner_ids)
                            tier_review_data.is_send_email = True
                i = i + 1



    def send_approval_emil_temp(self,id,partner_ids):
        ir_model_data = self.env['ir.model.data']
        template_ids = ir_model_data.get_object_reference('e2yun_agreement_extend', 'email_template_check_agreement')[1]
        email_template_obj_message = self.env['mail.compose.message']
        if template_ids:
            attachment_ids_value = email_template_obj_message.onchange_template_id(template_ids, 'comment',
                                                                                   'agreement', id)
            if not partner_ids:
                return
            mails = self.env['mail.mail']
            mail_values = {
                'email_from': 'postmaster-odoo@e2yun.com',
                'email_to': partner_ids[0],
                'subject': attachment_ids_value['value']['subject'],
                'body_html': attachment_ids_value['value']['body'],
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
