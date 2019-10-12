# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OutboundFinal(models.Model):
    _name = 'outbound.final'
    _description = '出库报表'

    ID = fields.Char('ID')
    salesorderid = fields.Char('销售订单')
    LFADT = fields.Datetime('日期', required=True)
    werks = fields.Char('工厂')
    vkorgtext = fields.Char('事业部')
    vtweg = fields.Char('分销渠道')
    ywy = fields.Char('导购员')
    kunnr = fields.Char('门店')
    # jine = fields.Char('金额')
    jiesuanjine = fields.Char('结算小计')
    xiaoshoujine = fields.Char('销售小计')


    def xxxx(self):
        pass