# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OutboundFinal(models.Model):
    _name = 'outbound.final'
    _description = '出库报表'

    salesorserid = fields.Char('销售订单')
    operatedatetime = fields.Datetime('日期')
    werks = fields.Char('工厂')
    vkorgtext = fields.Char('事业部')
    vtweg = fields.Char('分销渠道')
    ywy = fields.Char('导购员')
    mendian = fields.Char('门店')
    jine = fields.Char('金额')
    jiesuanjine = fields.Char('结算小计')
    xiaoshoujine = fields.Char('销售小计')
