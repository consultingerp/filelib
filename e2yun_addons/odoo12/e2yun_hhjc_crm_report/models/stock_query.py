# -*- coding: utf-8 -*-

from odoo import models, fields, api,tools,exceptions
from datetime import date
import datetime,time
from dateutil.relativedelta import relativedelta
import suds.client

class StockQueryCondiyion(models.Model):
    _name = 'stock.query.condition.report'
    _description = "stock_query_condition_report"

    def default_werks(self):
        return self.env['res.company']._company_default_get('stock.query.condition.report').company_code

    def default_werks_id(self):
        return self.env['res.company']._company_default_get('stock.query.condition.report').id

    def default_matne_code(self):
        ctx = self._context.copy()
        if ctx.get('matnr_code',False):
            matnr_code = ctx.get('matnr_code')
            if isinstance(matnr_code,str):
                return matnr_code.replace('*', '')

    def default_matne_code1(self):
        ctx = self._context.copy()
        if ctx.get('matnr_code',False):
            matnr_code = ctx.get('matnr_code')
            if isinstance(matnr_code,int):
                return matnr_code

    def default_charg(self):
        ctx = self._context.copy()
        if ctx.get('charg',False):
            return ctx.get('charg')

    def default_lgort(self):
        ctx = self._context.copy()
        if ctx.get('lgort',False):
            return ctx.get('lgort')

    def default_mendian(self):
        ctx = self._context.copy()
        if ctx.get('mendian',False):
            return ctx.get('mendian')

    matnr_code = fields.Char('物料编码1',default=default_matne_code)
    matnr_code1 = fields.Many2one('product.product',default=default_matne_code1,string='物料编码2')
    werks = fields.Char('工厂',default=default_werks,readonly=True)
    werks_id = fields.Integer('工厂',default=default_werks_id,readonly=True)
    lgort = fields.Many2one('crm.warehouse','仓库',default=default_lgort)
    charg = fields.Char('批次',default=default_charg)
    mendian = fields.Many2one('crm.team','门店代码',default=default_mendian)

    def init_date(self,ctx):

        #ctx = self._context.copy()

        matnr_code = ctx['matnr_code'] or ''
        werks = ctx['werks'] or ''
        lgort = ctx.get('lgort') or ''
        charg = ctx['charg'] or ''
        mendian = ctx['mendian'] or ''

        stock_query = self.env['stock.query.report']

        search_key = str(matnr_code) + '_' + str(werks) + '_' + str(lgort) + '_' + charg + '_' + str(self._uid) + '_' + str(mendian)

        del_sql = "delete from stock_query_report where to_char(create_date,'yyyymmdd') < to_char(CURRENT_DATE,'yyyymmdd')"
        self._cr.execute(del_sql)

        del_sql = "delete from stock_query_condition_report where to_char(create_date,'yyyymmdd') < to_char(CURRENT_DATE,'yyyymmdd')"
        self._cr.execute(del_sql)

        del_sql = "delete from stock_query_report where search_key = %s "
        self._cr.execute(del_sql, [search_key])

        #调用POS接口
        ICPSudo = self.env['ir.config_parameter'].sudo()
        #查询门店编码
        md_code = mendian
        if md_code:
            md_code = self.env['crm.team'].sudo().browse(md_code).shop_code

        #物料编码
        m_code = matnr_code
        if m_code and isinstance(m_code,int):
            m_code = self.env['product.product'].sudo().browse(m_code).default_code

        lgort_code = lgort
        if lgort_code:
            lgort_code = self.env['crm.warehouse'].sudo().browse(lgort_code).code

        url = ICPSudo.get_param('e2yun.pos_url')+'/esb/webservice/SyncReport?wsdl'  # webservice调用地址
        client = suds.client.Client(url)
        result = client.service.stockQuery(m_code,werks,lgort_code,charg,md_code,search_key)

        if result != 'S':
            raise exceptions.Warning('查询库存数据异常:' + result)



    def open_table(self):
        # if context is None:
        #     context = {}
        data = self.read()[0]
        ctx = self._context.copy()

        matnr_code = ''
        matnr_code1 = ''
        if 'matnr_code' in data and data['matnr_code']:
            matnr_code = str(data['matnr_code'])
            if matnr_code.find('*') < 0:
                matnr_code = '*'+matnr_code+'*'

        if 'matnr_code1' in data and data['matnr_code1']:
            matnr_code1 = data['matnr_code1'][0]

        if matnr_code and matnr_code1:
            raise exceptions.Warning('物料编码只能输入一个')

        if matnr_code or matnr_code1:
            ctx['matnr_code'] = matnr_code or matnr_code1
        else:
            ctx['matnr_code'] = False


        if 'werks' in data and data['werks']:
            ctx['werks'] = data['werks']
        else:
            ctx['werks'] = False
        if 'lgort' in data and data['lgort']:
            ctx['lgort'] = data['lgort'][0]
        else:
            ctx['lgort'] = False

        if 'charg' in data and data['charg']:
            ctx['charg'] = data['charg']
        else:
            ctx['charg'] = False

        if 'mendian' in data and data['mendian']:
            ctx['mendian'] = data['mendian'][0]
        else:
            ctx['mendian'] = False

        self.init_date(ctx)

        return {
            'name': '库存查询',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'stock.query.report',
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

class StockQuery(models.Model):
    _name = 'stock.query.report'
    _description = "stock_query_report"

    search_key = fields.Char('Search Key', readonly='True')
    matnr_code = fields.Char('商品编码', readonly='True')
    matnr_name = fields.Char('商品名称', readonly='True')
    logrt_name = fields.Char('仓库名称', readonly='True')
    charg = fields.Char('批次', readonly='True')
    atwrt = fields.Char('色号', readonly='True')
    labst = fields.Char('实际库存', readonly='True')
    un_com_qty = fields.Char('占货数量', readonly='True')
    prdha = fields.Char('产品层次', readonly='True')
    groes = fields.Char('规格', readonly='True')
    vbeln = fields.Char('销售订单', readonly='True')
    posnr = fields.Char('订单项目', readonly='True')

    def search(self, args, offset=0, limit=None, order=None, count=False):
        matnr_code = self._context['matnr_code'] or ''
        werks = self._context['werks'] or ''
        lgort = self._context.get('lgort') or ''
        charg = self._context['charg'] or ''
        mendian = self._context['mendian'] or ''

        search_key = str(matnr_code) + '_' + str(werks) + '_' + str(lgort) + '_' + charg + '_' + str(self._uid) + '_' + str(mendian)

        args = args + [('search_key','=',search_key)]
        result = super(StockQuery, self).search(
            args, offset=offset, limit=limit, order=order,
            count=count)

        return result