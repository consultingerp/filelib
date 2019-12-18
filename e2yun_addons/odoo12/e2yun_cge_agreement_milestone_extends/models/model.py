# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AgreementMilestone(models.Model):
    _name = 'agreement.milestone'

    agreement_id = fields.Many2one('agreement', '合同编号')
    project_id = fields.Many2one('project.project', '合约编号')
    name = fields.Char("里程碑")
    milestone_date = fields.Datetime("里程碑时间")
    code = fields.Char('合同编号', related='agreement_id.code')
    plan_start_date = fields.Datetime("计划开始时间")
    plan_finish_date = fields.Datetime("计划完成时间")
    payment_rate = fields.Float("付款比例")
    payment_date = fields.Datetime("付款时间")
    payment_amount = fields.Float("付款金额", compute='_compute_payment_amount', store=True)

    @api.multi
    @api.depends('payment_rate', 'agreement_id.amount')
    def _compute_payment_amount(self):
        for item in self:
            item.payment_amount = item.agreement_id.amount * item.payment_rate / 100


class Project(models.Model):
    _name = 'agreement'
    _inherit = 'agreement'

    agreement_milestone = fields.One2many('agreement.milestone', 'agreement_id', string="里程碑")
    amount = fields.Float("合同金额")


class Project(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    agreement_milestone = fields.One2many('agreement.milestone', 'project_id', string="合同")


