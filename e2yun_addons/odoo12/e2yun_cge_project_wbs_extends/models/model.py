# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class Project(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    account_analytic_task_id = fields.Many2one('account.analytic.tag', '分析帐号包')
