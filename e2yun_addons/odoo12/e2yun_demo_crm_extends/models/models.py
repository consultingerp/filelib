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

class e2yun_demo_crm_extend_sres_partner(models.Model):
    _inherit = "res.partner"

    x_studio_account_type = fields.Selection([["Target Client", "目标客户"], ["Active Client", "活动客户"],
                                              ["Significant Client", "重要客户"]], 'Account type', track_visibility='onchange')

    x_studio_ = fields.Selection(
        [["客户类型", "T&M 合约，按月/按季度计费"], ["行业1", "按里程碑计费的 FP"],
         ["银行", "项目完成后支付工资，项目周期小于2个月"],
         ["制造业", "项目完成后支付工资，项目周期大于2个月"]], 'Way of settlement', track_visibility='onchange')

class e2yun_demo_crm_extend_crm_lead(models.Model):
    _inherit = "crm.lead"

    proposal_type = fields.Selection([["recruiting", "邀请"],
                                      ["structured RFP", "招标"],
                                      ["prospecting", "探寻"]], '方案类型', track_visibility='onchange')
