# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


# 该模型用于在问卷page页面，通过问题模板往问卷page中添加问题
class AddQuestionFromTemplate(models.TransientModel):
    _name = 'survey.add.question.from.template'
    _description = '从模板添加问题'

    template_question = fields.Many2one('survey.question', string='模板问题')

    def copy_and_save_template_question(self):
        if not self.template_question:
            raise Warning(_("请选择模板问题！"))
        current_page_id = self._context.get('current_page_id')
        current_page = self.env['survey.page'].browse(current_page_id)
        current_question_ids = current_page.question_ids.ids

        question_after_copy = self.template_question.copy()
        question_after_copy.is_template_question = False
        current_question_ids.append(question_after_copy.id)

        current_page.update({'question_ids': current_question_ids})
        return 1


class SurveyPage(models.Model):
    _inherit = 'survey.page'

    chose_from_template_question = fields.Many2one('survey.question', string='从模板问题中选择')
    # 调查问卷page页面添加’权重‘字段
    weight = fields.Char(string='权重')
    # 小计
    x_studio_survey_page_sum = fields.Float(string='小计', compute='_compute_page_sum')
    survey_id = fields.Many2one(required=False)

    @api.onchange('chose_from_template_question')
    def onchange_chose_question_from_template(self):
        pass
        """
        留个念想：
        该功能是在survey.page页面，添加模板问题选择功能
        初定实现形式是，选择
        尝试过以下几种办法，钧存在问题
        """
        # 以下思路三：
        # if not self.chose_from_template_question:
        #     pass
        # else:
        #     values = {'is_template_question': False}
        #     current_question = self.chose_from_template_question
        #     # 表头
        #     if current_question.question:
        #         values['question'] = current_question.question
        #     if current_question.question_bank_type:
        #         values['question_bank_type'] = current_question.question_bank_type
        #     if current_question.type:
        #         values['type'] = current_question.type
        #     # 选项 选项卡
        #     if current_question.constr_mandatory:
        #         values['constr_mandatory'] = current_question.constr_mandatory
        #     else:
        #         values['constr_mandatory'] = False
        #     # 答案选项卡
        #     label_ids_values = []
        #     label_ids_2_values = []
        #
        #     labels_id_copy_ids = []
        #     labels_2_id_copy_ids = []
        #     if current_question.scoring_method:
        #         values['scoring_method'] = current_question.scoring_method
        #     if current_question.labels_ids:
        #         for label in current_question.labels_ids:
        #             new_label = label.copy()
        #             labels_id_copy_ids.append(new_label.id)
        #             # label_values = {'value': label.value, 'quizz_mark': label.quizz_mark}
        #             # label_col = (0, 0, label_values)
        #             # label_ids_values.append(label_col)
        #         # values['labels_ids'] = label_ids_values
        #         values['labels_ids'] = [(6, 0, labels_id_copy_ids)]
        #     if current_question.labels_ids_2:
        #         for label2 in current_question.labels_ids_2:
        #             new_label2 = label2.copy()
        #             labels_2_id_copy_ids.append(new_label2.id)
        #         values['labels_ids_2'] = [(6, 0, labels_2_id_copy_ids)]
        #
        #         #     label2_values = {'value': label2.value}
        #         #     label2_col = (0, 0, label2_values)
        #         #     label_ids_2_values.append(label2_col)
        #         # values['labels_ids_2'] = label_ids_2_values
        #     self.update({
        #         'question_ids': [(0, 0, values)]
        #     })
        #     self.chose_from_template_question = False

            # 以下思路一：self.question_ids = current_questions 复制后取id写入当前list，直接替换  存在问题
            # current_question_ids = self.question_ids.ids
            # question_after_copy = self.chose_from_template_question.copy()
            # current_question_ids.append(question_after_copy.id)
            # current_questions = self.env['survey.question'].browse(current_question_ids)
            # self.question_ids = current_questions
            # self.chose_from_template_question = False

        # 以下思路二：self.update({'question_ids': [(4, question_after_copy.id)]}) 复制后取ID，用m2m的4,id进行写入  存在问题
        # current_question_ids = self.question_ids.ids
        # question_after_copy = self.chose_from_template_question.copy()
        # current_question_ids.append(question_after_copy.id)
        # current_questions = self.env['survey.question'].browse(current_question_ids)
        # self.update({'question_ids': [(4, question_after_copy.id)]})
        # self.chose_from_template_question = False

    @api.model
    def create(self, vals_list):
        res = super(SurveyPage, self).create(vals_list)
        return res

    @api.multi
    @api.depends('question_ids')
    def _compute_page_sum(self):
        for record in self:
            page_total_score = 0.0
            for question in record.question_ids:
                page_total_score = page_total_score + question.highest_score
            record.x_studio_survey_page_sum = page_total_score


    # 权重百分比
    @api.onchange('weight')
    def _onchange_weight(self):
        if self.weight:
            if '%' in self.weight:
                self.weight = str(self.weight)
            else:
                self.weight = str(self.weight) + '%'
        else:
            self.weight = ''

    def chose_question_from_template(self):
        # view = self.env.ref('merp_picking_wave.view_message_wizard')
        current_id = self.id
        new_context = self._context.copy()
        new_context['current_page_id'] = current_id

        return {
            'name': '从模板问题库中选择问题',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'survey.add.question.from.template',
            'context': new_context
        }

    def new_question(self):
        return {
            'name': '新建问题',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'survey.question'
        }
    # 小计逻辑
    # @api.onchange('question_ids')
    # def _onchange_page_sum(self):
    #     res = self.question_ids
    #     if res:
    #         all_score = 0
    #         for i in res:
    #             all_score += int(i.highest_score)
    #         self.x_studio_survey_page_sum = all_score