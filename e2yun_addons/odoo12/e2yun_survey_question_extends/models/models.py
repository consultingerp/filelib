# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import logging
import math
from numpy import nan as NaN
_logger = logging.getLogger(__name__)


class e2yun_survey_question_extends(models.Model):
    _inherit = 'survey.question'

    is_template_question = fields.Boolean(string='是否模板问题')

    highest_score = fields.Float(string='最高分值', compute='_compute_highest_score', default=0.0)
    scoring_method = fields.Selection([('唯一性计分', '唯一性计分'), ('选择性计分', '选择性计分'), ('不计分', '不计分')], string='计分方式', required=True)
    reference_existing_question = fields.Many2one('survey.question', string='引用已有题库')
    # 题库页面创建并可以保存，继承并修改：required=False
    page_id = fields.Many2one('survey.page', string='Survey page',
                              ondelete='cascade', required=False, default=lambda self: self.env.context.get('page_id'))
    # type_id = fields.Many2one('question.type', string='问题类型')
    # type_name = fields.Char(string='问题类型')
    question_bank_type = fields.Selection([('供应商基本信息', '供应商基本信息'), ('人口属性', '人口属性'), ('市场调研', '市场调研')
                                              , ('用户满意度', '用户满意度'), ('联系方式', '联系方式'), ('其他', '其他')], default='供应商基本信息', string='题库大类', required=True)
    type = fields.Selection([
        ('free_text', 'Multiple Lines Text Box'),
        ('textbox', 'Single Line Text Box'),
        ('numerical_box', 'Numerical Value'),
        ('date', 'Date'),
        ('simple_choice', 'Multiple choice: only one answer'),
        ('multiple_choice', 'Multiple choice: multiple answers allowed'),
        ('matrix', 'Matrix'),
        ('select_box', '下拉框'),
        ('scoring', '打分'),
        ('upload attachments', '附件上传'),
        ], required=False)


    @api.model
    def default_get(self, fields_list):
        res = super(e2yun_survey_question_extends, self).default_get(fields_list)
        is_template_question = self._context.get('is_template_question')
        if is_template_question:
            res.update({'is_template_question': True})
        else:
            res.update({'is_template_question': False})
        return res

    @api.multi
    def validate_question(self, post, answer_tag):
        self.ensure_one()
        try:
            # checker = getattr(self, 'validate_' + self.type_id.name)
            checker = getattr(self, 'validate_' + self.type)
        except AttributeError:
            _logger.warning(self.type + ": This type of question has no validation method")
            return {}
        else:
            return checker(post, answer_tag)

    def _compute_highest_score(self):
        for record in self:
            if len(record.labels_ids) > 0 and record.type in ['simple_choice', 'multiple_choice']:
                record_highest_score = 0.0
                for line in record.labels_ids:
                    if line.quizz_mark > record_highest_score:
                        record_highest_score = line.quizz_mark
                record.highest_score = record_highest_score

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
        # self.type_id = self.reference_existing_question.type_id
        self.type = self.reference_existing_question.type
        self.scoring_method = self.reference_existing_question.scoring_method
        self.labels_ids = self.reference_existing_question.labels_ids

    @api.onchange('labels_ids')
    def _onchange_labels_ids(self):
        if self.scoring_method == '唯一性计分':
            all = []
            for label in self.labels_ids:
                if label.quizz_mark > 0.0:
                    all.append(label.quizz_mark)
            if len(all) >= 2:
                # statistics = all.count(0.0)
                # if count > 2 or count == 1 or statistics == 0:
                raise exceptions.Warning(_('唯一性计分只能给一个选项赋值，其他为0，请重新输入'))


    # 唯一性计分分值超出则弹框提醒；选择性计分只能有唯一答案，但每个选项都有分数，否则弹框提醒。
    @api.multi
    def write(self, vals):
        # if 'type_id' in vals:
        #     type_id = vals.get('type_id')
        #     question_type_item = self.env['question.type'].browse(type_id)
        #     if question_type_item:
        #         question_type_name = question_type_item.name
        #         if question_type_name in ['file', 'pull_down', 'score']:
        #             question_type_name = 'free_text'
        #         vals['type'] = question_type_name
        # for item in self:
        #     if item.scoring_method == '唯一性计分':
        #         if item.labels_ids:
        #             # count = 0
        #             all = []
        #             for l in item.labels_ids:
        #                 # count += 1
        #                 if l.quizz_mark > 0.0:
        #                     all.append(l.quizz_mark)
        #             if len(all) >= 2:
        #                 # statistics = all.count(0.0)
        #                 # if count > 2 or count == 1 or statistics == 0:
        #                 raise exceptions.Warning(_('唯一性计分只能给一个选项赋值，其他为0，请重新输入'))
        #     elif item.scoring_method == '选择性计分':
        #         if item.labels_ids:
        #             for l in item.labels_ids:
        #                 if l.quizz_mark is False:
        #                     raise exceptions.Warning(_('选择性计分每个选项都有分值，请重新输入'))
        res = super(e2yun_survey_question_extends, self).write(vals)
        for question in self:
            if question.scoring_method == '唯一性计分':
                if question.labels_ids:
                    # count = 0
                    all = []
                    for l in question.labels_ids:
                        # count += 1
                        if l.quizz_mark > 0.0:
                            all.append(l.quizz_mark)
                    if len(all) >= 2:
                        # statistics = all.count(0.0)
                        # if count > 2 or count == 1 or statistics == 0:
                        raise exceptions.Warning(_('唯一性计分只能给一个选项赋值，其他为0，请重新输入'))
            elif question.scoring_method == '选择性计分':
                if question.labels_ids:
                    for l in question.labels_ids:
                        if l.quizz_mark is False:
                            raise exceptions.Warning(_('选择性计分每个选项都有分值，请重新输入'))

        return res

    # ⑥创建问题保存时，系统校验 “题库大类”和“计分方式”是否选择，如果未选择，则弹出提示“计分方式未选择，请选择”；# 唯一性计分分值超出则弹框提醒；选择性计分只能有唯一答案，但每个选项都有分数，否则弹框提醒。
    @api.model
    def create(self, vals):
        # if 'type_id' in vals:
        #     type_id = vals.get('type_id')
        #     question_type_item = self.env['question.type'].browse(type_id)
        #     if question_type_item:
        #         question_type_name = question_type_item.name
        #         if question_type_name in ['file', 'pull_down', 'score']:
        #             question_type_name = 'free_text'
        #         vals['type'] = question_type_name
        # if 'scoring_method' in vals and vals['scoring_method'] == '唯一性计分':
        #     if 'labels_ids' in vals:
        #         # count = 0
        #         all = []
        #         for l in vals['labels_ids']:
        #             if l[0] == 1 and l[2] is not False:
        #                 if 'quizz_mark' in l[2]:
        #                     if l[2]['quizz_mark'] > 0.0:
        #                         all.append(l.quizz_mark)
        #         # statistics = all.count(0.0)
        #         # if count > 2 or count == 1 or statistics > 1 or statistics == 0:
        #         if len(all) >= 2:
        #             raise exceptions.Warning(_('唯一性计分只能给一个选项赋值，其他为0，请重新输入'))
        # elif 'scoring_method' in vals and vals['scoring_method'] == '选择性计分':
        #     if 'labels_ids' in vals:
        #         for l in vals['labels_ids']:
        #             if l[0] == 1 and l[2] is not False:
        #                 if 'quizz_mark' in l[2] and l[2]['quizz_mark'] is False:
        #                     raise exceptions.Warning(_('选择性计分每个选项都有分值，请重新输入'))
        #                 elif 'quizz_mark' not in l[2]:
        #                     raise exceptions.Warning(_('选择性计分每个选项都有分值，请重新输入'))
        # if 'question_bank_type' not in vals or 'scoring_method' not in vals:
        #     raise exceptions.Warning(_('题库大类或计分方式未选择，请选择'))
        res = super(e2yun_survey_question_extends, self).create(vals)
        if res.scoring_method == '唯一性计分':
            if res.labels_ids:
                # count = 0
                all = []
                for l in res.labels_ids:
                    if l.quizz_mark > 0.0:
                        all.append(l.quizz_mark)
                # statistics = all.count(0.0)
                # if count > 2 or count == 1 or statistics > 1 or statistics == 0:
                if len(all) >= 2:
                    raise exceptions.Warning(_('唯一性计分只能给一个选项赋值，其他为0，请重新输入'))
        elif res.scoring_method == '选择性计分':
            if res.labels_ids:
                for l in res.labels_ids:
                    if l.quizz_mark is False:
                        raise exceptions.Warning(_('选择性计分每个选项都有分值，请重新输入'))
        if not res.question_bank_type or not res.scoring_method:
            raise exceptions.Warning(_('题库大类或计分方式未选择，请选择'))

        return res

