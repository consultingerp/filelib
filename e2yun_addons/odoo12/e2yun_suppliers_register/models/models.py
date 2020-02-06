# -*- coding: utf-8 -*-

from odoo import models, fields, api

class e2yun_suppliers_register(models.Model):
    _inherit = 'survey.survey'

    lock_survey = fields.Boolean(string='问卷锁定', default=False)

class e2yun_suppliers_register_lock_survey(models.TransientModel):
    _inherit = 'survey.mail.compose.message'

    @api.multi
    def send_mail_action(self):
        ctx = self.env.context.copy()
        survey_status = self.env['survey.survey'].browse(ctx['default_survey_id'])
        survey_status.write({'lock_survey': True})
        return super(e2yun_suppliers_register_lock_survey, self).send_mail_action()