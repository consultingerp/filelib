# -*- coding: utf-8 -*-

from odoo import models, fields, api

class e2yun_demo_crm_extends(models.Model):
    _inherit = "e2yun.customer.info"

    x_studio_account_source = fields.Selection([["Other", "Other"],
                                                ["Net", "网络"],
                                                ["Internal_Referral", "内部推荐"],
                                                ["External_Referral", "外部引荐"],
                                                ["Cooperators", "合作伙伴"],
                                                ["Public_Relations", "公共关系"],
                                                ["Exhibition", "展会"]], 'Account Source', track_visibility='onchange')

