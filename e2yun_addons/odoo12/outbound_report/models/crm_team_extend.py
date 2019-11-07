# -*- coding: utf-8 -*-
from _datetime import date
from odoo import api, fields, models, exceptions, tools


class CrmTeamExtend(models.Model):
    _inherit = 'crm.team'

    invoiced_target_month = fields.One2many(
        'team.target',
        'team_target_monthly',
        string='月度目标')

    invoiced_year = fields.Integer(
        compute='_compute_invoiced_year',
        string='已达成年目标', readonly=True
    )

    invoiced_target_year = fields.Integer(string='年度目标')

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


class TeamTarget(models.Model):
    _name = 'team.target'
    _description = '门店目标'

    @api.model
    def default_get(self, fields_list):
        res = super(TeamTarget, self).default_get(fields_list)
        res.update({'team_id': self.env.context.get('team_id')})
        return res

    # current_shop_id = fields.Integer('门店id')
    team_target_monthly = fields.Integer('目标值')
    target_date = fields.Selection([('1', '一月'), ('2', '二月'), ('3', '三月'), ('4', '四月'), ('5', '五月'), ('6', '六月'), ('7', '七月'), ('8', '八月'), ('9', '九月'), ('10', '十月'), ('11', '十一月'), ('12', '十二月')], string='月份')
    sales_member = fields.Many2one('res.users', string='导购')




