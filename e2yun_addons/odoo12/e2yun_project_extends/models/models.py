# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, exceptions
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
    # questionnaire_ids = fields.One2many('project.questionnaire', 'parent_id', string='Child Questionnaires')
    # temp_ids = fields.One2many('survey.survey', 'task_id', string='问卷模板')
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
                # raise Warning(_('权重之和大于100%，请重新输入'))
                raise exceptions.Warning(_('权重之和大于100%，请重新输入'))
        return res


    # 任务页面打开问卷页面的方法
    # @api.multi
    # def turn_page(self):
    #     self.ensure_one()
    #     # Get lead views
    #     form_view = self.env.ref('survey.survey_form')
    #     tree_view = self.env.ref('survey.survey_tree')
    #     kanban_view = self.env.ref('survey.survey_kanban')
    #     return {
    #         'name': '新建问卷',
    #         'res_model': 'survey.survey',
    #         # 'domain': [('type', '=', 'lead')],
    #         # 'res_id': self.id,
    #         'view_id': False,
    #         'target': 'new',
    #         'views': [
    #             (form_view.id, 'form'),
    #             (tree_view.id, 'tree'),
    #             (kanban_view.id, 'kanban')
    #         ],
    #         'view_type': 'tree',
    #         'view_mode': 'tree,form,kanban',
    #         'type': 'ir.actions.act_window',
    #     }

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
    # @api.onchange("questionnaire_classification")
    # def default_classification(self):
    #     ctx = self.env.context
        # try:
        #     res_model = ctx['active_model']
        #     questionnaire_id = ctx['active_id']
        #     res_record = self.env[res_model].search([('id', '=', questionnaire_id)])
        #     questionnaire_classification = res_record.parent_id.questionnaire_classification
        # if questionnaire_classification == 'Internally':
        #     res = '对内测评（公司商务）'
        #     return res
        # else:
        #     res = '对外测评（供应商）'
        #     return res
        # except:
        #     return ''
    # 自动带出问卷场景字段值
    # @api.onchange("field_domain", "default_value")
    # def default_scenario(self):
    #     ctx = self.env.context
    #     try:
    #         res_model = ctx['active_model']
    #         task_id = ctx['active_id']
    #         res_record = self.env[res_model].search([('id', '=', task_id)])
    #         scenario = res_record['questionnaire_scenario']
    #         return scenario
    #     except:
    #         return ''

    questionnaire_classification = fields.Selection([('Internally', '对内'), ('Foreign', '对外')], string='问卷分类')
    questionnaire_scenario = fields.Selection([('评分问卷', '评分问卷'), ('资质调查', '资质调查'), ('满意度调查', '满意度调查'),
         ('报名登记表', '报名登记表'), ('其他', '其他')], string='问卷场景')
    # questionnaire_id = fields.Many2one('project.questionnaire', 'survey_temp_id', string='')
    # task_id = fields.Many2one('project.task', related='questionnaire_id.', string='任务')

    # 权重百分比之和为100%，超出则弹框提醒
    @api.multi
    def write(self, vals):
        res = super(E2yunProjectSurvey, self).write(vals)
        for item in self:
            all_weight = 0
            for l in item.page_ids:
                if l.weight:
                    i = l.weight[:-1]
                    all_weight += int(i)
            if all_weight > 100:
                # warnings.warn('权重之和大于100%，请重新输入')
                # raise ValueError('权重之和大于100%，请重新输入')
                # raise Warning(_('权重之和大于100%，请重新输入'))
                raise exceptions.Warning(_('权重之和大于100%，请重新输入'))
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
    # 题库页面创建并可以保存，继承并修改：required=False
    page_id = fields.Many2one('survey.page', string='Survey page',
                              ondelete='cascade', required=False, default=lambda self: self.env.context.get('page_id'))
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

    # 唯一性计分分值超出则弹框提醒
    @api.multi
    def write(self, vals):
        res = super(SurveyQuestion, self).write(vals)
        for item in self:
            if item.scoring_method == '唯一性计分':
                if item.labels_ids:
                    count = 0
                    all = []
                    for l in item.labels_ids:
                        count += 1
                        all.append(l.quizz_mark)
                    statistics = all.count(0.0)
                    if count > 2 or count == 1 or statistics > 1 or statistics == 0:
                        raise exceptions.Warning(_('唯一性计分只能给一个选项赋值，其他为0，请重新输入'))
        return res

