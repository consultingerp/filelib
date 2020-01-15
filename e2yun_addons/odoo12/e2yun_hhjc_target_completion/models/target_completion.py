from datetime import datetime
import calendar
from odoo import api, fields, models, exceptions, tools


class TargetCompletion(models.Model):
    _inherit = 'outbound_sync_from_pos.final'

    # @api.model
    # def create(self, vals_list):
    #     # 创建新(计算字段)记录之前删除数据库中原有的数据
    #     final = self.env['outbound_sync_from_pos.final'].search(['|', ('jiesuan_amount', '!=', ''), ('target_amount', '!=', '')])
    #     if final:
    #         for rec in final:
    #             rec.unlink()
    #     res = super(TargetCompletion, self).create(vals_list)
    #     # 判断是查询目标完成占比报表,生成两条数据
    #     if 'target_year' in vals_list:
    #         new_val_list = []
    #         # if res.jiesuan_amount:
    #         jiesuan_dict = vals_list.copy()
    #         jiesuan_dict.update({'completion': res.jiesuan_amount, 'sale_id': 1, 'target_id': 2})
    #         new_val_list.append(jiesuan_dict)
    #         # if res.target_amount:
    #         target_dict = vals_list.copy()
    #         target_dict.update({'completion': res.target_amount, 'sale_id': 1, 'target_id': 1})
    #         new_val_list.append(target_dict)
    #         aa = super(TargetCompletion, self).create(new_val_list)
    #         if aa:
    #             kk = aa[0]
    #             res.unlink()
    #             return kk
    #     # 不是,直接返回
    #     else:
    #         return res

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
    # target_amount = fields.Integer('门店目标', compute='_compute_target_amount', store=True)
    # jiesuan_amount = fields.Integer('销售金额', compute='_compute_jiesuan_amount', store=True)

    target_amount = fields.Integer('门店目标')
    jiesuan_amount = fields.Integer('销售金额')
    completion = fields.Integer('目标完成占比')
    sale_id = fields.Many2one('proportion.type', '占比类型')
    target_id = fields.Many2one('target_data.source', '数据来源')

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
                    sql_str = "select * from outbound_sync_from_pos_final where %s %s %s" % (time_sql, kunnr_sql, ywy_sql)
                else:
                    time_sql = "TO_CHAR(\"LFADT\", 'YYYY') = '%s'" % (str(rec.target_year))
                    sql_str = "select * from outbound_sync_from_pos.final where %s %s %s" % (time_sql, kunnr_sql, ywy_sql)
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
        query_view = self.env.ref('e2yun_hhjc_target_completion.view_target_completion_query_report2')
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
        del_sql = "delete from outbound_sync_from_pos_final where %s %s %s %s %s %s %s" % (target_year_sql, target_month_sql, werks_sql, vtweg_sql, vkorgtext_sql, kunnr_sql, ywy_sql)
        self._cr.execute(del_sql)

    def open_target_table(self):
        data = self.read()[0]
        ctx = self._context.copy()
        # 获取视图的id,return时返回指定视图
        tree_view = self.env.ref('e2yun_hhjc_target_completion.target_completion_report_tree_view2')
        graph_view = self.env.ref('e2yun_hhjc_target_completion.target_completion_report_graph_view2')

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

        kunnr2 = ctx['kunnr'][1]
        if ctx['ywy']:
            ywy2 = ctx['ywy'][1]
        else:
            ywy2 = ctx['ywy']
        if ctx['vtweg']:
            vtweg2 = ctx['vtweg'][1]
        else:
            vtweg2 = ctx['vtweg']
        if ctx['vkorgtext']:
            vkorgtext2 = ctx['vkorgtext'][1]
        else:
            vkorgtext2 = ctx['vkorgtext']

        t_year = '%s' % ctx['target_year']
        f_month = ctx['target_month']
        if f_month:
            last_day = calendar.monthrange(int(t_year), int(f_month))[1]
            t_month = '%02d' % int(f_month)
            str_start_date = '%s-%s-01' % (t_year, t_month)
            str_end_date = '%s-%s-%s' % (t_year, t_month, last_day)
        else:
            str_start_date = '%s-01-01' % t_year
            str_end_date = '%s-12-31' % t_year
        self.start_date = datetime.strptime(str_start_date, '%Y-%m-%d').date()
        self.end_date = datetime.strptime(str_end_date, '%Y-%m-%d').date()

        # 写入数据之前清空表数据
        clear_data_sql = 'truncate table outbound_sync_from_pos_final'
        self._cr.execute(clear_data_sql)

        pos_result = self.outbound_report_sync_from_pos()
        for res in pos_result:
            data_dict = {}
            if res['status'] == '已传输':
                data_dict.update({'salesorderid': res['salesorderid'],
                             'LFADT': res['lfdat'],
                             'werks': res['werks'],
                             'vkorgtext2': data['vkorgtext'],
                             'vtweg2': res['customname'],
                             'ywy2': res['assistant_name'],
                             'kunnr2': res['name1'],
                             'xiaoshoujine': res['xsxj'],
                             'jiesuanjine': float(res['jsxj'])
                             })
                self.create(data_dict)

        # 清除查询创建的数据行
        self.init_target_date(ctx)

        target_amount = self.get_target_amount(ctx)
        jiesuan_amount = self.get_jiesuan_amount(ctx)

        clear_data_sql = 'truncate table outbound_sync_from_pos_final'
        self._cr.execute(clear_data_sql)

        show_value = [{'target_year': t_year, 'target_month': f_month, 'werks': ctx['werks'],
                      'vkorgtext2': vkorgtext2, 'vtweg2': vtweg2, 'kunnr2': kunnr2,
                      'ywy2': ywy2, 'completion': target_amount, 'sale_id': 1, 'target_id': 1},
                    {'target_year': t_year, 'target_month': f_month, 'werks': ctx['werks'],
                     'vkorgtext2': vkorgtext2, 'vtweg2': vtweg2, 'kunnr2': kunnr2,
                     'ywy2': ywy2, 'completion': jiesuan_amount, 'sale_id': 1, 'target_id': 2}]
        for date in show_value:
            self.create(date)

        return {
            'name': '目标完成占比报表',
            # 'view_type': 'dashboard',
            'view_type': 'form',
            # 'view_mode': 'dashboard',
            'view_mode': 'tree,graph',
            'res_model': 'outbound_sync_from_pos.final',
            'type': 'ir.actions.act_window',
            'context': ctx,
            # 'domain': domain_list,
            # 实现视图重定向
            'views': [[tree_view.id, 'tree'],
                      [graph_view.id, 'graph']],
        }

    def get_jiesuan_amount(self, ctx):
        kunnr_sql = "and kunnr2 = '%s'" % str(ctx['kunnr'][1])
        if ctx['ywy']:
            ywy_sql = "and ywy2 = '%s'" % ctx['ywy'][1]
        else:
            ywy_sql = ""
        if ctx['target_month']:
            month = '%02d' % int(ctx['target_month'])
            time_sql = "TO_CHAR(\"LFADT\", 'YYYYMM') = '%s'" % (str(ctx['target_year'])+str(month))
            sql_str = "select * from outbound_sync_from_pos_final where %s %s %s" % (time_sql, kunnr_sql, ywy_sql)
        else:
            time_sql = "TO_CHAR(\"LFADT\", 'YYYY') = '%s'" % (str(ctx['target_year']))
            sql_str = "select * from outbound_sync_from_pos_final where %s %s %s" % (time_sql, kunnr_sql, ywy_sql)
        self._cr.execute(sql_str)
        res_amount = self._cr.dictfetchall()
        jiesuan_amount = 0
        if res_amount:
            for res in res_amount:
                jiesuan_amount += res['jiesuanjine']
        ctx['jiesuan_amount'] = jiesuan_amount
        return ctx['jiesuan_amount']

    def get_target_amount(self, ctx):
        # 选择月份（展示门店/业务月度目标）
        if ctx['target_month']:
            if ctx['ywy']:
                target_detail = self.env['team.target.detail'].search([('current_team_id', '=', ctx['kunnr'][0]),
                                                                       ('detail_year', '=', ctx['target_year']),
                                                                       ('target_month', '=?', ctx['target_month']),
                                                                       ('sales_member.id', '=?', ctx['ywy'])])
            else:
                target_detail = self.env['team.target.detail'].search([('current_team_id', '=', ctx['kunnr'][0]),
                                                                      ('detail_year', '=', ctx['target_year']),
                                                                      ('target_month', '=?', ctx['target_month'])])
            target_amount = 0
            if target_detail:
                for detail in target_detail:
                    target_amount += detail.team_target_monthly
        # 不选择月份（展示门店/业务年度目标）
        else:
            # 选择业务员,年度目标通过分配目标的取值
            if ctx['ywy']:
                target_detail = self.env['team.target.detail'].search([('current_team_id', '=', ctx['kunnr'][0]),
                                                                       ('detail_year', '=', ctx['target_year']),
                                                                       ('sales_member.id', '=?', ctx['ywy'])])
                target_amount = 0
                if target_detail:
                    for detail in target_detail:
                        target_amount += detail.team_target_monthly
            # 不选择业务员,直接取门店年度目标
            else:
                target_year = self.env['team.target.year'].search([('team_id', '=', ctx['kunnr'][0]),
                                                                   ('target_year', '=', ctx['target_year'])])
                target_amount = 0
                if target_year:
                    for target in target_year:
                        target_amount += target.invoiced_target_year
            return target_amount


class ProportionType(models.Model):
    _name = 'proportion.type'
    _description = '占比类型'

    name = fields.Char('占比类型')


class TargetSource2(models.Model):
    _name = 'target_data.source'
    _description = '目标数据来源'

    name = fields.Char('数据来源')