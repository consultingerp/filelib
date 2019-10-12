# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Questionnaire(models.Model):
    _name = 'project.questionnaire'

    # 问卷场景
    questionnaire_scenario = fields.Selection(
        [('Score questionnaire', '评分问卷'), ('Qualification survey', '资质调查'), ('Satisfaction Survey', '满意度调查'),
         ('Registration Form', '报名登记表'), ('Other', '其他')], string='问卷场景')
    # 权重
    weight = fields.Char(string='权重')
    # 问卷模板
    survey_temp_id = fields.Many2one('survey.survey', string='问卷模版')
    parent_id = fields.Many2one('project.task', string='Parent Task')





class E2yunTaskInfo(models.Model):
    _inherit = 'project.task'

    survey_id = fields.Many2one('survey.survey', string='问卷调查')
    # 新增任务模式字段
    task_mode = fields.Selection([('common mode', '普通模式'), ('questionnaire model', '调查问卷模式')], string='任务模式')
    # 问卷分类
    questionnaire_classification = fields.Selection([('Internally', '对内'), ('Foreign', '对外')], string='问卷分类')
    # 是否多问卷
    multiple_questionnaires = fields.Selection([('yes', '是'), ('no', '否')], string='是否多问卷')
    # 一对多连接列表对象
    questionnaire_ids = fields.One2many('project.questionnaire', 'parent_id', string='Child Questionnaires')






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

# class E2yunProjectSurvey(models.Model):
#     _inherit = 'survey.survey'

    # def default_classification(self):
    #     # questionnaire_classification = self.env.context.get('questionnaire_classification')
    #     # tasks = self.env['project.task']
    #     # context = self.context_get()
    #     uid = self.env.context.get('uid')
    #     res = self.env['project.task'].search(['user_id', '=', uid])
    #     # questionnaire_classification = user.partner_id.questionnaire_classification
    #     # res = self.env.ref('project.view_task_form2')
    #     questionnaire_classification = res.questionnaire_classification
    #     return questionnaire_classification
    # @api.depends('')
    # def default_scenario(self):
    #     uid = self.env.context.get('uid')
    #     res = self.env['project.task'].search(['user_id', '=', uid])
    #     questionnaire_scenario = res.questionnaire_scenario
    #     return questionnaire_scenario


    # questionnaire_classification = fields.Char(string='问卷分类', readonly=True, required=True, default=default_classification)
    # # questionnaire_classification = fields.Selection([('Internally', '对内'), ('Foreign', '对外')], string='问卷分类', default='default_classification')
    #
    # questionnaire_scenario = fields.Char(string='问卷场景', readonly=True, required=True, default=default_scenario)
    # questionnaire_scenario = fields.Selection([('Score questionnaire', '评分问卷'), ('Qualification survey', '资质调查'), ('Satisfaction Survey', '满意度调查'), ('Registration Form', '报名登记表'), ('Other', '其他')], string='问卷场景')
    #


    # @api.depends('survey_temp_id')
    # def _compute_survey_classification(self):
    #     # questionnaire_scenario = self.env.ref['survey.survey_form'].questionnaire_scenario
    #     for survey in self:
    #         survey.questionnaire_classification = self.env.ref['e2yun_project_extends.view_task_form2_extends'].questionnaire_classification