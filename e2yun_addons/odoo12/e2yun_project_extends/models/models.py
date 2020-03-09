# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, exceptions
import logging
_logger = logging.getLogger(__name__)



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

    # 动态domain筛选模板
    @api.depends('questionnaire_scenario', 'parent_id.questionnaire_classification')
    @api.onchange('questionnaire_scenario', 'parent_id.questionnaire_classification')
    def onchange_temp_id(self):
        code = self.questionnaire_scenario
        code1 = self.parent_id.questionnaire_classification
        domain = [('questionnaire_scenario', '=', code), ('questionnaire_classification', '=', code1)]
        return {
            'domain': {'survey_temp_id': domain}
        }

    @api.onchange('weight')
    def _onchange_weight(self):
        if self.weight:
            if '%' in self.weight:
                self.weight = str(self.weight)
            else:
                self.weight = str(self.weight)+'%'
        else:
            self.weight = ''

class E2yunTaskInfo(models.Model):
    _inherit = 'project.task'

    survey_id = fields.Many2one('survey.survey', string='问卷调查')
    # 新增任务模式字段
    task_mode = fields.Selection([('common mode', '普通模式'), ('questionnaire model', '调查问卷模式')], string='任务模式', required=True)
    # 问卷分类
    questionnaire_classification = fields.Selection([('Internally', '对内'), ('Foreign', '对外')], string='问卷分类')
    # 是否多问卷
    multiple_questionnaires = fields.Selection([('yes', '是'), ('no', '否')], string='是否多问卷')
    # 一对多连接列表对象
    questionnaire_ids = fields.One2many('project.questionnaire', 'parent_id', string='问卷')

    # 非多问卷时只展示一行
    @api.onchange('questionnaire_ids')
    def _questionnaire_length_control(self):
        if self.multiple_questionnaires == 'no':
            if len(self.questionnaire_ids) > 1:
                raise exceptions.Warning(_("行数超过限制！"))

    @api.onchange('multiple_questionnaires')
    def _on_change_multiple_questionnaires(self):
        if self.multiple_questionnaires == 'no':
            if len(self.questionnaire_ids) > 1:
                a = self.questionnaire_ids
                question_no1 = self.questionnaire_ids[0]
                self.questionnaire_ids = question_no1

    @api.model
    def create(self, vals):
        res = super(E2yunTaskInfo, self).create(vals)
        all = self.questionnaire_ids
        if all:
            for i in all:
                if self.questionnaire_classification != i.survey_temp_id.questionnaire_classification:
                    raise exceptions.Warning(_('问卷分类字段必须与明细行模板问卷的问卷分类保持一致，请重新选择问卷分类'))
        return res

    @api.one
    def write(self, vals):
        res = super(E2yunTaskInfo, self).write(vals)
        # if self.multiple_questionnaires == 'no' and len(self.questionnaire_ids) == 0:
        #     raise exceptions.Warning(_('请先维护行信息！'))
        if self.multiple_questionnaires and self.multiple_questionnaires == 'no':
            for questionnaire in self.questionnaire_ids:
                questionnaire.weight = '100%'
        all_score = 0
        for record in self.questionnaire_ids:
            str_weight = record.weight
            if str_weight:
                int_weight = int(str_weight[:-1])
                all_score += int_weight
        if all_score > 100:
            raise exceptions.Warning(_('权重之和大于100%，请重新输入'))
        all = self.questionnaire_ids
        if all:
            for i in all:
                if self.questionnaire_classification != i.survey_temp_id.questionnaire_classification:
                    raise exceptions.Warning(_('问卷分类字段必须与明细行模板问卷的问卷分类保持一致，请重新选择问卷分类'))
        return res

    # 任务页面打开问卷页面的方法
    @api.multi
    def turn_page(self):
        self.ensure_one()
        # Get lead views
        form_view = self.env.ref('survey.survey_form')
        tree_view = self.env.ref('survey.survey_tree')
        kanban_view = self.env.ref('survey.survey_kanban')
        return {
            'name': '新建问卷',
            'res_model': 'survey.survey',
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





