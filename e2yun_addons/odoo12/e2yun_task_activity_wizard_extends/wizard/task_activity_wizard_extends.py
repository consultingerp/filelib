# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import logging
import pytz
import uuid
from odoo.exceptions import UserError

from odoo import api, exceptions, fields, models, _

from odoo.tools import pycompat
from odoo.tools.misc import clean_context

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.model
    def _default_users(self):
        ctx = self.env.context.copy()
        survey_status = self.env['project.task'].browse(ctx['default_res_id'])
        res = survey_status.partner_ids
        ids = []
        for partner in res:
            ids.append(partner.user_ids.ids[0])
        return ids

    user_ids = fields.Many2many('res.users', string="Users", index=True, required=True, default=_default_users)
    # partner_ids = fields.Many2many('res.partner', string='Existing contacts', required=True, domain="[('user_ids.share', '=', False)]")

    # @api.onchange('partner_ids')
    # def _compute_users(self):
    #     for wizard in self:
    #         partner_ids = wizard.partner_ids
    #         wizard.user_ids = partner_ids.user_ids
    #         return False
    @api.model
    def create(self, values):
        # already compute default values to be sure those are computed using the current user
        # res = super(MailActivity,self).create(values)
        ctx = self.env.context.copy()
        task_record = self.env['project.task'].browse(ctx['default_res_id'])

        def create_token(wizard, partner_id, email,survey_id):
            SurveyUserInput = self.env['survey.user_input']
            token = pycompat.text_type(uuid.uuid4())
            # create response with token
            # deadline = wizard['date_deadline']
            # dt_now = datetime.today().date()
            # if dt_now > deadline:
            #     raise UserError(_("Please do not enter the invitation date before today!"))
            survey_user_input = SurveyUserInput.create({
                'survey_id': survey_id,
                'new_deadline': wizard['date_deadline'],
                'deadline': wizard['date_deadline'],
                'date_create': fields.Datetime.now(),
                'type': 'link',
                'state': 'new',
                'token': token,
                'partner_id': partner_id,
                'email': email})
            return survey_user_input.token

        res = False
        if values['user_ids']:
            for user_id in values['user_ids'][0][2]:
                newvalues = values.copy()
                newvalues['user_ids'] = False
                newvalues['user_id'] = user_id

                user = self.env['res.users'].sudo().search([('id', '=', user_id)])
                email = user.email
                if task_record.questionnaire_ids:
                    note_a = ""
                    for survey_id in task_record.questionnaire_ids:
                        survey = survey_id.survey_temp_id
                        title = survey.title
                        url = survey.public_url
                        token = create_token(newvalues, user.partner_id.id, email, survey.id)
                        if token:
                            url = url + '/' + token
                        note_a = note_a + """<a href='""" + url + """' target="_blank" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">""" + title + """</a>"""
                    note = """
                                                <div style="margin: 0px; padding: 0px; font-size: 13px;">
                                                    <p style="margin: 0px; padding: 0px; font-size: 13px;">
                                                        您好<br /><br />
                                                        我们正在进行调查，您的回复将不胜感激。
                                                        <div style="margin: 16px 0px 16px 0px;">
                                                            """ + note_a + """
                                                        </div>
                                                        谢您的参与！
                                                    </p>
                                                </div>
                                           """
                    newvalues['note'] = note

                res = super(MailActivity,self).create(newvalues)
        return res


    # @api.multi
    # def action_close_dialog(self):
    #     ctx = self.env.context.copy()
    #     task_record = self.env['project.task'].browse(ctx['default_res_id'])
    #
    #
        # def create_token(wizard, partner_id, email,survey_id):
        #     SurveyUserInput = self.env['survey.user_input']
        #     token = pycompat.text_type(uuid.uuid4())
        #     # create response with token
        #     deadline = wizard.date_deadline
        #     dt_now = datetime.today().date()
        #     if dt_now > deadline:
        #         raise UserError(_("Please do not enter the invitation date before today!"))
        #     survey_user_input = SurveyUserInput.create({
        #         'survey_id': survey_id,
        #         'new_deadline': wizard.date_deadline,
        #         'deadline': wizard.date_deadline,
        #         'date_create': fields.Datetime.now(),
        #         'type': 'link',
        #         'state': 'new',
        #         'token': token,
        #         'partner_id': partner_id,
        #         'email': email})
        #     return survey_user_input.token
    #
    #     for wizard in self:
    #         for user_id in wizard.user_ids:
    #             email = user_id.email
    #             if task_record.questionnaire_ids:
    #                 note_a = ""
    #                 for survey_id in task_record.questionnaire_ids:
    #                     survey = survey_id.survey_temp_id
    #                     title = survey.title
    #                     url = survey.public_url
    #                     token = create_token(wizard, user_id.partner_id.id, email, survey.id)
    #                     if token:
    #                         url = url + '/' + token
    #                     note_a = note_a + """<a href='""" + url + """' style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">""" + title + """</a>"""
    #                 note = """
    #                             <div style="margin: 0px; padding: 0px; font-size: 13px;">
    #                                 <p style="margin: 0px; padding: 0px; font-size: 13px;">
    #                                     您好<br /><br />
    #                                     我们正在进行调查，您的回复将不胜感激。
    #                                     <div style="margin: 16px 0px 16px 0px;">
    #                                         """ + note_a + """
    #                                     </div>
    #                                     谢您的参与！
    #                                 </p>
    #                             </div>
    #                        """
    #                 wizard.note = note
    #
    #     return {'type': 'ir.actions.act_window_close'}

