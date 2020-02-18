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

    # 调查问卷page页面添加’权重‘字段
    weight = fields.Char(string='权重')
    # 小计
    x_studio_survey_page_sum = fields.Float(string='小计', compute='_compute_page_sum')

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