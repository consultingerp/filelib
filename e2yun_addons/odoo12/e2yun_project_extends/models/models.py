# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, exceptions
import logging
_logger = logging.getLogger(__name__)


import warnings

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
    # partner_questionnaire_classification = fields.Selection([('Internally', '对内'), ('Foreign', '对外')], string='问卷分类',
    #                                                 related='parent_id.questionnaire_classification')


    # 动态domain筛选模板
    # @api.depends('questionnaire_scenario', 'partner_questionnaire_classification')
    # @api.onchange('questionnaire_scenario', 'partner_questionnaire_classification')
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

    # @api.onchange('parent_id.multiple_questionnaires')
    # def _onchange_weight(self):
    #     code = self.parent_id.multiple_questionnaires
    #     if code == 'yes':


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

    # 非多问卷时只展示一行
    @api.onchange('questionnaire_ids')
    def _questionnaire_length_control(self):
        if self.multiple_questionnaires == 'no':
            if len(self.questionnaire_ids) > 1:
                raise exceptions.Warning(_("行数超过限制！"))
                # question_no1 = self.questionnaire_ids[0]
                # self.questionnaire_ids = question_no1

    @api.onchange('multiple_questionnaires')
    def _on_change_multiple_questionnaires(self):
        if self.multiple_questionnaires == 'no':
            if len(self.questionnaire_ids) > 1:
                a = self.questionnaire_ids
                question_no1 = self.questionnaire_ids[0]
                self.questionnaire_ids = question_no1

    @api.one
    def write(self, vals):
        res = super(E2yunTaskInfo, self).write(vals)
        if self.multiple_questionnaires == 'no' and len(self.questionnaire_ids) == 0:
            raise exceptions.Warning(_('请先维护行信息！'))
        if self.multiple_questionnaires and self.multiple_questionnaires == 'no':
            self.questionnaire_ids.weight = '100%'
        all_score = 0
        for record in self.questionnaire_ids:
            str_weight = record.weight
            if str_weight:
                int_weight = int(str_weight[:-1])
                all_score += int_weight
        if all_score > 100:
            # raise Warning(_('权重之和大于100%，请重新输入'))
            raise exceptions.Warning(_('权重之和大于100%，请重新输入'))
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

    # @api.model
    # def create(self, vals):
    #     res = super(E2yunTaskInfo, self).create(vals)
    #     if res.survey_temp_id:
    #         res.survey_id = res.survey_temp_id.copy().id
    #     return res



class E2yunProjectSurvey(models.Model):
    _inherit = 'survey.survey'

    # 自动带出问卷分类
    # @ap           i.onchange("questionnaire_classification")
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

    # @api.one
    # def write(self, vals):
    #     res = super(E2yunProjectSurvey, self).write(vals)
    #     return res

    # 权重百分比之和为100%，超出则弹框提醒
    @api.one
    def write(self, vals):
        res = super(E2yunProjectSurvey, self).write(vals)
        all_weight = 0
        for l in self.page_ids:
            if l.weight:
                i = l.weight[:-1]
                all_weight += int(i)
        if all_weight > 100:
            # warnings.warn('权重之和大于100%，请重新输入')
            # raise ValueError('权重之和大于100%，请重新输入')
            # raise Warning(_('权重之和大于100%，请重新输入'))
            raise exceptions.Warning(_('权重之和大于100%，请重新输入'))
        # self.copy()
        return res

    # def get_formview_id(self, access_uid=None):
    #     res = super(E2yunProjectSurvey,self).get_formview_id(access_uid)
    #     return res


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
    @api.onchange('question_ids')
    def _onchange_page_sum(self):
        res = self.question_ids
        if res:
            all_score = 0
            for i in res:
                all_score += int(i.highest_score)
            self.x_studio_survey_page_sum = all_score

class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    highest_score = fields.Float(string='最高分值')
    scoring_method = fields.Selection([('唯一性计分', '唯一性计分'),('选择性计分', '选择性计分'),('不计分', '不计分')],string='计分方式')
    reference_existing_question = fields.Many2one('survey.question', string='引用已有题库')
    # 题库页面创建并可以保存，继承并修改：required=False
    page_id = fields.Many2one('survey.page', string='Survey page',
                              ondelete='cascade', required=False, default=lambda self: self.env.context.get('page_id'))
    type_id = fields.Many2one('question.type', string='问题类型')
    type_name = fields.Char(string='问题类型', related='type_id.display_name_chs')

    @api.multi
    def validate_question(self, post, answer_tag):
        self.ensure_one()
        try:
            checker = getattr(self, 'validate_' + self.type_id.name)
        except AttributeError:
            _logger.warning(self.type + ": This type of question has no validation method")
            return {}
        else:
            return checker(post, answer_tag)

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
        self.type_id = self.reference_existing_question.type_id
        self.scoring_method = self.reference_existing_question.scoring_method
        self.labels_ids = self.reference_existing_question.labels_ids

    # 唯一性计分分值超出则弹框提醒；选择性计分只能有唯一答案，但每个选项都有分数，否则弹框提醒。
    @api.multi
    def write(self, vals):
        res = super(SurveyQuestion, self).write(vals)
        for item in self:
            if item.scoring_method == '唯一性计分':
                if item.labels_ids:
                    # count = 0
                    all = []
                    for l in item.labels_ids:
                        # count += 1
                        if l.quizz_mark > 0.0:
                            all.append(l.quizz_mark)
                    if len(all) >= 2:
                    # statistics = all.count(0.0)
                    # if count > 2 or count == 1 or statistics == 0:
                        raise exceptions.Warning(_('唯一性计分只能给一个选项赋值，其他为0，请重新输入'))
            elif item.scoring_method == '选择性计分':
                if item.labels_ids:
                    for l in item.labels_ids:
                        if l.quizz_mark == 0:
                            raise exceptions.Warning(_('选择性计分每个选项都有分值，请重新输入'))
        return res

    # ⑥创建问题保存时，系统校验 “题库大类”和“计分方式”是否选择，如果未选择，则弹出提示“计分方式未选择，请选择”；# 唯一性计分分值超出则弹框提醒；选择性计分只能有唯一答案，但每个选项都有分数，否则弹框提醒。
    @api.model
    def create(self, vals):
        res = super(SurveyQuestion, self).create(vals)
        if res.scoring_method == '唯一性计分':
            if res.labels_ids:
                # count = 0
                all = []
                for l in self.labels_ids:
                    if l.quizz_mark > 0.0:
                        all.append(l.quizz_mark)
                # statistics = all.count(0.0)
                # if count > 2 or count == 1 or statistics > 1 or statistics == 0:
                if len(all) >= 2:
                    raise exceptions.Warning(_('唯一性计分只能给一个选项赋值，其他为0，请重新输入'))
        elif res.scoring_method == '选择性计分':
            if res.labels_ids:
                for l in res.labels_ids:
                    if l.quizz_mark == 0:
                        raise exceptions.Warning(_('选择性计分每个选项都有分值，请重新输入'))
        if not res.question_bank_type or not res.scoring_method:
            raise exceptions.Warning(_('题库大类或计分方式未选择，请选择'))
        return res


class NewQuestionType(models.Model):
    _name = 'question.type'

    name = fields.Char(string='问题类型的名称')
    display_name_chs = fields.Char(string='问题类型中文名称')
    type_html = fields.Html(string='问题类型的样式')
    question_ids = fields.One2many('survey.question', 'type_id', string='问题')

    @api.multi
    def name_get(self):
        res = []
        for question_type in self:
            name = question_type.display_name_chs
            res.append((question_type.id, name))
        return res



