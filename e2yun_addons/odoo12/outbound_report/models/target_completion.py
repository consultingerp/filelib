from _datetime import datetime

from odoo import api, fields, models, exceptions, tools


class TargetCompletion(models.Model):
    _inherit = 'outbound.final'
    _description = '目标完成占比情况'

    target_amount = fields.Integer('目标金额')

    def open_target_table(self):
        data = self.read()[0]
        ctx = self._context.copy()
        # 获取视图的id
        tree_view = self.env.ref('outbound_report.target_completion_report_tree_view')
        graph_view = self.env.ref('outbound_report.target_completion_report_graph_view')

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
            # 'views': [[tree_view.id, 'tree'],
            #           [graph_view.id, 'graph'], ],
        }