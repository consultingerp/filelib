# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import datetime
try:
    from odoo.addons.e2yun_agreement_tier_validation.models import get_zone_datetime
except BaseException as b:
    print(b)
    pass
class Agreement(models.Model):
    _name = "agreement"
    _inherit = ['agreement', 'tier.validation']
    _stage_id_from = ['1', '2', '3']
    _stage_id_to = ['4']

    rebut_tier = fields.Boolean()

    can_review = fields.Boolean(compute="_compute_can_review")

    @api.multi
    def _compute_can_review(self):
        for rec in self:
            rec.can_review = self.env.user in rec.reviewer_ids

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
                            })

                    self._update_counter()
        self._notify_review_requested(created_trs)
        #self.emil_temp(self.id, partner_ids)
        return created_trs


    @api.multi
    def restart_validation(self):
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
        self.comment=check_advise_temp[0:3]+"..."
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
            sql = "UPDATE  agreement set stage_id=%s where id=%s"
            self._cr.execute(sql, (tier_stage_id, self.res_id))

        rec._update_counter()




class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    @api.multi
    def write(self, vals):
        flag_stage_id=False
        flag_plan_sign_time = False
        message_main_attachment_id=False
        for key in vals:
            if 'stage_id'!=key and 'revision'!=key:
                flag_stage_id=True
            if 'plan_sign_time'!=key and 'revision'!=key:
                flag_plan_sign_time=True
            if 'message_main_attachment_id' != key and 'revision' != key:
                message_main_attachment_id=True

        if not flag_stage_id:
            # if vals['stage_id'] == 6 and not self.plan_sign_time:
            #   raise UserError(u'客户签章阶段计划回签时间必须写入')
            user_reviews = self.env['tier.review'].search([
                ('model', '=', 'agreement'),
                ('res_id', '=', self.id),
                ('status', '=', 'pending')
            ])
            if user_reviews:
                raise UserError(u'该操作正在审批中。')

            if vals['stage_id'] == 7:
                pdfswy='（PDF首尾页）'
                pdfqw = '（PDF全文版）'
                fktj = '（付款条件）'
                if self.pdfswy:
                    pdfswy = ""
                if self.pdfqw:
                    pdfqw = ""
                if self.fktj:
                    fktj = ""
                if pdfswy!="" or pdfqw!="" or fktj!="":
                    raise UserError(u'执行阶段必须上传'+pdfswy+pdfqw+fktj)
            sql="UPDATE  agreement set stage_id=%s where id=%s"
            self._cr.execute(sql,(vals['stage_id'],self.id))
            return True
        if not flag_plan_sign_time:
            sql = "UPDATE  agreement set plan_sign_time=%s where id=%s"
            if vals['plan_sign_time']:
                plan_sign_time=vals['plan_sign_time']
            else:
                plan_sign_time=None
            self._cr.execute(sql, (plan_sign_time, self.id))
            return True

        if not message_main_attachment_id:
            sql = "UPDATE  agreement set message_main_attachment_id=%s where id=%s"
            if vals['message_main_attachment_id']:
                message_main_attachment_id=vals['message_main_attachment_id']
            self._cr.execute(sql, (message_main_attachment_id, self.id))
            return True
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
                    self._check_allow_write_under_validation(vals)):
                raise ValidationError(_("The operation is under validation."))

        if vals.get(self._state_field) in self._state_from:
            self.mapped('review_ids').unlink()
        return super(TierValidation, self).write(vals)


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