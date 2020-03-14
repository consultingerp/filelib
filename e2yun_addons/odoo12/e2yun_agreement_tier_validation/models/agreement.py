# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import datetime
try:
    from odoo.addons.e2yun_agreement_tier_validation.models import get_zone_datetime
except BaseException as b:
    pass
class Agreement(models.Model):
    _name = "agreement"
    _inherit = ['agreement', 'tier.validation']
    _stage_id_from = ['1', '2', '3']
    _stage_id_to = ['4']

    rebut_tier = fields.Boolean()

    can_review = fields.Boolean(compute="_compute_can_review")

    bo_review= fields.Char()

    is_creator=fields.Boolean(default=False)


    @api.multi
    def _compute_can_review(self):
        for rec in self:
            #rec.can_review = self.env.user in rec.reviewer_ids
            rec.can_review = self.env.user in  rec.review_ids.filtered(
                lambda r: r.status == 'pending').mapped('reviewer_ids')

            if rec.can_review and rec.approve_sequence:
                sequence = rec.review_ids.filtered(
                    lambda r: r.status in ('pending', 'rejected') and
                              (self.env.user in r.reviewer_ids)).mapped('sequence')
                sequence.sort()
                my_sequence = sequence[0]
                tier_bf = rec.review_ids.filtered(
                    lambda r: r.status != 'approved' and r.sequence < my_sequence)
                if tier_bf:
                    rec.can_review = False

            if rec.can_review==True:
                for review in  rec.review_ids:
                    if review.reviewer_id.id==self.env.user.id:
                        if review.up_sequence:
                            can_review=rec.review_ids.filtered(lambda r:r.cp_sequence==review.up_sequence
                                                            and  r.status=='approved')
                            if can_review:
                                rec.can_review = True
                            else:
                                rec.can_review = False

                # node_name = rec.review_ids.filtered(
                #     lambda r: r.status in ('pending', 'rejected') and
                #                   (self.env.user in r.reviewer_ids)).mapped('node_name')
                # if node_name:
                #      rec.bo_review = node_name[0]


    approve_sequence = fields.Boolean(
        compute='_compute_approve_sequence',
    )


    @api.multi
    def _compute_approve_sequence(self):
        for rec in self:
            approve_sequence = rec.review_ids.filtered(
                lambda r: r.status in ('pending', 'rejected') and
                (self.env.user in r.reviewer_ids)).mapped('approve_sequence')

            rec.approve_sequence = True in approve_sequence

    rebut = fields.Boolean(
        compute='_compute_rebut',
    )
    reject = fields.Boolean(
        compute='_compute_reject',
    )

    @api.multi
    def _compute_rebut(self):
        for rec in self:
            rebut = rec.review_ids.filtered(
                lambda r: r.rebut==True and
                          self.env.user in r.reviewer_ids)
            if rebut:
              rec.rebut = True
            else:
              rec.rebut = False

    @api.multi
    def _compute_reject(self):
        for rec in self:
            reject = rec.review_ids.filtered(
                lambda r: r.reject == True and
                          self.env.user in r.reviewer_ids)
            if reject:
                rec.reject = True
            else:
                rec.reject = False

    @api.multi
    def _compute_validated_rebut_tier(self, reviews):
        """Override for different validation policy."""
        if not reviews:
            return False

        user_reviews = reviews.filtered(
            lambda r: r.status in ('pending') and
                      (self.env.user in r.reviewer_ids))
        sequence = user_reviews.sequence - 1

        for review in reviews:
            if review.sequence == sequence:
                return True

        return False

    @api.multi
    def rebut_tier(self):
        self.ensure_one()
        if self.has_comment:
            return self._add_comment('rebut')
        self._rejected_tier()
        self._update_counter()

    @api.multi
    def request_validation(self):
        td_obj = self.env['tier.definition']
        tr_obj = created_trs = self.env['tier.review']
        partner_ids = []
        if self._uid != self.create_uid.id and self._uid != self.assigned_user_id.id:
            raise UserError(u'仅提交人可以修改发起的合同。')
        else:
            if self.agreement_subtype_id.name == 'MAD+SOW（主服务协议+工作说明书）':
                if not self.pws_line_ids and not self.pws_line_ids.pws_line_attachment_ids:
                    raise UserError("合同子类型：MAD+SOW（主服务协议+工作说明书），请上传PWS导入")

        for rec in self:
            if getattr(rec, self._state_field) in self._state_from:
                if rec.need_validation:
                    tier_definitions = td_obj.search([
                        ('model', '=', self._name)], order="sequence asc")
                    sequence = 0
                    for td in tier_definitions:
                        is_send_email = False
                        if rec.evaluate_tier(td):
                            sequence += 1
                            if td.review_type=='group':
                                w_approver=td.reviewer_group_id.name
                                w_approver_id=""
                                 #组找对应的团队领导
                                if sequence == 1:
                                    if self.assigned_user_id:
                                        partner_ids.append(self.assigned_user_id.sale_team_id.user_id.partner_id.email)

                            else:
                                w_approver = td.reviewer_id.name
                                w_approver_id = td.reviewer_id.id
                                if sequence == 1:
                                    partner_ids.append(td.reviewer_id.partner_id.email)
                            created_trs += tr_obj.create({
                                'model': self._name,
                                'res_id': rec.id,
                                'definition_id': td.id,
                                'sequence': sequence,
                                'requested_by': self.env.uid,
                                'up_sequence': td.up_sequence,
                                'cp_sequence':td.sequence,
                                'rebut': td.rebut,
                                'reject': td.reject,
                                'w_approver':w_approver,
                                'w_approver_id': w_approver_id,
                                'tier_stage_id':td.tier_stage_id.id,
                                'is_send_email':is_send_email,
                                'node_name':td.name,
                            })

                    self._update_counter()
        self._notify_review_requested(created_trs)
        #self.emil_temp(self.id, partner_ids)

        sql = "UPDATE  agreement set stage_id=%s where id=%s"
        self._cr.execute(sql, (3, self.id))

        return created_trs


    @api.multi
    def restart_validation(self):
        if self._uid != self.create_uid.id and self._uid != self.assigned_user_id.id:
            raise UserError(u'仅提交人可以修改发起的合同。')
        for rec in self:
            if getattr(rec, self._state_field) in self._state_from:
                rec.mapped('review_ids').unlink()
                self._update_counter()
        sql = "UPDATE  agreement set stage_id=%s where id=%s"
        self._cr.execute(sql, (1, self.id))

    def _rebut_tier(self, tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids

        user_reviews = tier_reviews.filtered(
            lambda r: r.status in ('pending') and
                      (self.env.user in r.reviewer_ids))
        sequence=user_reviews.sequence-1

        for tier_review in tier_reviews:
            if tier_review.sequence==sequence:
                user_reviews=tier_review

        GetDatetime = get_zone_datetime.GetDatetime()
        reviewed_date = GetDatetime.get_datetime()
        user_reviews.write({
            'status': 'pending',
            'done_by': '',
            'reviewed_date': reviewed_date,
        })
        for review in user_reviews:
            rec = self.env[review.model].browse(review.res_id)
            rec._notify_accepted_reviews()


    def emil_temp(self,id,partner_ids):
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
                'body_html':attachment_ids_value['value']['body'],
                'notification': True,
               # 'mailing_id': mailing.id,
                'auto_delete': True,
            }
            mail = self.env['mail.mail'].create(mail_values)
            mails |= mail
        mails.send()


    def _validate_tier_extend(self, body,attachment_ids,tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status in ('pending', 'rejected') and
            (self.env.user in r.reviewer_ids))

        GetDatetime = get_zone_datetime.GetDatetime()
        reviewed_date = GetDatetime.get_datetime()

        user_reviews.write({
            'status': 'approved',
            'done_by': self.env.user.id,
            'reviewed_date': reviewed_date,
        })
        for review in user_reviews:
            rec = self.env[review.model].browse(review.res_id)
            rec._notify_accepted_reviews_extend(body,attachment_ids)

    def _notify_accepted_reviews_extend(self,body,attachment_ids):
        if hasattr(self, 'message_post'):
            # Notify state change
            getattr(self, 'message_post')(
                subtype='mt_comment',
                body=body,
                attachment_ids=attachment_ids
            )

    def _rejected_tier_extend(self, body,attachment_ids,tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status in ('pending', 'approved') and
            (r.reviewer_id == self.env.user or
             r.reviewer_group_id in self.env.user.groups_id))

        GetDatetime = get_zone_datetime.GetDatetime()
        reviewed_date = GetDatetime.get_datetime()

        user_reviews.write({
            'status': 'rejected',
            'done_by': self.env.user.id,
            'reviewed_date':reviewed_date,
        })
        for review in user_reviews:
            rec = self.env[review.model].browse(review.res_id)
            rec._notify_rejected_review_extend(body,attachment_ids)

    def _notify_rejected_review_extend(self,body,attachment_ids):
        if hasattr(self, 'message_post'):
            # Notify state change
            getattr(self, 'message_post')(
                subtype='mt_comment',
                body=body,
                attachment_ids=attachment_ids
            )

