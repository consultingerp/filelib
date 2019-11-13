# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import warnings

class Questionnaire(models.Model):
    _name = 'project.questionnaire'

    # 如若是否多问卷字段选择否，则权重字段默认带出100%
    # @api.onchange("parent_id")
    # def onchange_weight(self):
    #     res = self.parent_id
        # ctx = self.env.context
        # id = ctx['params']['id']
        # record = self.env['project.task'].search([('id', '=', id)])
        # res = record.multiple_questionnaires
        # if res == 'no':
        #     self.weight = '100'
        # else:
        #     self.weight = ''


    # 问卷场景
    questionnaire_scenario = fields.Selection(
        [('评分问卷', '评分问卷'), ('资质调查', '资质调查'), ('满意度调查', '满意度调查'),
         ('报名登记表', '报名登记表'), ('其他', '其他')], string='问卷场景')
    # 权重
    # weight = fields.Char(string='权重', default=_default_weight)
    weight = fields.Char(string='权重')
    # 权重单位
    # weight_unit = fields.Char(string='权重单位', default='%')
    # 问卷模板
    survey_temp_id = fields.Many2one('survey.survey', string='问卷模版')
    parent_id = fields.Many2one('project.task', string='Parent Task')

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
    task_mode = fields.Selection([('common mode', '普通模式'), ('questionnaire model', '调查问卷模式')], string='任务模式')
    # 问卷分类
    questionnaire_classification = fields.Selection([('Internally', '对内'), ('Foreign', '对外')], string='问卷分类')
    # 是否多问卷
    multiple_questionnaires = fields.Selection([('yes', '是'), ('no', '否')], string='是否多问卷')
    # 一对多连接列表对象
    questionnaire_ids = fields.One2many('project.questionnaire', 'parent_id', string='Child Questionnaires')

    # @api.multi
    # def weight_write(self, vals):
    #     print("@@@@@@@@@@@@@@@@@@@@@")
    #     res = super(E2yunTaskInfo, self).write(vals)
    #     for item in self:
    #         all_score = 0
    #         for record in item.questionnaire_ids:
    #             str_weight = record.weight
    #             if str_weight:
    #                 int_weight = int(str_weight[:1])
    #                 all_score += int_weight
    #         if all_score > 100:
    #             raise Warning(_('权重之和大于100%，请重新输入'))
    #     return res

    @api.multi
    def write(self, vals):
        res = super(E2yunTaskInfo, self).write(vals)
        for item in self:
            if item.multiple_questionnaires and item.multiple_questionnaires == 'no':
                item.questionnaire_ids.weight = '100%'
            all_score = 0
            for record in item.questionnaire_ids:
                str_weight = record.weight
                if str_weight:
                    int_weight = int(str_weight[:-1])
                    all_score += int_weight
            if all_score > 100:
                raise Warning(_('权重之和大于100%，请重新输入'))
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

    # 权重百分比之和为100%，超出则弹框提醒
    # @api.one
    # def write(self, vals):
    #
    #     res = super(E2yunProjectSurvey, self).write(vals)
    #     return res
    #
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
        try:
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
        except:
            return ''
    # 自动带出问卷场景字段值
    def default_scenario(self):
        ctx = self.env.context
        try:
            res_model = ctx['active_model']
            task_id = ctx['active_id']
            res_record = self.env[res_model].search([('id', '=', task_id)])
            questionnaire = res_record['questionnaire_ids']
            res = ''
            for i in questionnaire:
                res = i.questionnaire_scenario
            return res
        except:
            return ''
    questionnaire_classification = fields.Char(string='问卷分类', default=default_classification)
    questionnaire_scenario = fields.Char(string='问卷场景', default=default_scenario)

    # 权重百分比之和为100%，超出则弹框提醒

    @api.multi
    def write(self, vals):
        res = super(E2yunProjectSurvey, self).write(vals)
        for item in self:
            all_weight = 0
            for l in item.page_ids:
                i = l.weight[:-1]
                all_weight += int(i)
            if all_weight > 100:
                # warnings.warn('权重之和大于100%，请重新输入')
                # raise ValueError('权重之和大于100%，请重新输入')
                raise Warning(_('权重之和大于100%，请重新输入'))
        return res



