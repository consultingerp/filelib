# -*- coding: utf-8 -*-
from _datetime import date, datetime
from odoo import api, fields, models, exceptions, tools


class CrmTeamExtend(models.Model):
    _inherit = 'crm.team'

    def write(self, vals):
        res = super(CrmTeamExtend, self).write(vals)
        team_target_year = self.env['team.target.year'].search([])
        for line in team_target_year:
            year = line.target_year
            total_target = line.invoiced_target_year

            target_detail = self.env['team.target.detail'].search([('current_team_id', '=', self.id),
                                                                   ('detail_year', '=', year)])
            invoiced_target = 0
            for target in target_detail:
                invoiced_target += target.team_target_monthly

            if invoiced_target > total_target:
                raise exceptions.Warning('%s年：设定目标不能超过年度目标' % year)
        return res

    team_target = fields.One2many(
        'team.target.year',
        'team_id',
        string='门店目标')

    invoiced_target_detail = fields.One2many(
        'team.target.detail',
        'current_team_id',
        string='目标明细')


class TeamTargetYear(models.Model):
    _name = 'team.target.year'
    _description = '门店年度目标'

    # @api.multi
    # def _compute_invoiced_year(self):
    #     invoice_data = self.env['account.invoice'].read_group([
    #         ('state', 'in', ['open', 'in_payment', 'paid']),
    #         ('team_id', 'in', self.ids),
    #         ('date', '<=', date.today()),
    #         ('date', '>=', date.today().replace(month=1, day=1)),
    #         ('type', 'in', ['out_invoice', 'out_refund']),
    #     ], ['amount_untaxed_signed', 'team_id'], ['team_id'])
    #     for datum in invoice_data:
    #         self.browse(datum['team_id'][0]).invoiced = datum['amount_untaxed_signed']

    # def _default_year(self):
    #     self.target_year = datetime.now().year
    #     return self.target_year

    team_id = fields.Many2one('crm.team', '门店', readonly=True)
    target_year = fields.Selection(
        [(num, str(num)) for num in range(datetime.now().year - 5, datetime.now().year + 30)],
        string='年份')
    invoiced_target_year = fields.Integer(string='年度目标')
    # invoiced_target_assigned = fields.Integer(string='已分配目标', readonly=True, )
    # invoiced_year = fields.Integer(
    #     compute='_compute_invoiced_year',
    #     string='已达成年目标', readonly=True
    # )


class TeamTargetDetail(models.Model):
    _name = 'team.target.detail'
    _description = '门店目标详情'

    @api.depends('current_team_id')
    @api.onchange('current_team_id')
    def _default_domain(self):
        member_ids = self.current_team_id.member_ids
        domain = [('id', 'in', member_ids._ids)]
        return {
            'domain': {'sales_member': domain}
                }

    current_team_id = fields.Many2one('crm.team', '门店', readonly=True)
    detail_year = fields.Selection([(num, str(num)) for num in range(datetime.now().year-5, datetime.now().year+20)],
                                   string='年份')
    target_month = fields.Selection(
        [('1', '一月'), ('2', '二月'), ('3', '三月'), ('4', '四月'), ('5', '五月'), ('6', '六月'), ('7', '七月'), ('8', '八月'),
         ('9', '九月'), ('10', '十月'), ('11', '十一月'), ('12', '十二月')], string='月份')
    team_target_monthly = fields.Integer('目标值')
    sales_member = fields.Many2one('res.users', string='导购')




