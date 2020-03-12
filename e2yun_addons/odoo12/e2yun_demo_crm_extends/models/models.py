# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

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

    customer_lost1 = fields.Char('退回原因', track_visibility='onchange')
    customer_lost2 = fields.Char('审批不通过原因', track_visibility='onchange')

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

    @api.multi
    def btn_exec_action(self):
        cx = self.env.context.copy() or {}
        if cx.get('btn_key') in ('N8IMU9JJ0E', '9QPVIFOWV7'):
            cx.update({'active_id': self.id, 'active_ids': self.ids})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'e2yun.customer.info.lost',
                'target': 'new',
                'context': cx,
            }
        else:
            return super(e2yun_demo_crm_extends, self).btn_exec_action()

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
    @api.multi
    def write(self, vals):
        flag = self.env.context.get('falg_no_drop')
        get_stage = vals.get('stage_id', False)
        stage_per = self.env['crm.stage'].browse(get_stage).probability
        if get_stage and stage_per == 0:
            if flag == 20200220:
                return super(e2yun_demo_crm_extend_crm_lead, self).write(vals)
            else:
                raise exceptions.Warning('请在商机中设置标记丢失/退出/暂停')
        else:
            return super(e2yun_demo_crm_extend_crm_lead, self).write(vals)

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

class e2yun_customer_info_lost(models.Model):
    _name = 'e2yun.customer.info.lost'

    lost_reason = fields.Char('退回原因')

    def confirm_customer_lost_reason(self):
        cx = self.env.context.copy() or {}
        if cx.get('btn_key') == 'N8IMU9JJ0E':
            self.env['e2yun.customer.info'].browse(cx.get('active_id')).write({'customer_lost1': self.lost_reason})
        elif cx.get('btn_key') == '9QPVIFOWV7':
            self.env['e2yun.customer.info'].browse(cx.get('active_id')).write({'customer_lost2': self.lost_reason})
        wkf_btn_obj = self.env['e2yun.workflow.node.button']
        btn_rec = wkf_btn_obj.search([('btn_key', '=', cx.get('btn_key', False))])
        if btn_rec:
            return btn_rec.with_context(cx).run()

class E2yunCRMDemoMailActivity(models.Model):
    _inherit = "mail.activity"

    @api.onchange('crm_lead_id')
    def onchange_crm_lead_res_id(self):
        if not self.res_id:
            self.res_id = self.crm_lead_id.id

    crm_lead_id = fields.Many2one('crm.lead', '对应商机', required=True)

    # res_model_id = fields.Many2one(
    #     'ir.model', 'Document Model',
    #     index=True, ondelete='cascade', required=True, default=178)

    @api.model
    def default_get(self, fields_list):
        flag = self.env.context.get('flag_crm_lead_activity', False)
        if flag == 2020022501:
            res = super(E2yunCRMDemoMailActivity, self).default_get(fields_list)
            res.update({'res_model_id': 178})
            return res
        else:
            return super(E2yunCRMDemoMailActivity, self).default_get(fields_list)

    # @api.model
    # def create(self, vals_list):
    #     cx = self.env.context.copy()
    #     return super(E2yunCRMDemoMailActivity, self).create(vals_list)
