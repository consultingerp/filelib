# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions


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