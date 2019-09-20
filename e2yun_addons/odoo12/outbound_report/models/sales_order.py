# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SalesOrder(models.Model):
    _name = 'sales.order'
    _description = '销售订单明细'

    POSID = fields.Char('销售和分销凭证号')
    POSNR = fields.Char('销售和分销凭证的项目号')
    MATNR = fields.Char('物料号')
    ARKTX = fields.Char('销售订单项目短文本')
    WERKS = fields.Char('工厂')
    LGORT = fields.Char('库存地点')
    LFIMG = fields.Float(string='实际已交货量(按销售单位)', digits=(13, 3))
    MEINS = fields.Char('基本计量单位')
    VGBEL = fields.Char('参考单据的单据编号')
    VGPOS = fields.Char('采购凭证的项目编号')
    BWART = fields.Char('移动类型(库存管理)')
    VRKME = fields.Char('销售单位')
    LGMNG = fields.Float(string='以仓库保管单位级的实际交货数量', digits=(13, 3))
    SHWRK = fields.Char('工厂')
    BRGEW = fields.Float(string='毛重', digits=(13, 3))
    GEWEI = fields.Char('重量单位')
    VOLUM = fields.Float(string='业务量', digits=(13, 3))
    VOLEH = fields.Char('体积单位')
    CHARG = fields.Char('批号')
    salesorderid = fields.Char('销售订单号')
    delete = fields.Char('删除标识')
    # delete属性在pos中为del,与系统名冲突
    labst = fields.Char('可用库存')
    receivebs = fields.Char('收货确认标识')
    receivenum = fields.Char('收货确认数量')
    ordertypetext = fields.Char('订单类型')
    ordertype = fields.Char('订单类型')
    itemtype = fields.Char('行项目类型')
    itemtypetext = fields.Char('行项目类型文本')
    jiagong = fields.Char('是否加工')
    jiagongcharg = fields.Char('加工批次号')
    guanlianbianhao = fields.Char('关联编号')
    guanlianbianhaotype = fields.Selection([(1, '套餐'), (2, '配对')])
    peiduishuliang = fields.Char('配对数量')
    atwrt = fields.Char('色号')