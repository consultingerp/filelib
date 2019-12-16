from datetime import datetime

from odoo import api, fields, models, exceptions, tools


class TargetCompletion(models.Model):
    _inherit = 'outbound.final'
    _description = '目标完成占比情况'

    @api.model
    def create(self, vals_list):
        # 创建新(计算字段)记录之前删除数据库中原有的数据
        final = self.env['outbound.final'].search(['|', ('jiesuan_amount', '!=', ''), ('target_amount', '!=', '')])
        if final:
            for rec in final:
                rec.unlink()
        res = super(TargetCompletion, self).create(vals_list)
        # 判断是查询目标完成占比报表,生成两条数据
        if 'target_year' in vals_list:
            new_val_list = []
            if res.jiesuan_amount:
                jiesuan_dict = vals_list.copy()
                jiesuan_dict.update({'completion': res.jiesuan_amount, 'sale_id': 1, 'target_id': 2})
                new_val_list.append(jiesuan_dict)
            if res.target_amount:
                target_dict = vals_list.copy()
                target_dict.update({'completion': res.target_amount, 'sale_id': 1, 'target_id': 1})
                new_val_list.append(target_dict)
            aa = super(TargetCompletion, self).create(new_val_list)
            if aa:
                kk = aa[0]
                res.unlink()
                return kk
        # 不是,直接返回
        else:
            return res

    def default_target_year(self):
        ctx = self._context.copy()
        if ctx.get('target_year', False):
            return ctx.get('target_year')

    def default_target_month(self):
        ctx = self._context.copy()
        if ctx.get('target_month', False):
            return ctx.get('target_month')

    target_year = fields.Selection([(num, str(num)) for num in range(datetime.now().year - 5, datetime.now().year + 30)],
                                    string='年份', default=default_target_year)
    target_month = fields.Selection(
        [('1', '一月'), ('2', '二月'), ('3', '三月'), ('4', '四月'), ('5', '五月'), ('6', '六月'), ('7', '七月'), ('8', '八月'),
         ('9', '九月'), ('10', '十月'), ('11', '十一月'), ('12', '十二月')], string='月份', default=default_target_month)
    target_amount = fields.Integer('门店目标', compute='_compute_target_amount', store=True)
    jiesuan_amount = fields.Integer('销售金额', compute='_compute_jiesuan_amount', store=True)
    completion = fields.Integer('目标完成占比')
    sale_id = fields.Many2one('sale.source', '占比类型')
    target_id = fields.Many2one('target.source', '目标数据')

    @api.depends('target_year', 'target_month', 'kunnr', 'ywy')
    def _compute_target_amount(self):
        for rec in self:
            # 确认是查询目标完成占比报表
            if rec.target_year:
                # 选择月份（展示门店/业务月度目标）
                if rec.target_month:
                    if rec.ywy:
                        target_detail = self.env['team.target.detail'].search([('current_team_id', '=', rec.kunnr.id),
                                                                               ('detail_year', '=', rec.target_year),
                                                                               ('target_month', '=?', rec.target_month),
                                                                               ('sales_member.id', '=?', rec.ywy)])
                    else:
                        target_detail = self.env['team.target.detail'].search([('current_team_id', '=', rec.kunnr.id),
                                                                              ('detail_year', '=', rec.target_year),
                                                                              ('target_month', '=?', rec.target_month)])
                    target_amount = 0
                    if target_detail:
                        for detail in target_detail:
                            target_amount += detail.team_target_monthly
                    rec.target_amount = target_amount
                # 不选择月份（展示门店/业务年度目标）
                else:
                    # 选择业务员,年度目标通过分配目标的取值
                    if rec.ywy:
                        ywy = rec.ywy.id
                        target_detail = self.env['team.target.detail'].search([('current_team_id', '=', rec.kunnr.id),
                                                                               ('detail_year', '=', rec.target_year),
                                                                               ('sales_member.id', '=?', ywy)])
                        target_amount = 0
                        if target_detail:
                            for detail in target_detail:
                                target_amount += detail.team_target_monthly
                        rec.target_amount = target_amount
                    # 不选择业务员,直接取门店年度目标
                    else:
                        target_year = self.env['team.target.year'].search([('team_id', '=', rec.kunnr.id),
                                                                           ('target_year', '=', rec.target_year)])
                        target_amount = 0
                        if target_year:
                            for target in target_year:
                                target_amount += target.invoiced_target_year
                        rec.target_amount = target_amount
            else:
                pass

    @api.depends('target_year', 'target_month', 'kunnr', 'ywy')
    def _compute_jiesuan_amount(self):
        for rec in self:
            # 确认是查询目标完成占比报表
            if rec.target_year:
                if rec.kunnr:
                    kunnr_sql = "and kunnr = %s" % rec.kunnr.id
                else:
                    kunnr_sql = ''
                if rec.ywy:
                    ywy_sql = "and ywy = '%s'" % rec.ywy.id
                else:
                    ywy_sql = ""
                if rec.target_month:
                    month = '%02d' % int(rec.target_month)
                    time_sql = "TO_CHAR(\"LFADT\", 'YYYYMM') = '%s'" % (str(rec.target_year) + str(month))
                    sql_str = "select * from outbound_final where %s %s %s" % (time_sql, kunnr_sql, ywy_sql)
                else:
                    time_sql = "TO_CHAR(\"LFADT\", 'YYYY') = '%s'" % (str(rec.target_year))
                    sql_str = "select * from outbound_final where %s %s %s" % (time_sql, kunnr_sql, ywy_sql)
                rec._cr.execute(sql_str)
                res_amount = rec._cr.dictfetchall()
                jiesuan_amount = 0
                if res_amount:
                    for res in res_amount:
                        jiesuan_amount += res['jiesuanjine']
                rec.jiesuan_amount = jiesuan_amount
            else:
                pass

    # 获取查询视图的view_id,在js中访问该方法获取指定该视图id
    @api.model
    def get_view_id(self):
        query_view = self.env.ref('outbound_report.view_target_completion_query_report')
        query_view_id = query_view.id
        return query_view_id

    # 删除查询时在模板内创建的新纪录
    def init_target_date(self, ctx):
        if ctx['werks']:
            werks_sql = "and werks = '%s'" % ctx['werks']
        else:
            werks_sql = ''
        if ctx['vtweg']:
            vtweg_sql = "and vtweg = '%s'" % ctx['vtweg'][0]
        else:
            vtweg_sql = ''
        if ctx['vkorgtext']:
            vkorgtext_sql = "and vkorgtext = '%s'" % ctx['vkorgtext'][0]
        else:
            vkorgtext_sql = ''
        if ctx['kunnr']:
            kunnr_sql = "and kunnr = %s" % ctx['kunnr'][0]
        else:
            kunnr_sql = ''
        if ctx['ywy']:
            ywy_sql = "and ywy = '%s'" % ctx['ywy'][0]
        else:
            ywy_sql = ''
        if ctx['target_month']:
            target_month_sql = "and target_month = '%s'" % ctx['target_month']
        else:
            target_month_sql = ''
        if ctx['target_year']:
            target_year_sql = "target_year = '%s'" % ctx['target_year']
        else:
            target_year_sql = ''
        del_sql = "delete from outbound_final where %s %s %s %s %s %s %s" % (target_year_sql, target_month_sql, werks_sql, vtweg_sql, vkorgtext_sql, kunnr_sql, ywy_sql)
        self._cr.execute(del_sql)

    def open_target_table(self):
        data = self.read()[0]
        ctx = self._context.copy()
        # 获取视图的id,return时返回指定视图
        # tree_view = self.env.ref('outbound_report.target_completion_report_tree_view')
        graph_view = self.env.ref('outbound_report.target_completion_report_graph_view')

        ctx['target_year'] = data['target_year']
        ctx['target_month'] = data['target_month']
        ctx['kunnr'] = data['kunnr']
        ctx['ywy'] = data['ywy']
        ctx['werks'] = data['werks']
        ctx['vtweg'] = data['vtweg']
        ctx['vkorgtext'] = data['vkorgtext']
        ctx['target_amount'] = data['target_amount']
        ctx['jiesuan_amount'] = data['jiesuan_amount']
        ctx['new_view'] = 1

        domain_list = []
        if ctx['target_year']:
            year_query = ('target_year', '=', ctx['target_year'])
            domain_list.append(year_query)
        if ctx['target_month']:
            month_query = ('target_month', '=', ctx['target_month'])
            domain_list.append(month_query)
        if ctx['werks'] and ctx['werks'] != '0000':
            werks_query = ('werks', '=', ctx['werks'])
            domain_list.append(werks_query)
        if ctx['vtweg']:
            vtweg_query = ('vtweg', '=', ctx['vtweg'][0])
            domain_list.append(vtweg_query)
        if ctx['vkorgtext']:
            vkorgtext_query = ('vkorgtext', 'ilike', ctx['vkorgtext'][0])
            domain_list.append(vkorgtext_query)
        if ctx['kunnr']:
            kunnr_query = ('kunnr', '=', ctx['kunnr'][0])
            domain_list.append(kunnr_query)
        if ctx['ywy']:
            ywy_query = ('ywy', '=', ctx['ywy'][0])
            domain_list.append(ywy_query)

        # 在没有数据时直接删除创建的新纪录
        if ctx['target_amount'] == 0 and ctx['jiesuan_amount'] == 0:
            self.init_target_date(ctx)

        return {
            'name': '目标完成占比报表',
            # 'view_type': 'dashboard',
            'view_type': 'form',
            # 'view_mode': 'dashboard',
            'view_mode': 'tree,graph',
            'res_model': 'outbound.final',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': domain_list,
            # 实现视图重定向
            'views': [ # [tree_view.id, 'tree'],
                      [graph_view.id, 'graph']],
        }

    def get_jiesuan_amount(self, ctx):
        kunnr_sql = "and kunnr = %s" % str(ctx['kunnr'][0])
        if ctx['ywy']:
            ywy_sql = "and ywy = %s" % ctx['ywy'][0]
        else:
            ywy_sql = ""
        if ctx['target_month']:
            month = '%02d' % int(ctx['target_month'])
            time_sql = "TO_CHAR(\"LFADT\", 'YYYYMM') = '%s'" % (str(ctx['target_year'])+str(month))
            sql_str = "select * from outbound_final where %s %s %s" % (time_sql, kunnr_sql, ywy_sql)
        else:
            time_sql = "TO_CHAR(\"LFADT\", 'YYYY') = '%s'" % (str(ctx['target_year']))
            sql_str = "select * from outbound_final where %s %s %s" % (time_sql, kunnr_sql, ywy_sql)
        self._cr.execute(sql_str)
        res_amount = self._cr.dictfetchall()
        jiesuan_amount = 0
        if res_amount:
            for res in res_amount:
                jiesuan_amount += res['jiesuanjine']
        ctx['jiesuan_amount'] = jiesuan_amount
        return ctx['jiesuan_amount']

    def open_target_table2(self):
        data = self.read()[0]
        ctx = self._context.copy()
        tree_view = self.env.ref('outbound_report.target_completion_report_tree_view')
        graph_view = self.env.ref('outbound_report.target_completion_report_graph_view')
        ctx['werks'] = data['werks']
        ctx['vtweg'] = data['vtweg']
        ctx['vkorgtext'] = data['vkorgtext']
        ctx['kunnr'] = data['kunnr']
        ctx['ywy'] = data['ywy']
        domain_list = []
        if ctx['werks'] and ctx['werks'] != '0000':
            werks_query = ('werks', '=', ctx['werks'])
            domain_list.append(werks_query)
        if ctx['kunnr']:
            kunnr_query = ('kunnr', '=', ctx['kunnr'][0])
            domain_list.append(kunnr_query)
        if ctx['ywy']:
            ywy_query = ('ywy', '=', ctx['ywy'][0])
            domain_list.append(ywy_query)
        return {
            'name': '目标完成占比报表',
            # 'view_type': 'dashboard',
            'view_type': 'form',
            # 'view_mode': 'dashboard',
            'view_mode': 'tree,graph',
            'res_model': 'outbound.final',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': domain_list,
            # 实现视图重定向
            'views': [[tree_view.id, 'tree'],
                      [graph_view.id, 'graph']],
                }


class SaleSource(models.Model):
    _name = 'sale.source'
    _description = '占比类型'

    name = fields.Char('占比类型')


class TargetSource(models.Model):
    _name = 'target.source'
    _description = '目标数据来源'

    name = fields.Char('数据来源')