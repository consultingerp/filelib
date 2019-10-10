# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api
import suds.client


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    saleorderid = fields.Char('订单编号')
    customerno = fields.Char('客户编号')
    customername = fields.Char('客户名称')
    werksname = fields.Char('门店名称')
    telephone_pos = fields.Char('联系电话')
    address_pos = fields.Char('客户地址')
    sale_man = fields.Char('导购员')
    corporate_designer = fields.Char('公司设计师')
    delivery_date = fields.Date('预计交货日期')
    customer_po = fields.Char('客户PO号')
    contract_no = fields.Char('合同编号')
    order_reason = fields.Char('订单原因')
    lift = fields.Boolean('电梯')
    delivery_upstairs = fields.Boolean('送货上楼')
    headman = fields.Char('工长')
    designer = fields.Char('设计师')
    settlement_amount = fields.Float('结算金额')
    reduction_price1 = fields.Float('降价费1')
    reduction_price2 = fields.Float('降价费2')
    vkorg = fields.Char('销售组织')
    branch = fields.Char('分部')
    factory = fields.Char('工厂')
    actual_amount = fields.Float('费用实收')
    remark_pos = fields.Float('备注')
    order_state = fields.Char('订单状态')
    categories_of_stores = fields.Char('门店类别')
    order_date = fields.Date('下单日期')
    pricing_date = fields.Date('定价日期')
    order_type = fields.Char('订单类型')
    create_man_pos = fields.Char('创建人')
    create_date_pos = fields.Date('创建时间')
    last_update_date_pos = fields.Date('最后更新时间')
    update_man_pos = fields.Char('更新人')
    amount_pos = fields.Float('总金额')

    def action_sync_pos_sale_order(self):
        if self.saleorderid:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            url = ICPSudo.get_param('e2yun.sync_saleorder_webservice_url')  # webservice调用地址
            client = suds.client.Client(url)
            result = client.service.getSaleOrderInfo(self.saleorderid)
            print(result)
        else:
            raise Exception('pos销售订单为空，不能同步！')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    item_number = fields.Char('项目号')
    product_no = fields.Char('商品编号')
    product_name = fields.Char('商品名称')
    item_type = fields.Char('行项目类别')
    sale_quantity = fields.Float('销售数量')
    batch_no = fields.Char('批次')
    sale_amount = fields.Float('销售金额')
    settlement_amount = fields.Float('结算金额')
    sale_subtotal = fields.Float('销售小计')
    settlement_subtotal = fields.Float('结算小计')
    actual_cost = fields.Float('费用实收')
    cost_receivable = fields.Float('费用应收')
    reduction_price1 = fields.Float('降价费1')
    reduction_price2 = fields.Float('降价费2')
    return_reason = fields.Char('退货原因')
    factory_contract_number = fields.Char('工厂合同编号')
    factory = fields.Char('工厂')
    store = fields.Char('仓库')
    freezing_reason = fields.Char('冻结原因')
    if_close = fields.Boolean('是否关闭')
    if_third_party = fields.Boolean('是否第三方')
    if_processing = fields.Boolean('是否加工')
