# -*- coding: utf-8 -*-

import datetime
import logging
import re
import uuid
from collections import Counter, OrderedDict
from itertools import product
from werkzeug import urls

from odoo import api, fields, models, tools, SUPERUSER_ID, _, exceptions
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError, ValidationError
email_validator = re.compile(r"[^@]+@[^@]+\.[^@]+")
_logger = logging.getLogger(__name__)

class Task(models.Model):
    _inherit = 'project.task'

    @api.multi
    def action_send_survey(self):
        """ Open a window to compose an email, pre-filled with the survey message """
        # Ensure that this survey has at least one page with at least one question.
        # if not self.questionnaire_ids or not [page.question_ids for questionnaire in self.questionnaire_ids if page.question_ids]:
        #     raise UserError(_('You cannot send an invitation for a survey that has no questions.'))

        if self.stage_id.name != '评估准备':
            raise UserError(_("You cannot send invitations for closed surveys."))

        if self.questionnaire_ids:
            survey_ids = []
            if len(self.questionnaire_ids) == 1:
                template = self.env.ref('e2yun_task_mail_wizard_extends.email_template_survey_1', raise_if_not_found=False)
                for record in self.questionnaire_ids:
                    survey_ids.append(record.survey_temp_id.id)
                local_context = dict(
                    self.env.context,
                    default_model='project.task',
                    default_res_id=self.id,
                    default_survey_ids=survey_ids,
                    default_use_template=bool(template),
                    default_template_id=template and template.id or False,
                    default_composition_mode='comment',
                    notif_layout='mail.mail_notification_light',
                )
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'task.mail.compose.message',
                    'target': 'new',
                    'context': local_context,
                }
            if len(self.questionnaire_ids) == 2:
                templatee = self.env.ref('e2yun_task_mail_wizard_extends.email_template_survey_2', raise_if_not_found=False)
                for record in self.questionnaire_ids:
                    survey_ids.append(record.survey_temp_id.id)
                local_context = dict(
                self.env.context,
                default_model='project.task',
                default_res_id=self.id,
                default_survey_ids=survey_ids,
                default_use_template=bool(templatee),
                default_template_id=templatee and templatee.id or False,
                default_composition_mode='comment',
                notif_layout='mail.mail_notification_light',
            )
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'task.mail.compose.message',
                    'target': 'new',
                    'context': local_context,
                }
            if len(self.questionnaire_ids) == 3:
                templateee = self.env.ref('e2yun_task_mail_wizard_extends.email_template_survey_3', raise_if_not_found=False)
                for record in self.questionnaire_ids:
                    survey_ids.append(record.survey_temp_id.id)
                local_context = dict(
                    self.env.context,
                    default_model='project.task',
                    default_res_id=self.id,
                    default_survey_ids=survey_ids,
                    default_use_template=bool(templateee),
                    default_template_id=templateee and templateee.id or False,
                    default_composition_mode='comment',
                    notif_layout='mail.mail_notification_light',
                )
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'task.mail.compose.message',
                    'target': 'new',
                    'context': local_context,
                }
        else:
            raise exceptions.Warning(_('There is no questionnaire for the task!'))
