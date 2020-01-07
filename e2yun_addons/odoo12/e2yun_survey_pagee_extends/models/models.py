# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SurveyPage(models.Model):
    _inherit = 'survey.page'

    # 调查问卷page页面添加’权重‘字段
    weight = fields.Char(string='权重')
    # 小计
    x_studio_survey_page_sum = fields.Integer(string='小计')
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