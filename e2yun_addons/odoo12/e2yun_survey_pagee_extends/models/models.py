# -*- coding: utf-8 -*-

from odoo import models, fields, api

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
    # 小计逻辑
    # @api.onchange('question_ids')
    # def _onchange_page_sum(self):
    #     res = self.question_ids
    #     if res:
    #         all_score = 0
    #         for i in res:
    #             all_score += int(i.highest_score)
    #         self.x_studio_survey_page_sum = all_score