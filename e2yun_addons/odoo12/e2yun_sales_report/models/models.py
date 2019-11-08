# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime

class e2yun_sales_report(models.Model):
    _name = 'sales.report.form'

    @api.depends('werks')
    @api.onchange('werks')
    def _onchange_werks(self):
        code = self.werks
        domain = [('factory', '=', code)]
        return {
            'domain': {'vkorgtext': domain}
        }

    def default_start_date(self):
        ctx = self._context.copy()
        if ctx.get('date_from1', False):
            return ctx.get('date_from1')

    def default_end_date(self):
        ctx = self._context.copy()
        if ctx.get('date_end2', False):
            return ctx.get('date_end2')

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

    date_from1 = fields.Date('日期从', default=default_start_date)
    date_end2 = fields.Date('日期到', default=default_start_date)
    werks = fields.Selection([('1000', "1000"), ('2000', "2000")], '工厂')
    vkorgtext = fields.Many2one('group.departments', '事业部', default=default_vkorgtext)
    vtweg = fields.Many2one('group.channels', '渠道', default=default_vtweg)
    ywy = fields.Many2one('res.users', '导购员', default=default_ywy)
    kunnr = fields.Many2one('crm.team', '门店', default=default_kunnr)

    def open_table(self):
        data = self.read()[0]
        ctx = self._context.copy()

        if data['date_from1'] and data['date_end2']:
            date_now = datetime.now()
            if data['date_from1'] > datetime.date(date_now):
                raise exceptions.Warning('开始日期不能大于当前日期')
            elif data['date_from1'] > data['date_end2']:
                raise exceptions.Warning('开始日期不能大于结束日期')
            elif data['date_end2'] > datetime.date(date_now):
                raise exceptions.Warning('结束日期不能大于当前日期')
            ctx['date_from1'] = data['date_from1']
            ctx['date_end2'] = data['date_end2']

        ctx['werks'] = data['werks']
        ctx['vtweg'] = data['vtweg']
        ctx['vkorgtext'] = data['vkorgtext']
        ctx['kunnr'] = data['kunnr']
        ctx['ywy'] = data['ywy']

        domain_list = []

        sale_orders = self.env['sale.order'].search([])
        if ctx['werks']:
            sale_orders1 = sale_orders.search([('werks', '=', ctx['werks'])])
        else:
            sale_orders1 = sale_orders
        if ctx['vtweg']:
            sale_orders2 = sale_orders1.search([('vtweg', '=', ctx['vtweg'][1])])
        else:
            sale_orders2 = sale_orders1
        if ctx['vkorgtext']:
            sale_orders3 = sale_orders2.search([('vkorgtext', '=', ctx['vkorgtext'][1])])
        else:
            sale_orders3 = sale_orders2
        if ctx['kunnr']:
            sale_orders4 = sale_orders3.search([('kunnr', '=', ctx['kunnr'][1])])
        else:
            sale_orders4 = sale_orders3
        if ctx['ywy']:
            sale_orders5 = sale_orders4.search([('ywy', '=', ctx['ywy'][1])])
        else:
            sale_orders5 = sale_orders4

        for orders in sale_orders5:
            if orders.insertdatetime:
                dd = orders.insertdatetime
                d1 = ctx['date_from1']
                d2 = ctx['date_end2']
                if dd >= d1 and dd<=d2:
                    domain_list.append(orders.id)

        return {
            'name': '销售明细报表',
            'view_type': 'form',
            'view_mode': 'tree,graph',
            'res_model': 'sale.order.line',
            'type': 'ir.actions.act_window',
            'domain': [('order_id', 'in', domain_list)],
            'context': ctx,
        }
