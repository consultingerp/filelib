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

    @api.onchange('weight')
    def _onchange_weight(self):
        if self.weight:
            self.weight = str(self.weight)+'%'
        else:
            self.weight = ''



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

    # 打开问卷页面的方法
    @api.multi
    def turn_page(self):
        self.ensure_one()
        # Get lead views
        form_view = self.env.ref('survey.survey_form')
        tree_view = self.env.ref('survey.survey_tree')
        kanban_view = self.env.ref('survey.survey_kanban')
        return {
            'name': 'Lead',
            'res_model': 'survey.survey',
            # 'domain': [('type', '=', 'lead')],
            # 'res_id': self.id,
            'view_id': False,
            'target': 'new',
            'views': [
                (form_view.id, 'form'),
                (tree_view.id, 'tree'),
                (kanban_view.id, 'kanban')
            ],
            'view_type': 'tree',
            'view_mode': 'tree,form,kanban',
            'type': 'ir.actions.act_window',
        }

    # @api.model
    # def create(self, vals):
    #     res = super(E2yunTaskInfo, self).create(vals)
    #     if res.survey_temp_id:
    #         res.survey_id = res.survey_temp_id.copy().id
    #     return res

    # @api.multi
    # def write(self, vals):
    #     res = super(E2yunTaskInfo, self).write(vals)
    #     for item in self:
    #         if not item.survey_id and item.survey_temp_id:
    #             item.survey_id = item.survey_temp_id.copy().id
    #     return res

class E2yunProjectSurvey(models.Model):
    _inherit = 'survey.survey'

    # @api.depends('task_ids')
    # def _compute_scenario(self):
    #     id = self.id
    #     scenarios = self.env['project.questionnaire'].search([('survey_temp_id', '=', id)])
    #     questionnaire_scenario = scenarios.questionnaire_scenario
    #     return questionnaire_scenario
    questionnaire_classification = fields.Char(string='问卷分类')
    questionnaire_scenario = fields.Char(string='问卷场景')
    # task_ids = fields.One2many('project.questionnaire', 'survey_temp_id', string='Child Questionnaires')
class SurveyPage(models.Model):
    _inherit = 'survey.page'

    weight = fields.Char(string='权重')
