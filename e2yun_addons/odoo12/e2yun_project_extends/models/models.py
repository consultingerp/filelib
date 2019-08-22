# -*- coding: utf-8 -*-
from odoo import models, fields, api


class E2yunTaskInfo(models.Model):
    _inherit = 'project.task'

    survey_temp_id = fields.Many2one('survey.survey', string='问卷调查模版')
    survey_id = fields.Many2one('survey.survey', string='问卷调查')

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
