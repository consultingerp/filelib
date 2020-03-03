# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions, tools, SUPERUSER_ID
from collections import Counter, OrderedDict
from itertools import product

import datetime
import logging
import re
import uuid


from werkzeug import urls


from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError, ValidationError
email_validator = re.compile(r"[^@]+@[^@]+\.[^@]+")
_logger = logging.getLogger(__name__)



class E2yunProjectSurvey(models.Model):
    _inherit = 'survey.survey'

    questionnaire_classification = fields.Selection([('Internally', '对内'), ('Foreign', '对外')], string='问卷分类')
    questionnaire_scenario = fields.Selection([('评分问卷', '评分问卷'), ('资质调查', '资质调查'), ('满意度调查', '满意度调查'),
                                               ('报名登记表', '报名登记表'), ('其他', '其他')], string='问卷场景')

    @api.one
    def write(self, vals):
        res = super(E2yunProjectSurvey, self).write(vals)
        all_weight = 0
        for l in self.page_ids:
            if l.weight:
                i = l.weight[:-1]
                all_weight += int(i)
        if all_weight > 100:
            raise exceptions.Warning(_('权重之和大于100%，请重新输入'))
        return res

    @api.model
    def prepare_result(self, question, current_filters=None):
        """ Compute statistical data for questions by counting number of vote per choice on basis of filter """
        current_filters = current_filters if current_filters else []
        result_summary = {}

        # Calculate and return statistics for choice
        if question.type in ['simple_choice', 'multiple_choice']:
            comments = []
            answers = OrderedDict(
                (label.id, {'text': label.value, 'count': 0, 'answer_id': label.id}) for label in question.labels_ids)
            for input_line in question.user_input_line_ids:
                if not input_line.is_test_answer_line:
                    if input_line.answer_type == 'suggestion' and answers.get(input_line.value_suggested.id) and (
                            not (current_filters) or input_line.user_input_id.id in current_filters):
                        answers[input_line.value_suggested.id]['count'] += 1
                    if input_line.answer_type == 'text' and (
                            not (current_filters) or input_line.user_input_id.id in current_filters):
                        comments.append(input_line)
            result_summary = {'answers': list(answers.values()), 'comments': comments}

        # Calculate and return statistics for matrix
        if question.type == 'matrix':
            rows = OrderedDict()
            answers = OrderedDict()
            res = dict()
            comments = []
            [rows.update({label.id: label.value}) for label in question.labels_ids_2]
            [answers.update({label.id: label.value}) for label in question.labels_ids]
            for cell in product(rows, answers):
                res[cell] = 0
            for input_line in question.user_input_line_ids:
                if not input_line.is_test_answer_line:
                    if input_line.answer_type == 'suggestion' and (not (
                    current_filters) or input_line.user_input_id.id in current_filters) and input_line.value_suggested_row:
                        res[(input_line.value_suggested_row.id, input_line.value_suggested.id)] += 1
                    if input_line.answer_type == 'text' and (
                            not (current_filters) or input_line.user_input_id.id in current_filters):
                        comments.append(input_line)
            result_summary = {'answers': answers, 'rows': rows, 'result': res, 'comments': comments}

        # Calculate and return statistics for free_text, textbox, date
        if question.type in ['free_text', 'textbox', 'date']:
            result_summary = []
            for input_line in question.user_input_line_ids:
                if not input_line.is_test_answer_line:
                    if not (current_filters) or input_line.user_input_id.id in current_filters:
                        result_summary.append(input_line)

        # Calculate and return statistics for numerical_box
        if question.type == 'numerical_box':
            result_summary = {'input_lines': []}
            all_inputs = []
            for input_line in question.user_input_line_ids:
                if not input_line.is_test_answer_line:
                    if not (current_filters) or input_line.user_input_id.id in current_filters:
                        all_inputs.append(input_line.value_number)
                        result_summary['input_lines'].append(input_line)
            if all_inputs:
                result_summary.update({'average': round(sum(all_inputs) / len(all_inputs), 2),
                                       'max': round(max(all_inputs), 2),
                                       'min': round(min(all_inputs), 2),
                                       'sum': sum(all_inputs),
                                       'most_common': Counter(all_inputs).most_common(5)})
        return result_summary

    @api.model
    def get_input_summary(self, question, current_filters=None):
        """ Returns overall summary of question e.g. answered, skipped, total_inputs on basis of filter """
        current_filters = current_filters if current_filters else []
        result = {}
        if question.survey_id.user_input_ids:
            total_input_ids = current_filters or [input_id.id for input_id in question.survey_id.user_input_ids if
                                                  input_id.state != 'new' and input_id.is_test_answer is not True]
            result['total_inputs'] = len(total_input_ids)
            question_input_ids = []
            for user_input in question.user_input_line_ids:
                if not user_input.skipped and not user_input.is_test_answer_line:
                    question_input_ids.append(user_input.user_input_id.id)
            result['answered'] = len(set(question_input_ids) & set(total_input_ids))
            result['skipped'] = result['total_inputs'] - result['answered']
        return result

    @api.multi
    def action_send_survey(self):
        """ Open a window to compose an email, pre-filled with the survey message """
        # Ensure that this survey has at least one page with at least one question.
        if not self.page_ids or not [page.question_ids for page in self.page_ids if page.question_ids]:
            raise UserError(_('You cannot send an invitation for a survey that has no questions.'))

        if self.stage_id.closed:
            raise UserError(_("You cannot send invitations for closed surveys."))

        template = self.env.ref('e2yun_survey_eextends.email_template_survey_extends', raise_if_not_found=False)

        local_context = dict(
            self.env.context,
            default_model='survey.survey',
            default_res_id=self.id,
            default_survey_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            notif_layout='mail.mail_notification_light',
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'survey.mail.compose.message',
            'target': 'new',
            'context': local_context,
        }


class E2yunSurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    # user_input_id

    is_test_answer = fields.Boolean()

    @api.model
    def create(self, vals_list):
        # test_entry
        if vals_list.get('test_entry'):
            vals_list['is_test_answer'] = True
        res = super(E2yunSurveyUserInput, self).create(vals_list)
        return res

class E2yunSurveyUserInputLines(models.Model):
    _inherit = 'survey.user_input_line'

    is_test_answer_line = fields.Boolean(related='user_input_id.is_test_answer', store=True)
