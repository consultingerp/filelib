# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_users(models.Model):
    _inherit = 'res.users'

    vat = fields.Char('统一社会信用代码')
    company_name = fields.Char('公司名称')

    @api.model
    def create(self, values):
        print("=================================创建用户开始==================================", values)
        user = super(res_users, self).create(values)
        print("=================================创建用户结束==================================", user)
        return user
