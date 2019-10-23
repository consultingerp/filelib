# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api
import datetime
import suds.client
import json


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    salesorderid = fields.Char('订单编号')
    vip = fields.Char('客户编号')
    vipname = fields.Char('客户名称')
    kunnr = fields.Char('门店名称')
    telephone = fields.Char('联系电话')
    address = fields.Char('客户地址')
    ywy = fields.Char('导购员')
    gongsishejishitext = fields.Char('公司设计师')
    yujijiaohuoriqi = fields.Date('预计交货日期')
    po = fields.Char('客户PO号')
    contractno = fields.Char('合同编号')
    orderreason = fields.Char('订单原因')
    elevator = fields.Boolean('电梯')
    upstairs = fields.Boolean('送货上楼')
    gongzhang = fields.Char('工长')
    shejishi = fields.Char('设计师')
    jiesuanjine = fields.Float('结算金额')
    jiangjiafei1 = fields.Float('降价费1')
    jiangjiafei2 = fields.Float('降价费2')
    vkorg = fields.Char('销售组织')
    branch = fields.Char('分部')
    werks = fields.Char('工厂')
    feiyongshishou = fields.Float('费用实收')
    remarks = fields.Float('备注')
    orderstatustext = fields.Char('订单状态')
    viptypetext = fields.Char('门店类别')
    orderdate = fields.Date('下单日期')
    pricedate = fields.Date('定价日期')
    ordertypetext = fields.Char('订单类型')
    createuserid = fields.Char('创建人')
    insertdatetime = fields.Date('创建时间')
    updater = fields.Char('更新人')
    totalmoney = fields.Float('总金额')
    operatedatetime = fields.Datetime('pos最后更新时间')

    def action_sync_pos_sale_order(self):
        # self.env['sale.order']._fields.keys()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncSaleOrder?wsdl'  # webservice调用地址
        pageSize = ICPSudo.get_param('e2yun.pos_sync_pageSize') or 20
        client = suds.client.Client(url)
        sale_order = self.env['sale.order']
        sale_order_line = self.env['sale.order.line']

        if self.salesorderid:
            result = client.service.getSaleOrderInfo(self.salesorderid)
            # lastDate = datetime.datetime.now()
            # result = client.service.getSaleOrderInfo(lastDate)
            # print(result)
        else:
            info = self.env['sale.order'].search([('operatedatetime', '!=', False)], order='operatedatetime desc', limit=1)
            if info.operatedatetime:
                lastDate = info.operatedatetime.strftime('%Y-%m-%d %H:%M:%S')
            else:
                startDate = "2010-10-01"
                lastDate = datetime.datetime.strptime(startDate, '%Y-%m-%d').time()
                lastDate = lastDate.strftime('%Y-%m-%d %H:%M:%S')

            result = client.service.getSaleOrderInfos(lastDate, pageSize)
            json2python = json.loads(result)
            for line in json2python['ROOT']:
                data = {}
                date_line = {}
                for key in line.keys():
                    if key in sale_order._fields:
                        data[key] = line[key]
                partner = self.env['res.partner'].search([('app_code', '=', line['memberposid'])])
                data['partner_id'] = partner.id
                order_id = sale_order.create(data)

                orderitem = line.pop('orderitem')
                for line in orderitem:
                    for key in line:
                        if key in sale_order_line._fields:
                            date_line[key] = line[key]
                    date_line['order_id'] = order_id.id
                    date_line['name'] = line['maktx']
                    product = self.env['product.product'].search([('default_code', '=', line['matnr'])])
                    if not product:
                        self.env['product.product'].sync_pos_matnr_to_crm(line['matnr'], '2000-01-01')
                        product = self.env['product.product'].search([('default_code', '=', line['matnr'])])
                    date_line['product_id'] = product.id
                    sale_order_line.create(date_line)

            # raise Exception('pos销售订单为空，不能同步！')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rownum = fields.Char('项目号')
    matnr = fields.Char('商品编号')
    maktx = fields.Char('商品名称')
    itemtype = fields.Char('行项目类别')
    kwmen = fields.Float('销售数量')
    charg = fields.Char('批次')
    xiaoshoujine = fields.Float('销售金额')
    jiesuanjine = fields.Float('结算金额')
    itemtotal = fields.Float('销售小计')
    itemjiesuantotal = fields.Float('结算小计')
    feiyongshishou = fields.Float('费用实收')
    feiyongyingshou = fields.Float('费用应收')
    jiangjiafei1 = fields.Float('降价费1')
    jiangjiafei2 = fields.Float('降价费2')
    tuihuoyuanyintext = fields.Char('退货原因')
    gongchanghetongbianhao = fields.Char('工厂合同编号')
    werkstext = fields.Char('工厂')
    lgorttext = fields.Char('仓库')
    dongjieyuanyintext = fields.Char('冻结原因')
    closed = fields.Char('是否关闭')
    isthird = fields.Char('是否第三方')
    jiagongtext = fields.Char('是否加工')
