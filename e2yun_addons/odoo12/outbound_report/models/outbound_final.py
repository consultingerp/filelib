# -*- coding: utf-8 -*-
from _datetime import datetime

from odoo import api, fields, models, exceptions, tools


class OutboundFinal(models.Model):
    _name = 'outbound.final'
    _description = '出库报表'

    @api.depends('werks')
    @api.onchange('werks')
    def _onchange_werks(self):
        code = self.werks
        domain = [('factory', '=', code)]
        return {
            'domain': {'vkorgtext': domain}
        }

    @api.depends('kunnr')
    @api.onchange('kunnr')
    def _onchange_kunnr(self):
        code = self.kunnr.id
        domain = [('sale_team_id', '=', code)]
        return {
            'domain': {'ywy': domain}
        }

    def default_werks(self):
        return self.env['res.company']._company_default_get('outbound.final').company_code

    def default_werks_id(self):
        return self.env['res.company']._company_default_get('outbound.final').id

    def default_start_date(self):
        ctx = self._context.copy()
        if ctx.get('start_date', False):
            return ctx.get('start_date')

    def default_end_date(self):
        ctx = self._context.copy()
        if ctx.get('end_date', False):
            return ctx.get('end_date')

    def default_vkorgtext(self):
        ctx = self._context.copy()
        if ctx.get('vkorgtext', False):
            return ctx.get('vkorgtext')[0]

    def default_vtweg(self):
        ctx = self._context.copy()
        if ctx.get('vtweg', False):
            return ctx.get('vtweg')[0]

    def default_ywy(self):
        ctx = self._context.copy()
        if ctx.get('ywy', False):
            return ctx.get('ywy')[0]

    def default_kunnr(self):
        ctx = self._context.copy()
        if ctx.get('kunnr', False):
            return ctx.get('kunnr')[0]

    ID = fields.Char('ID')
    salesorderid = fields.Char('销售订单')
    LFADT = fields.Date('日期')
    start_date = fields.Date('日期从', default=default_start_date)
    end_date = fields.Date('日期到', default=default_end_date)
    werks = fields.Char('工厂', default=default_werks, readonly=True)
    vkorgtext = fields.Many2one('group.departments', '事业部', default=default_vkorgtext)
    vtweg = fields.Many2one('group.channels', '分销渠道', default=default_vtweg)
    ywy = fields.Many2one('res.users', '导购员', default=default_ywy, domain=[('function', 'in', ['店长', '店员'])])
    kunnr = fields.Many2one('crm.team', '门店', default=default_kunnr)
    jiesuanjine = fields.Float('结算小计')
    xiaoshoujine = fields.Float('销售小计')

    def init_outbound_date(self, ctx):
        start_date = str(ctx['start_date']).replace('-', '')
        end_date = str(ctx['end_date']).replace('-', '')
        time_sql = "to_char(start_date, 'YYYYMMDD') = '%s' and to_char(end_date, 'YYYYMMDD') = '%s'" % (start_date, end_date)
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
            kunnr_sql = "and kunnr = '%s'" % ctx['kunnr'][0]
        else:
            kunnr_sql = ''
        if ctx['ywy']:
            ywy_sql = "and ywy = '%s'" % ctx['ywy'][0]
        else:
            ywy_sql = ''

        del_sql = "delete from outbound_final where %s %s %s %s %s %s" % (time_sql, werks_sql, vtweg_sql, vkorgtext_sql, kunnr_sql, ywy_sql)
        self._cr.execute(del_sql)

    def open_table(self):
        data = self.read()[0]
        ctx = self._context.copy()

        if data['start_date'] and data['end_date']:
            date_now = datetime.now()
            if data['start_date'] > datetime.date(date_now):
                raise exceptions.Warning('开始日期不能大于当前日期')
            elif data['start_date'] > data['end_date']:
                raise exceptions.Warning('开始日期不能大于结束日期')
            elif data['end_date'] > datetime.date(date_now):
                raise exceptions.Warning('结束日期不能大于当前日期')
            ctx['start_date'] = data['start_date']
            ctx['end_date'] = data['end_date']
        else:
            raise exceptions.Warning('查询日期不能为空')

        ctx['werks'] = data['werks']
        ctx['vtweg'] = data['vtweg']
        ctx['vkorgtext'] = data['vkorgtext']
        ctx['kunnr'] = data['kunnr']
        ctx['ywy'] = data['ywy']

        domain_list = []
        sql1 = ('LFADT', '>=', ctx['start_date'])
        sql2 = ('LFADT', '<=', ctx['end_date'])
        domain_list.append(sql1)
        domain_list.append(sql2)
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

        # 删除查询时创建的数据行
        self.init_outbound_date(ctx)

        return {
            'name': '出库报表查询',
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'outbound.final',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': domain_list,
            # 'views': [[2812, 'dashboard'], ],
            # 'context': ctx.update({'dashboard_view_ref': 'outbound_report.outbound_report_dashboard_view'}),
        }

