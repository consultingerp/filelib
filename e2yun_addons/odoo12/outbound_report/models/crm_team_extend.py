# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import api, fields, models, exceptions, tools


class CrmTeamExtend(models.Model):
    _inherit = 'crm.team'

    def write(self, vals):
        res = super(CrmTeamExtend, self).write(vals)
        # 验证目标设置逻辑
        if self.use_invoices and not self.team_year:
            raise exceptions.Warning('请选择年份')
        if self.team_year and not self.team_target:
            raise exceptions.Warning('请填写门店目标')
        if self.team_year and not self.invoiced_target_detail:
            raise exceptions.Warning('请填写目标明细')
        team_target_year = self.env['team.target.year'].search([('team_id', '=', self.id)])
        target_year_list = []
        for line in team_target_year:
            year = line.target_year
            if year in target_year_list:
                raise exceptions.Warning('%s年的年度目标已存在' % year)
            target_year_list.append(year)
            total_target = line.invoiced_target_year
            target_detail = self.env['team.target.detail'].search([('current_team_id', '=', self.id),
                                                                   ('detail_year', '=', year)])
            invoiced_target = 0
            month_sale_dict = {}
            for target in target_detail:
                month = target.target_month
                sale = target.sales_member.name
                if month in month_sale_dict.keys() and month_sale_dict['%s' % month] == sale:
                    raise exceptions.Warning('%s月份导购%s的目标值已存在' % (month, sale))
                month_sale_dict.update({month: sale})
                invoiced_target += target.team_target_monthly
            if invoiced_target > total_target:
                raise exceptions.Warning('%s年：设定目标不能超过年度目标' % year)
        target_detail_all = self.env['team.target.detail'].search([('current_team_id', '=', self.id)])
        detail_year_list = []
        for detail in target_detail_all:
            detail_year = detail.detail_year
            if detail_year not in target_year_list:
                raise exceptions.Warning('请先设置%s年的年度目标' % detail_year)
            if detail_year not in detail_year_list:
                detail_year_list.append(detail_year)
        for r in target_year_list:
            if r not in detail_year_list:
                raise exceptions.Warning('请设置%s年的目标明细' % r)

        # # 数据拷贝到相应的store模型中
        # val = vals.copy()
        # if 'team_target' in val:
        #     val['team_target_store'] = val['team_target']
        # if 'invoiced_target_detail' in val:
        #     val['invoiced_target_detail_store'] = val['invoiced_target_detail']
        return res

    # @api.depends('team_year')
    # @api.onchange('team_year')
    # def _onchange_team_year(self):
    #     team_year = self.team_year
    #     team_id = self.alias_parent_thread_id
    #     y_sql_str = "select target_year, invoiced_target_year from team_target_year y where y.target_year = %s and y.team_id = %s" \
    #                 % (team_year, team_id)
    #     d_sql_str = "select detail_year, target_month, sales_member, team_target_monthly from team_target_detail d where d.detail_year = " \
    #                 "%s and d.current_team_id = %s" % (team_year, team_id)
    #     self._cr.execute(y_sql_str)
    #     res_y = self._cr.dictfetchall()
    #     self._cr.execute(d_sql_str)
    #     res_d = self._cr.dictfetchall()
    #     all_value = {
    #         'ues_invoices': True,
    #         'team_year': team_year,
    #         'team_target': [],
    #         'invoiced_target_detail': []
    #     }
    #     if res_y:
    #         all_value.update({'team_target': res_y})
    #     if res_d:
    #         all_value.update({'invoiced_target_detail': res_d})
    #     return {'value': all_value}
    #
    # @api.depends('use_invoices')
    # @api.onchange('use_invoices')
    # def onchange_team_year(self):
    #     if self.use_invoices:
    #         self.team_year = datetime.now().year
    #
    # @api.model
    # def _default_year(self):
    #     return datetime.now().year

    team_year = fields.Selection([(num, str(num)) for num in range(datetime.now().year - 5, datetime.now().year + 30)],
                                 string='年份')

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

    @api.depends('team_id')
    @api.onchange('team_id')
    def default_year(self):
        year = self.team_id.team_year
        for record in self:
            record.target_year = year

    team_id = fields.Many2one('crm.team', '门店', readonly=True)
    target_year = fields.Selection(
        [(num, str(num)) for num in range(datetime.now().year - 5, datetime.now().year + 30)],
        string='年份')
    invoiced_target_year = fields.Integer(string='年度目标', required=True)


class SalesNameSearch(models.Model):
    _inherit = 'res.users'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super(SalesNameSearch, self).name_search(name, args, operator, limit)
        return res


class TeamTargetDetail(models.Model):
    _name = 'team.target.detail'
    _description = '门店目标详情'

    @api.depends('current_team_id')
    @api.onchange('current_team_id')
    def _default_domain(self):
        member_ids = self.current_team_id.member_ids
        year = self.current_team_id.team_year
        for record in self:
            record.detail_year = year
        domain = [('id', 'in', member_ids._ids)]
        return {
            'domain': {'sales_member': domain},
                }

    current_team_id = fields.Many2one('crm.team', '门店', readonly=True)
    detail_year = fields.Selection([(num, str(num)) for num in range(datetime.now().year-5, datetime.now().year+20)],
                                   string='年份')
    target_month = fields.Selection(
        [('1', '一月'), ('2', '二月'), ('3', '三月'), ('4', '四月'), ('5', '五月'), ('6', '六月'), ('7', '七月'), ('8', '八月'),
         ('9', '九月'), ('10', '十月'), ('11', '十一月'), ('12', '十二月')], string='月份', required=True)
    team_target_monthly = fields.Integer('目标值', required=True)
    sales_member = fields.Many2one('res.users', string='导购', required=True)




