# -*- coding: utf-8 -*-

from odoo import models, fields, api

class e2yun_survey_input_extends(models.Model):
    _inherit = "survey.user_input"

    new_deadline = fields.Date('截止日期', help="Date by which the person can open the survey and submit answers")