class CommentWizard(models.TransientModel):
    _inherit = 'comment.wizard'
    _description = 'Comment Wizard'

    check_advise = fields.Html('Contents', default='', sanitize_style=True,  required=True,)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'agreement_tier_validation_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')

    comment = fields.Char('comment', required=False)
    comment_temp = fields.Char('comment Temp')

    @api.multi
    def add_comment(self):
        self.ensure_one()
        rec = self.env[self.res_model].browse(self.res_id)
        tier_stage_id=""
        user_reviews = self.env['tier.review'].search([
            ('model', '=', self.res_model),
            ('res_id', '=', self.res_id),
            ('definition_id', 'in', self.definition_ids.ids)
        ])
        import re
        #check_advise_temp = re.findall(r'[^<p/>]', self.check_advise, re.S)
        #check_advise_temp = "".join(check_advise_temp)
        comp = re.compile('</?\w+[^>]*>')
        check_advise_temp = comp.sub('', self.check_advise)

        self.comment=check_advise_temp[0:5]+"..."
        for user_review in user_reviews:
            user_review.write({
                'comment': self.comment,
                'comment_temp':check_advise_temp,
            })
            if user_review.tier_stage_id:
                tier_stage_id = user_review.tier_stage_id
        attachment_ids=[]
        for attachment_id in  self.attachment_ids:
            attachment_ids.append(attachment_id.id)
        if self.validate_reject == 'validate':
            body = '审批通过:' + self.check_advise
            rec._validate_tier_extend(body,attachment_ids)
        if self.validate_reject == 'reject':
            body = '审批拒绝:' + self.check_advise
            rec._rejected_tier_extend(body,attachment_ids)
        if self.validate_reject == 'rebut':
            rec._rebut_tier()

        if tier_stage_id!="":
            if int(tier_stage_id)==5:
                #更新合同文本上传提醒邮件标识
               sql = "UPDATE  agreement set is_email_contract_text=%s where id=%s"
               self._cr.execute(sql, ('f',self.res_id))
            else:
                sql = "UPDATE  agreement set stage_id=%s where id=%s"
                self._cr.execute(sql, (tier_stage_id, self.res_id))

        rec._update_counter()




