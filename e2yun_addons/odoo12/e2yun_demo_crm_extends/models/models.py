# -*- coding: utf-8 -*-

from odoo import models, fields, api

class e2yun_demo_crm_extends(models.Model):
    _inherit = "e2yun.customer.info"

    @api.onchange('grade_id')
    def _onchange_grade_id(self):
        gradeid = self.grade_id.id
        if gradeid == False:
            self.x_studio_account_type = False
        elif gradeid == 18:
            self.x_studio_account_type = 'Target Client'
        elif gradeid == 19:
            self.x_studio_account_type = 'Active Client'
        else:
            self.x_studio_account_type = 'Significant Client'

    x_studio_account_type = fields.Selection([("Target Client", "目标客户"), ("Active Client", "活动客户"),
                                              ("Significant Client", "重要客户")], 'Account type', track_visibility='onchange', readonly=True)

    x_studio_account_source = fields.Selection([("Other", "Other"),
                                                ("Net", "网络"),
                                                ("Internal_Referral", "内部推荐"),
                                                ("External_Referral", "外部引荐"),
                                                ("Cooperators", "合作伙伴"),
                                                ("Public_Relations", "公共关系"),
                                                ("Exhibition", "展会")], 'Account Source', track_visibility='onchange')

    @api.model
    def create(self, vals_list):
        gradeid = vals_list.get('grade_id')
        if gradeid == 18:
            account_type = 'Target Client'
        elif gradeid == 19:
            account_type = 'Active Client'
        else:
            account_type = 'Significant Client'
        if gradeid:
            vals_list.update({'x_studio_account_type': account_type})
        return super(e2yun_demo_crm_extends, self).create(vals_list)

    @api.multi
    def write(self, vals):
        gradeid = vals.get('grade_id')
        if gradeid == 18:
            account_type = 'Target Client'
        elif gradeid == 19:
            account_type = 'Active Client'
        else:
            account_type = 'Significant Client'
        if gradeid:
            vals.update({'x_studio_account_type': account_type})
        return super(e2yun_demo_crm_extends, self).write(vals)


class e2yun_demo_crm_extend_sres_partner(models.Model):
    _inherit = "res.partner"

    @api.onchange('grade_id')
    def _onchange_grade_id(self):
        gradeid = self.grade_id.id
        if gradeid == False:
            self.x_studio_account_type = False
        elif gradeid == 18:
            self.x_studio_account_type = 'Target Client'
        elif gradeid == 19:
            self.x_studio_account_type = 'Active Client'
        else:
            self.x_studio_account_type = 'Significant Client'

    x_studio_account_type = fields.Selection([("Target Client", "目标客户"), ("Active Client", "活动客户"),
                                              ("Significant Client", "重要客户")], 'Account type', track_visibility='onchange', readonly=True)

    x_studio_ = fields.Selection(
        [("客户类型", "T&M 合约，按月/按季度计费"), ("行业1", "按里程碑计费的 FP"),
         ("银行", "项目完成后支付工资，项目周期小于2个月"),
         ("制造业", "项目完成后支付工资，项目周期大于2个月")], 'Way of settlement', track_visibility='onchange')

    x_studio_account_source = fields.Selection([("Other", "Other"),
                                                ("Net", "网络"),
                                                ("Internal_Referral", "内部推荐"),
                                                ("External_Referral", "外部引荐"),
                                                ("Cooperators", "合作伙伴"),
                                                ("Public_Relations", "公共关系"),
                                                ("Exhibition", "展会")], 'Account Source')


class e2yun_demo_crm_extend_crm_lead(models.Model):
    _inherit = "crm.lead"

    proposal_type = fields.Selection([("recruiting", "邀请"),
                                      ("structured RFP", "招标"),
                                      ("prospecting", "探寻")], '方案类型', track_visibility='onchange')

class e2yun_demo_crm_extend_crm_lead_lost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    @api.multi
    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        btn_type = self.env.context.get('btn_type', False)
        if btn_type:
            # stage = self.env['crm.stage'].search([('name', '=', btn_type)])
            leads.write({'lost_reason': self.lost_reason_id.id, 'stage_id': 11,
                         'losssuspend_detail': self.losssuspend_detail})
        else:
            leads.write({'lost_reason': self.lost_reason_id.id, 'losssuspend_detail': self.losssuspend_detail})
        return leads.action_set_lost()
