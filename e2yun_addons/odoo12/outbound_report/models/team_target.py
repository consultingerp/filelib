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

    team_id = fields.Many2one('crm.team', '门店')
    team_target_year_id = fields.Integer('team.target.year.id')
    shop_code = fields.Char('门店代码')
    target_year = fields.Selection(
        [(num, str(num)) for num in range(datetime.now().year - 5, datetime.now().year + 30)],
        string='年份')
    invoiced_target_year = fields.Integer(string='年度目标')


class TeamTargetDetailStore(models.Model):
    _name = 'team.target.detail.store'
    _description = '门店目标详情'

    current_team_id = fields.Many2one('crm.team', '门店')
    team_target_detail_id = fields.Integer('team.target.detail.id')
    shop_code = fields.Char('门店代码')
    detail_year = fields.Selection(
        [(num, str(num)) for num in range(datetime.now().year - 5, datetime.now().year + 20)],
        string='年份')
    target_month = fields.Selection(
        [('1', '一月'), ('2', '二月'), ('3', '三月'), ('4', '四月'), ('5', '五月'), ('6', '六月'), ('7', '七月'), ('8', '八月'),
         ('9', '九月'), ('10', '十月'), ('11', '十一月'), ('12', '十二月')], string='月份')
    team_target_monthly = fields.Integer('目标值')
    sales_member = fields.Many2one('res.users', string='导购')
