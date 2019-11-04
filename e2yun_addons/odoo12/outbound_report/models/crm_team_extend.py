# -*- coding: utf-8 -*-
from _datetime import date
from odoo import api, fields, models, exceptions, tools


class CrmTeamExtend(models.Model):
    _inherit = 'crm.team'

    invoiced_year = fields.Integer(
        compute='_compute_invoiced_year',
        string='已达成目标', readonly=True
    )
    invoiced_target_year = fields.One2many('annual.target', string='年度目标')

    @api.multi
    def _compute_invoiced_year(self):
        invoice_data = self.env['account.invoice'].read_group([
            ('state', 'in', ['open', 'in_payment', 'paid']),
            ('team_id', 'in', self.ids),
            ('date', '<=', date.today()),
            ('date', '>=', date.today().replace(month=1, day=1)),
            ('type', 'in', ['out_invoice', 'out_refund']),
        ], ['amount_untaxed_signed', 'team_id'], ['team_id'])
        for datum in invoice_data:
            self.browse(datum['team_id'][0]).invoiced = datum['amount_untaxed_signed']


class AnnualTarget(models.Model):
    _name = 'annual.target'

    target_count = fields.Char('月份')
    invoiced_target_year = fields.One2many('monthly.target', string='月度目标')


class MonthlyTarget(models.Model):
    _name = 'monthly.target'

    sales_member = fields.Char('导购')
    target_count = fields.Char('月份')
    target = fields.Integer('目标')
