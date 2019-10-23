# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Questionnaire(models.Model):
    _name = 'project.questionnaire'

    # 问卷场景
    questionnaire_scenario = fields.Selection(
        [('评分问卷', '评分问卷'), ('资质调查', '资质调查'), ('满意度调查', '满意度调查'),
         ('报名登记表', '报名登记表'), ('其他', '其他')], string='问卷场景')
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

    # 自动带出问卷分类
    def default_classification(self):
        ctx = self.env.context
        res_model = ctx['active_model']
        task_id = ctx['active_id']
        res_record = self.env[res_model].search([('id', '=', task_id)])
        questionnaire_classification = res_record.questionnaire_classification
        if questionnaire_classification == 'Internally':
            res = '对内测评（公司商务）'
            return res
        else:
            res = '对外测评（供应商）'
            return res

    # 自动带出问卷场景字段值
    def default_scenario(self):
        ctx = self.env.context
        res_model = ctx['active_model']
        task_id = ctx['active_id']
        res_record = self.env[res_model].search([('id', '=', task_id)])
        questionnaire = res_record['questionnaire_ids']
        res = ''
        for i in questionnaire:
            res = i.questionnaire_scenario
        return res

    questionnaire_classification = fields.Char(string='问卷分类', default=default_classification)
    questionnaire_scenario = fields.Char(string='问卷场景', default=default_scenario)



    # 权重百分比之和为100%，超出则弹框提醒
    @api.one
    def write(self, vals):

        res = super(E2yunProjectSurvey, self).write(vals)
        return res
    # task_ids = fields.One2many('project.questionnaire', 'survey_temp_id', string='Child Questionnaires')



class SurveyPage(models.Model):
    _inherit = 'survey.page'

    # 调查问卷page页面添加’权重‘字段
    weight = fields.Char(string='权重')

    # 权重百分比
    @api.onchange('weight')
    def _onchange_weight(self):
        if self.weight:
            self.weight = str(self.weight) + '%'
        else:
            self.weight = ''


    # @api.multi
    # def page_weight(self):
    #     weight_top = 100
    #     weight = 0
    #     for i in self:
    #         weight = weight+self.weight
    #     if weight > 100:
    #         raise Warning(_("Do not have access, skip this data for user's digest email"))

