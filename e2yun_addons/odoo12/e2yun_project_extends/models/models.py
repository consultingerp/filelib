# -*- coding: utf-8 -*-
from odoo import models, fields, api


class E2yunTaskInfo(models.Model):
    _inherit = 'project.task'

    survey_temp_id = fields.Many2one('survey.survey', string='问卷模版')
    survey_temp_idd = fields.Many2one('survey.survey', string='问卷模版')
    survey_temp_iddd = fields.Many2one('survey.survey', string='问卷模版')

    # survey_id = fields.Many2one('survey.survey', string='问卷调查')
    # 新增任务模式字段
    task_mode = fields.Selection([('common mode', '普通模式'), ('questionnaire model', '调查问卷模式')], string='任务模式')
    # 问卷分类
    questionnaire_classification = fields.Selection([('Internally', '对内'), ('Foreign', '对外')], string='问卷分类')
    # 是否多问卷
    multiple_questionnaires = fields.Selection([('yes', '是'), ('no', '否')], string='是否多问卷')
    # 问卷场景
    questionnaire_scenario = fields.Selection([('Score questionnaire', '评分问卷'), ('Qualification survey', '资质调查'), ('Satisfaction Survey', '满意度调查'), ('Registration Form', '报名登记表'), ('Other', '其他')], string='问卷场景')
    questionnaire_scenarioo = fields.Selection([('Score questionnaire', '评分问卷'), ('Qualification survey', '资质调查'), ('Satisfaction Survey', '满意度调查'), ('Registration Form', '报名登记表'), ('Other', '其他')], string='问卷场景')
    questionnaire_scenariooo = fields.Selection([('Score questionnaire', '评分问卷'), ('Qualification survey', '资质调查'), ('Satisfaction Survey', '满意度调查'), ('Registration Form', '报名登记表'), ('Other', '其他')], string='问卷场景')

    # 权重
    weight = fields.Char('权重')
    weightt = fields.Char('权重')
    weighttt = fields.Char('权重')
    # 问卷模板
    # questionnaire_template = fields.Many2one('survey.page', '问卷模板')

    @api.model
    def create(self, vals):
        res = super(E2yunTaskInfo, self).create(vals)
        if res.survey_temp_id:
            res.survey_id = res.survey_temp_id.copy().id
        return res

    @api.multi
    def write(self, vals):
        res = super(E2yunTaskInfo, self).write(vals)
        for item in self:
            if not item.survey_id and item.survey_temp_id:
                item.survey_id = item.survey_temp_id.copy().id
        return res
