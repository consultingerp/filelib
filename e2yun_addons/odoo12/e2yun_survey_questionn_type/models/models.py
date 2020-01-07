# -*- coding: utf-8 -*-

from odoo import models, fields, api

class NewQuestionType(models.Model):
    _name = 'question.type'

    name = fields.Char(string='问题类型的名称', required=True)
    display_name_chs = fields.Char(string='问题类型中文名称', required=True)
    type_html = fields.Html(string='问题类型的样式')
    question_ids = fields.One2many('survey.question', 'type_id', string='问题')

    # @api.multi
    # def name_get(self):
    #     res = []
    #     for question_type in self:
    #         name = question_type.display_name_chs
    #         res.append((question_type.id, name))
    #     return res