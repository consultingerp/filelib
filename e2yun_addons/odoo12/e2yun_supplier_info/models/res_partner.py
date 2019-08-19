# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    supplier_code = fields.Char('供应商代码')
    secondary_industry_ids = fields.Many2many(
        comodel_name='res.partner.industry', string="供应产品类别",
        domain="[('id', '!=', industry_id)]")

    organ_code = fields.Char('组织代码')
    business_license = fields.Binary('营业执照', attachment=True)
    annual_turnover = fields.Selection(
        [('1', '1000万以下'), ('2', '1000万-5000万'), ('3', '5000万-1亿'), ('4', '1亿-10亿'), ('5', '10亿-100亿')], '年营业额')
    employees = fields.Selection([('1', '500人以下'), ('2', '500-1000人'), ('3', '1000-5000人'), ('4', '5000-10000人')],
                                 '企业员工')
    authenitcation_id = fields.One2many('e2yun.supplier.authentication.info', 'partner_info_id', '认证信息')

    listed_company = fields.Boolean('是否上市')