class SurveyPage(models.Model):
    _inherit = 'survey.page'

    # 调查问卷page页面添加’权重‘字段
    weight = fields.Char(string='权重')
    # 网页标题变更为段落
    # weight_unit = fields.Char(string='单位', default='%')
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

    # 权重百分比之和为100%，超出则弹框提醒
    # @api.onchange('weight')
    # def onchange_weightt(self):
    #     all_weight = 0
    #     res = self.weight
    #     # record = self.env['survey.page'].search([('weight', '=', res)])
    #     # id = record['survey_id'].id
    #     # records = self.env['survey.page'].search([('survey_id', '=', id)])
    #     ctx = self.env.context
    #     print(ctx, '*******************')
    #     record = self.env['survey.survey'].search([('id', '=', ctx['default_survey_id'])])
    #     print(record, '###########')
    #     records = record.page_ids
    #     print(records, '!!!!!!!!!!!!!1')
    #     for item in records:
    #         # i = item.weight[:-1]
    #         i = item.weight
    #         all_weight += int(i)
    #     if all_weight > 100:
    #         return {
    #             'warning': {
    #                 'title': _("检查到错误"),
    #                 'message': _(
    #                     "权重之和大于100%，请重新输入")
    #             }
    #         }
    #     return res


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    highest_score = fields.Float(string='最高分值')
    scoring_method = fields.Selection([('唯一性计分', '唯一性计分'),('选择性计分', '选择性计分'),('不计分', '不计分')],string='计分方式')
    reference_existing_question = fields.Many2one('survey.question', string='引用已有题库')

    @api.onchange('labels_ids')
    def _onchange_score(self):
        res = self.labels_ids
        if res:
            all_score = []
            for i in res:
                score = i.quizz_mark
                all_score.append(score)
            rr = max(all_score)
            self.highest_score = rr
        # else:
        #     return True
    @api.onchange('reference_existing_question')
    def reference(self):
        self.question = self.reference_existing_question.question
        self.question_bank_type = self.reference_existing_question.question_bank_type
        self.type = self.reference_existing_question.type
        self.scoring_method = self.reference_existing_question.scoring_method
        self.labels_ids = self.reference_existing_question.labels_ids



    # 打开题库页面的方法
    # @api.multi
    # def turn_question(self):
        # self.ensure_one()
        # # Get lead views
        # # form_view = self.env.ref('survey.survey_question_form')
        # tree_view = self.env.ref('survey.survey_question_tree')
        # # kanban_view = self.env.ref('survey.survey_kanban')
        # return {
        #     'name': '查看页面_已有题库',
        #     'res_model': 'survey.question',
        #     # 'domain': [('type', '=', 'lead')],
        #     # 'res_id': self.id,
        #     'view_id': False,
        #     'target': 'new',
        #     'views': [
        #         # (form_view.id, 'form'),
        #         (tree_view.id, 'tree'),
        #         # (kanban_view.id, 'kanban')
        #     ],
        #     'view_type': 'tree',
        #     'view_mode': 'tree,form,kanban',
        #     'type': 'ir.actions.act_window',
        # }
        # data = self.read()[0]
        # ctx = self._context.copy()
        # return {
        #     'name': '查看页面_已有题库',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'quoting.question.bank',
        #     'type': 'ir.actions.act_window',
        #     'context': ctx,
        #     'target': 'current',
        #     # 'action': 'survey.action_survey_question_form',
        # }

# class SurveyLabel(models.Model):
#     _inherit = 'survey.label'
#
#     score = fields.Integer(string='分值')

# class QuotingQuestionBank(models.Model):
#     _name = 'quoting.question.bank'
#     # 对应题库
#     question_bank_id = fields.Many2one('survey.question', string='选择已有题库')
    # 问题名称
    # question_name = fields.Char('问题名称', required=True, translate=True)
    # 题库大类
    # question_bank_type = fields.Selection([('供应商基本信息', '供应商基本信息'), ('人口属性', '人口属性'), ('市场调研', '市场调研')
    #                                           , ('用户满意度', '用户满意度'), ('联系方式', '联系方式'), ('其他', '其他')], string='题库大类')
    # 问题类型
    # type = fields.Selection([
    #     ('free_text', 'Multiple Lines Text Box'),
    #     ('textbox', 'Single Line Text Box'),
    #     ('numerical_box', 'Numerical Value'),
    #     ('date', 'Date'),
    #     ('simple_choice', 'Multiple choice: only one answer'),
    #     ('multiple_choice', 'Multiple choice: multiple answers allowed'),
    #     ('matrix', 'Matrix')], string='问题类型', default='free_text', required=True)
    # 计分方式
    # scoring_method = fields.Selection([('唯一性计分', '唯一性计分'), ('选择性计分', '选择性计分')], string='计分方式')
    # 可供选项
    # labels_ids = fields.One2many('survey.label', 'id', string='可供选项', oldname='answer_choice_ids', copy=True)
    # sequence = fields.Integer('Label Sequence order', default=10)