class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    @api.multi
    def write(self, vals):
        #管理员 可做任何操作
        #ZCTA.ZCONTRACT_SYS_MANAGE
        groups_id = self.env.ref('ZCTA.ZCONTRACT_SYS_MANAGE').id
        sql = 'SELECT * from res_groups_users_rel where gid=%s and uid=%s'
        self._cr.execute(sql, (groups_id, self._uid,))
        groups_users = self._cr.fetchone()
        if groups_users:
            return super(TierValidation, self).write(vals)
        msg="该操作正在审批中"
        if int(self.stage_id)>=6:
            msg="该操作审批已结束"

        #草稿状态下 只能创建人能编辑
        if int(self.stage_id.id)<=1 and (self._uid!=self.create_uid.id and self._uid!=self.assigned_user_id.id):
            raise UserError(u'仅提交人可以修改发起的合同。')


        flag_stage_id=False
        flag_plan_sign_time = False
        flag_signed_time=False
        flag_message_main_attachment_id=False
        no_check=False
        signed_time=None
        is_email_sign_time=None


        for key in vals:
            if 'stage_id'!=key and 'revision'!=key:
                flag_stage_id=True
            if 'plan_sign_time'!=key and 'revision'!=key:
                flag_plan_sign_time=True

            if 'signed_time'!=key and 'revision'!=key:
                flag_signed_time=True
            if 'message_main_attachment_id' != key and 'revision' != key:
                flag_message_main_attachment_id=True

            #验证清洁版附件不能删除
            if 'contract_text_clean_attachment_ids'== key :

                # if self.bo_review != '审阅人-法务':
                #     raise UserError(u'仅法务可以更新清洁版合同文本。')
                groups_id = self.env.ref('ZCTA.ZCONTRACT_CHECK_LEGAL').id
                sql = 'SELECT * from res_groups_users_rel where gid=%s and uid=%s'
                self._cr.execute(sql, (groups_id, self._uid,))
                groups_users = self._cr.fetchone()
                if not groups_users:
                    raise UserError(u'仅法务可以更新清洁版合同文本。')


                if self.contract_text_clean_attachment_ids:
                    for contract_text_clean_attachment_id in self.contract_text_clean_attachment_ids :
                        if not contract_text_clean_attachment_id.id in vals['contract_text_clean_attachment_ids'][0][2]:
                            raise UserError(u'不能删除上传过的任何文档。')

            #验证审批过程版的附件不能删除
            if 'contract_text_process_attachment_ids' == key:
                if self.contract_text_process_attachment_ids:
                    for contract_text_process_attachment_id in self.contract_text_process_attachment_ids:
                        if not contract_text_process_attachment_id.id in vals['contract_text_process_attachment_ids'][0][2]:
                            raise UserError(u'不能删除上传过的任何文档。')

            # 验证文本最终版的附件不能删除
            if 'contract_text_attachment_ids' == key:
                #验证商务角色
                groups_id = self.env.ref('ZCTA.ZCONTRACT_BUSINESS').id
                sql = 'SELECT * from res_groups_users_rel where gid=%s and uid=%s'
                self._cr.execute(sql, (groups_id, self._uid,))
                groups_users = self._cr.fetchone()
                if not groups_users:
                    raise UserError(u'仅商务可以更新最终版合同文本')

                if self.contract_text_attachment_ids:
                    for contract_text_attachment_id in self.contract_text_attachment_ids:
                        if not contract_text_attachment_id.id in \
                               vals['contract_text_attachment_ids'][0][2]:
                            raise UserError(u'不能删除上传过的任何文档。')


            if 'pdfswy_attachment_ids' != key and   'pdfqw_attachment_ids' != key and  \
                    'contract_text_attachment_ids' != key \
                    and 'x_studio_srqrlx' != key and 'signed_time' !=key  and 'contract_text_clean_attachment_ids' !=key  \
                    and 'contract_text_process_attachment_ids' !=key  \
                    and 'revision' != key :
                no_check=True
            elif  ('contract_text_attachment_ids' == key or
                   'pdfswy_attachment_ids' == key or
                   'pdfqw_attachment_ids' == key)  and int(self.stage_id)==6 :
                #上传签章完成的最终合同，并回写签订时间
                GetDatetime = get_zone_datetime.GetDatetime()
                signed_time = GetDatetime.get_datetime()
                #验证合同签订时间 ZCTA.ZCONTRACT_BUSINESS

                groups_id = self.env.ref('ZCTA.ZCONTRACT_BUSINESS').id
                sql = 'SELECT * from res_groups_users_rel where gid=%s and uid=%s'
                self._cr.execute(sql, (groups_id, self._uid,))
                groups_users = self._cr.fetchone()
                if not groups_users:
                    raise UserError(u'仅商务可以更新最终版合同文本与PDF文本')

                if not self.signed_time and not 'signed_time' in vals.keys():
                    raise UserError(u'请填写合同签订时间。')
                # 处理历史文本合同
                sql = 'select attachment_id from agreement_contract_text_ir_attachments_rel where id=%s'
                self._cr.execute(sql, (self.id,))
                iattachment_ids = self._cr.fetchall()
                attachment = self.env['ir.attachment']
                contract_text_attachment_ids=[]
                for contract_text_attachment_id in  vals['contract_text_attachment_ids'][0][2]:
                    is_add=True
                    for iattachment_id in iattachment_ids:
                        if iattachment_id[0]==contract_text_attachment_id:
                            is_add=False
                            attachment.browse(iattachment_id[0]).unlink()
                    if is_add:
                        contract_text_attachment_ids.append(contract_text_attachment_id)
                vals['contract_text_attachment_ids']=[[6, False, contract_text_attachment_ids]]

                sql = 'delete from agreement_contract_text_ir_attachments_rel where id=%s'
                self._cr.execute(sql, (self.id,))

            elif 'contract_text_clean_attachment_ids' == key and int(self.stage_id) == 4:
                # 上传清洁版合同文本，更新提醒销售输入预计签回时间
                is_email_sign_time=True
                sql = "UPDATE  agreement set is_email_sign_time=%s where id=%s"
                self._cr.execute(sql, ('f', self.id))

        if is_email_sign_time!=None:
            #vals['stage_id'] =5
            sql = "UPDATE  agreement set stage_id=%s where id=%s"
            self._cr.execute(sql, ('5', self.id))

        if signed_time != None:
            #vals['stage_id'] = 7
            sql = "UPDATE  agreement set stage_id=%s where id=%s"


            pdfswy = '（PDF首尾页）'
            pdfqw = '（PDF全文版）'
            fktj = '（付款条件）'
            htwb = '（合同文本）'
            if self.pdfswy_attachment_ids or  'pdfswy_attachment_ids' in  vals.keys():
                pdfswy = ""
            if self.pdfqw_attachment_ids or  'pdfqw_attachment_ids' in  vals.keys():
                pdfqw = ""
            if self.fktj_attachment_ids or  'fktj_attachment_ids' in  vals.keys():
                fktj = ""
            if self.contract_text_attachment_ids or 'contract_text_attachment_ids' in  vals.keys():
                htwb = ""
            if pdfswy != "" or pdfqw != "" or fktj != "" or htwb != "":
                raise UserError(u'双方签章阶段必须上传' + pdfswy + pdfqw + fktj + htwb)
            self._cr.execute(sql, ('7', self.id))
        if not flag_stage_id:
            raise UserError(u'合同阶段不能手工拖拽。')
            user_reviews = self.env['tier.review'].search([
                ('model', '=', 'agreement'),
                ('res_id', '=', self.id),
                ('status', '=', 'pending')
            ])

            if user_reviews:
                raise UserError(u'合同正在审批中。')
            else:
                user_reviews = self.env['tier.review'].search([
                    ('model', '=', 'agreement'),
                    ('res_id', '=', self.id),
                    ('status', '=', 'approved')
                ])
                if not user_reviews:
                    raise UserError(u'合同未完成审批。')

            if vals['stage_id'] == 6 and not self.plan_sign_time:
              raise UserError(u'客户签章阶段计划回签日期必须写入')

            if vals['stage_id'] == 7:
                pdfswy='（PDF首尾页）'
                pdfqw = '（PDF全文版）'
                fktj = '（付款条件）'
                htwb= '（合同文本）'
                if self.pdfswy_attachment_ids:
                    pdfswy = ""
                if self.pdfqw_attachment_ids:
                    pdfqw = ""
                if self.fktj_attachment_ids:
                    fktj = ""
                if self.contract_text_attachment_ids:
                    htwb = ""
                if pdfswy!="" or pdfqw!="" or fktj!="" or htwb!="":
                    raise UserError(u'双方签章阶段必须上传'+pdfswy+pdfqw+fktj+htwb)
            sql="UPDATE  agreement set stage_id=%s where id=%s"
            self._cr.execute(sql,(vals['stage_id'],self.id))
            return True

        if not flag_plan_sign_time:
            #判断不能小于当前时间
            if self._uid != self.create_uid.id and self._uid != self.assigned_user_id.id:
                raise UserError(u'仅销售可以更新,预计回签时间。')
            user_reviews = self.env['tier.review'].search([
                ('model', '=', 'agreement'),
                ('res_id', '=', self.id),
                ('status', '=', 'pending')
            ])
            if user_reviews:
                raise UserError(msg)
            else:
                user_reviews = self.env['tier.review'].search([
                    ('model', '=', 'agreement'),
                    ('res_id', '=', self.id),
                    ('status', '=', 'approved')
                ])
                if not user_reviews:
                    raise UserError(msg)

            sql = "UPDATE  agreement set plan_sign_time=%s,stage_id=6 where id=%s"
            if vals['plan_sign_time']:
                plan_sign_time=vals['plan_sign_time']
            else:
                plan_sign_time=None
            self._cr.execute(sql, (plan_sign_time, self.id))
            return True
        if not flag_message_main_attachment_id:
            sql = "UPDATE  agreement set message_main_attachment_id=%s where id=%s"
            if vals['message_main_attachment_id']:
                message_main_attachment_id=vals['message_main_attachment_id']
            self._cr.execute(sql, (message_main_attachment_id, self.id))
            return True
        if not flag_signed_time:
            if not self.contract_text_attachment_ids:
                raise UserError(u'更新签订日期必须上传合同文本。')

            #更新签订日期
            sql = "UPDATE  agreement set signed_time=%s,stage_id=6 where id=%s"
            if vals['signed_time']:
                signed_time = vals['signed_time']
            else:
                signed_time = None
            self._cr.execute(sql, (signed_time, self.id))
            return True

        # if not flag_contract_text_attachment_ids:
        #     # 更新签订日期
        #     #sql = "UPDATE  agreement set signed_time=%s,stage_id=6 where id=%s"
        #     GetDatetime = get_zone_datetime.GetDatetime()
        #     vals['signed_time']=GetDatetime.get_datetime(),
        #     #self._cr.execute(sql, (GetDatetime.get_datetime(), self.id))
        if  no_check:
            # 判断 BO审阅 全程监管 角色仅在审核前可以审核当前数据
            groups_id = self.env.ref('ZCAT.ZCONTRACT_BO_CHECK_SUPERVISE').id
            sql = 'SELECT * from res_groups_users_rel where gid=%s and uid=%s'
            self._cr.execute(sql, (groups_id, self._uid,))
            groups_users = self._cr.fetchone()
            if self.can_review and groups_users:
                no_check = False
                #raise UserError(u'仅法务可以更新清洁版合同文本。')
            # if self.can_review and self.bo_review=='BO审阅-全程监管':
            #     no_check=False

        for rec in self:
            if (getattr(rec, self._state_field) in self._state_from and
                    vals.get(self._state_field) in self._state_to):
                if rec.need_validation:
                    # try to validate operation
                    reviews = rec.request_validation()
                    rec._validate_tier(reviews)
                    if not self._calc_reviews_validated(reviews):
                        raise ValidationError(_(
                            "This action needs to be validated for at least "
                            "one record. \nPlease request a validation."))
                if rec.review_ids and not rec.validated:
                    raise ValidationError(_(
                        "A validation process is still open for at least "
                        "one record."))
            if (rec.review_ids and getattr(rec, self._state_field) in
                    self._state_from and not vals.get(self._state_field) in
                    (self._state_to + [self._cancel_state]) and not
                    self._check_allow_write_under_validation(vals)) and no_check:
                raise ValidationError(msg)

        if vals.get(self._state_field) in self._state_from:
            self.mapped('review_ids').unlink()
        return super(TierValidation, self).write(vals)

    @api.multi
    def _compute_need_validation(self):
        for rec in self:
            tiers = self.env[
                'tier.definition'].search([('model', '=', self._name)])
            valid_tiers = any([rec.evaluate_tier(tier) for tier in tiers])
            rec.need_validation = not rec.review_ids and valid_tiers and \
                                  getattr(rec, self._state_field) in self._state_from

            if rec.need_validation:
               if self._uid != self.create_uid.id and  self._uid != self.assigned_user_id.id:
                 rec.need_validation = False
            # if self._uid != self.create_uid.id and self._uid != self.assigned_user_id.id:
            #      rec.is_creator=False





class TierReview(models.Model):
    _inherit = "tier.review"
    _description = "Tier Review"

    up_sequence = fields.Integer("up sequence")
    cp_sequence = fields.Integer("cp sequence")
    rebut = fields.Boolean("rebut")
    reject = fields.Boolean("reject")
    w_approver= fields.Char("W Approver")
    w_approver_id =fields.Many2one(
        comodel_name="res.users",
    )
    tier_stage_id = fields.Integer("stage")
    is_send_email=fields.Boolean("is_send_email")
    comment_temp = fields.Char('comment Temp')
    node_name= fields.Char('Node Name')