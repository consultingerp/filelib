# -*- coding: utf-8 -*-
from datetime import datetime
import suds.client, time, logging, json
from odoo import api, fields, models, exceptions, tools


class OutboundFinal2(models.Model):
    _name = 'outbound_sync_from_pos.final'
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
        return self.env['res.company']._company_default_get('outbound_sync_from_pos.final').company_code

    def default_werks_id(self):
        return self.env['res.company']._company_default_get('outbound_sync_from_pos.final').id

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

    vkorgtext2 = fields.Char('事业部')
    vtweg2 = fields.Char('分销渠道')
    ywy2 = fields.Char('导购员')
    kunnr2 = fields.Char('门店')

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

        del_sql = "delete from outbound_sync_from_pos_final where %s %s %s %s %s %s" % (time_sql, werks_sql, vtweg_sql, vkorgtext_sql, kunnr_sql, ywy_sql)
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

        ctx['werks'] = data['werks']
        ctx['vtweg'] = data['vtweg']
        ctx['vkorgtext'] = data['vkorgtext']
        ctx['kunnr'] = data['kunnr']
        ctx['ywy'] = data['ywy']

        # 删除查询时创建的数据行
        self.init_outbound_date(ctx)

        return {
            'name': '出库报表查询',
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'outbound_sync_from_pos.final',
            'type': 'ir.actions.act_window',
            'context': ctx,
            # 'domain': domain_list,
            # 'views': [[2812, 'dashboard'], ],
            # 'context': ctx.update({'dashboard_view_ref': 'outbound_report.outbound_report_dashboard_view'}),
        }

    def outbound_report_sync_from_pos(self):

        if self.vtweg:
            vtweg_code = self.vtweg.code
        else:
            vtweg_code = False

        if self.vkorgtext:
            vkorgtext_code = self.vkorgtext.code
        else:
            vkorgtext_code = False

        if self.ywy:
            ywy_code = self.ywy.name
        else:
            ywy_code = False

        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncReport?wsdl'  # webservice调用地址
        client = suds.client.Client(url)

        result = client.service.queryOutbound(self.werks or '',  # 工厂
                                              self.start_date or '',
                                              self.end_date or '',
                                              vtweg_code or '',  # 分销渠道
                                              vkorgtext_code or '',  # 事业部
                                              self.kunnr.shop_code or '',  # 门店
                                              ywy_code or '')  # 导购员
        result2 = json.loads(result)
        return result2
