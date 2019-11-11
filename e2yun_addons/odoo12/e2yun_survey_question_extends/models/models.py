# -*- coding: utf-8 -*-

from odoo import models, fields, api


class e2yun_survey_question_extends(models.Model):
    _inherit = 'survey.question'

    question_bank_type = fields.Selection([('供应商基本信息', '供应商基本信息'), ('人口属性', '人口属性'), ('市场调研', '市场调研')
                                              , ('用户满意度', '用户满意度'), ('联系方式', '联系方式'), ('其他', '其他')], string='题库大类')
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
        ])