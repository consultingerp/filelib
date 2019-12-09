from datetime import date, datetime
from odoo import api, fields, models, exceptions, tools


class CrmTeamStore(models.Model):
    _inherit = 'crm.team'

    team_target_store = fields.One2many(
        'team.target.year.store',
        'team_id',
        string='门店目标')
    invoiced_target_detail_store = fields.One2many(
        'team.target.detail.store',
        'current_team_id',
        string='目标明细')


class TeamTargetYearStore(models.Model):
    _name = 'team.target.year.store'
    _description = '门店年度目标'

    # @api.depends('team_id')
    # @api.onchange('team_id')
    # def default_year(self):
    #     year = self.team_id.team_year
    #     for record in self:
    #         record.target_year = year

    team_id = fields.Many2one('crm.team', '门店', readonly=True)
    target_year = fields.Selection(
        [(num, str(num)) for num in range(datetime.now().year - 5, datetime.now().year + 30)],
        string='年份')
    invoiced_target_year = fields.Integer(string='年度目标', required=True)


class TeamTargetDetailStore(models.Model):
    _name = 'team.target.detail.store'
    _description = '门店目标详情'

    # @api.depends('current_team_id')
    # @api.onchange('current_team_id')
    # def _default_domain(self):
    #     member_ids = self.current_team_id.member_ids
    #     year = self.current_team_id.team_year
    #     for record in self:
    #         record.detail_year = year
    #     domain = [('id', 'in', member_ids._ids)]
    #     return {
    #         'domain': {'sales_member': domain},
    #             }

    current_team_id = fields.Many2one('crm.team', '门店', readonly=True)
    detail_year = fields.Selection([(num, str(num)) for num in range(datetime.now().year-5, datetime.now().year+20)],
                                   string='年份')
    target_month = fields.Selection(
        [('1', '一月'), ('2', '二月'), ('3', '三月'), ('4', '四月'), ('5', '五月'), ('6', '六月'), ('7', '七月'), ('8', '八月'),
         ('9', '九月'), ('10', '十月'), ('11', '十一月'), ('12', '十二月')], string='月份', required=True)
    team_target_monthly = fields.Integer('目标值', required=True)
    sales_member = fields.Many2one('res.users', string='导购', required=True)
