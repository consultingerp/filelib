# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp

class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = 'crm.lead'

    tag_ids = fields.Many2one('crm.lead.tag', string='Opportunity Type',required=True, help="Classify and analyze your lead/opportunity categories like: Training, Service")
    property_product_pricelist = fields.Many2one('product.pricelist',string='Pricelist',required=True)
    amount = fields.Float(string='Amount',digits=dp.get_precision('Product Price'),required=True)
    amount_usd = fields.Float(string='Amount USD',digits=dp.get_precision('Product Price'))
    customer_owner= fields.Many2one( 'res.users',string='Customer Owner',compute='onchange_partner_id',groups="base.group_user",readonly=True)

    # _sql_constraints = [
    #     ('amount_gt_zero','CHECK (amount > 0)','The amount of opportunity must be greater than 0')
    # ]

    @api.constrains('amount')
    def check_gt_zero(self):
        for s in self:
            if s.amount<= 0:
                raise ValidationError('The amount of opportunity must be greater than 0')



    rec_rev = fields.Selection([("HB","HB-Hour Base"),
        ("DB","DB-Day Base"),
        ("MB","MB-Month Base"),
        ("RE","RE-Reimbursements Expenses"),
        ("MT","MT-Maintenance"),
        ("TF","TF-T&M Contract,FP Calculation"),
        ("HN","HN-Hardware Retail,Net(pass-through)"),
        ("SN","SN-Software Retail,Net(pass-through)"),
        ("HG","HG-Hardware Retail,Gross(without pass-through)"),
        ("SG","SG-Software Retail,Gross(without pass-through)"),
        ("SS","SS-Self-owned Software Product Sale"),
        ("FP","FP-Fixed price"),
        ("VG","VG-Service Retail,Gross(withou pass-through)"),
        ("VN","VN-Service Retail,Net(pass-through)"),
        ("WL","WL-Workload")],string='Rec Rev',required=True)

    cooperate_with_partner = fields.Boolean('Cooperate with Partner?',default=False)
    alliance_mode = fields.Selection([('Resell','Resell'),('Solution','Solution'),('Referral','Referral')],string='Alliance Mode')
    partner_name1 = fields.Many2one('res.partner',string='Partner Name 1',domain=[('supplier','=',True)])
    partner_name2 = fields.Many2one('res.partner',string='Partner Name 2',domain=[('supplier','=',True)])
    partner_name3 = fields.Many2one('res.partner',string='Partner Name 3',domain=[('supplier','=',True)])
    partner_name4 = fields.Many2one('res.partner',string='Partner Name 4',domain=[('supplier','=',True)])
    other_partner = fields.Char(string='Other Partner')
    product_name1 = fields.Many2one('product.product',string='Product Name 1')
    product_name2 = fields.Many2one('product.product',string='Product Name 2')
    product_name3 = fields.Many2one('product.product',string='Product Name 3')
    product_name4= fields.Many2one('product.product',string='Product Name 4')
    other_product= fields.Char(string='Other Product')
    losssuspend_detail= fields.Char(string='Loss/Suspend detail')

    @api.onchange("amount","property_product_pricelist")
    def onchange_amount_price(self):
        if not self.amount or self.amount == 0:
            self.planned_revenue = 0
            self.amount_usd = 0
        elif self.property_product_pricelist and self.amount:
            company_id = self.company_id or self.env.user.company_id
            create_date = self.create_date or self._origin.create_date or fields.Date.today()

            currency_rate = self.env['res.currency']._get_conversion_rate(self.property_product_pricelist.currency_id,company_id.currency_id, company_id,create_date)
            self.planned_revenue = self.amount * currency_rate

            usd_currency = self.env['res.currency'].search([('name','=','USD')])
            usd_currency_rate = self.env['res.currency']._get_conversion_rate(self.property_product_pricelist.currency_id,usd_currency,
                                                                          company_id, create_date)
            self.amount_usd = self.amount * usd_currency_rate


    @api.onchange("tag_ids","partner_id")
    def onchange_tag_ids(self):
        if self.tag_ids.name == 'New LOGO' and self.partner_id:
            opp_count = self.search_count([('partner_id','=',self.partner_id.id)])
            order_count = self.env['sale.order'].search_count([('partner_id','=',self.partner_id.id)])
            if opp_count > 0 or order_count > 0:
                self.tag_ids = False
                msg = "Customers already have opportunities or orders and cannot choose new customers."
                return {
                    'warning': {
                        'title': 'Tips',
                        'message': msg
                    }
                }

    @api.onchange('rec_rev')
    def onchange_rec_rev(self):
        if self.rec_rev in ['HN', 'SN', 'HG', 'SG']:
            self.cooperate_with_partner = True
        else:
            self.cooperate_with_partner = False

    def _onchange_partner_id_values(self, partner_id):
        res = super(CrmLead, self)._onchange_partner_id_values(partner_id)
        if res and partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            res['property_product_pricelist'] = partner.property_product_pricelist.id
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for line in self:
            line.customer_owner= line.partner_id.user_id.id



class CrmLeadLost(models.TransientModel):
    _name = 'crm.lead.lost'
    _inherit = 'crm.lead.lost'

    def _default_lost_reason_id(self):
        return self._context.get('lost_reason',False)

    def _default_losssuspend_detail(self):
        return self._context.get('losssuspend_detail',False)

    lost_reason_id = fields.Many2one('crm.lost.reason', 'Lost Reason',required=True,default=lambda self: self._default_lost_reason_id())
    losssuspend_detail = fields.Char(string='Loss/Suspend detail',required=True,default=lambda self: self._default_losssuspend_detail())

    @api.multi
    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        btn_type = self.env.context.get('btn_type',False)
        if btn_type:
            stage = self.env['crm.stage'].search([('name','=',btn_type)])
            leads.write({'lost_reason': self.lost_reason_id.id,'stage_id':stage[0].id,'losssuspend_detail':self.losssuspend_detail})
        else:
            leads.write({'lost_reason': self.lost_reason_id.id,'losssuspend_detail':self.losssuspend_detail})
        return leads.action_set_lost()

