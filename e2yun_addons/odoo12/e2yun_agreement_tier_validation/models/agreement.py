# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from ast import literal_eval

class Agreement(models.Model):
    _name = "agreement"
    _inherit = ['agreement', 'tier.validation']
    _stage_id_from = ['1', '2', '3']
    _stage_id_to = ['4']

    rebut_tier = fields.Boolean()

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


        user_reviews.write({
            'status': 'pending',
            'done_by': '',
            'reviewed_date': fields.Datetime.now(),
        })
        for review in user_reviews:
            rec = self.env[review.model].browse(review.res_id)
            rec._notify_accepted_reviews()





class CommentWizard(models.TransientModel):
    _inherit = 'comment.wizard'
    _description = 'Comment Wizard'


    @api.multi
    def add_comment(self):
        self.ensure_one()
        rec = self.env[self.res_model].browse(self.res_id)
        user_reviews = self.env['tier.review'].search([
            ('model', '=', self.res_model),
            ('res_id', '=', self.res_id),
            ('definition_id', 'in', self.definition_ids.ids)
        ])
        for user_review in user_reviews:
            user_review.write({
                'comment': self.comment,
            })
        if self.validate_reject == 'validate':
            rec._validate_tier()
        if self.validate_reject == 'reject':
            rec._rejected_tier()

        if self.validate_reject == 'rebut':
            rec._rebut_tier()

        rec._update_counter()




class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"



    @api.multi
    def write(self, vals):
        flag=False
        for key in vals:
            if 'stage_id'!=key and 'revision'!=key:
                flag=True
        if not flag:
            sql="UPDATE  agreement set stage_id=%s where id=%s"
            self._cr.execute(sql,(vals['stage_id'],self.id))
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
                    self._check_allow_write_under_validation(vals)) and flag:
                raise ValidationError(_("The operation is under validation."))
        if vals.get(self._state_field) in self._state_from:
            self.mapped('review_ids').unlink()
        return super(TierValidation, self).write(vals)


