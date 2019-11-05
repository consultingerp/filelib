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

    invoiced_target_year = fields.Integer(string='年度目标', related='invoiced_target_month.team_target_annual', readonly=True)

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
    _description = '门店年度目标'

    def default_shop(self):
        shop_code = self.env.context.get('shop_code').name
        return shop_code

    current_shop = fields.One2many('crm.team', string='当前门店', default=default_shop, readonly=True)
    target_date = fields.Char('月份')
    invoiced_target_month = fields.One2many('monthly.target', string='月度目标')


class TeamTarget(models.Model):
    _name = 'team.target'
    _description = '门店目标'

    def default_shop(self):
        shop_code = self.env.context.get('shop_code').name
        return shop_code

    def default_target_date(self):
        return date.today().month

    def _compute_sales_member(self):
        self.sales_member = self.env['crm.team'].search()

    current_shop = fields.Many2one('crm.team', string='当前门店', default=default_shop, readonly=True)
    sales_member = fields.Many2one(compute='_compute_sales_member', string='导购')
    target_date = fields.Selection([
        ('1', '一月'), ('2', '二月'), ('3', '三月'), ('4', '四月'), ('5', '五月'), ('6', '六月'),
        ('7', '七月'), ('8', '八月'), ('9', '九月'), ('10', '十月'), ('11', '十一月'), ('12', '十二月'),
    ], string='月份', default=default_target_date)
    target_for_person = fields.Integer('个人月目标')
    team_target_monthly = fields.Many2one('门店月目标', compute='_compute_team_target_monthly', readonly=True)
    team_target_annual = fields.Integer('门店年度目标', compute='_compute_team_target_annual', readonly=True)

    @api.multi
    def _compute_team_target_monthly(self):
        self.target_team_monthly = sum(self.env.context.get('target_for_person').groupby(self.env.context.get('target_date')))

    @api.multi
    def _compute_team_target_annual(self):
        self.target_team_annual = sum(self.env.context.get('team_target_monthly'))
