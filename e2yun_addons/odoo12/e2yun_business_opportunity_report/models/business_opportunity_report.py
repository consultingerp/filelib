# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api,tools


class CrmBusinessOpportunityReport(models.Model):
    _name = "crm.business.opportunity.report"
    _auto = False

    #表头
    name_title = fields.Char('Opportunity',readonly=True) #

    source_id = fields.Many2one('utm.source', string='Source') #

    rec_rev = fields.Char(string='Rec Rev',readonly=True) #

    create_uid_lead = fields.Many2one('res.users', string='Create lead' ,readonly=True)  #

    partner_id = fields.Many2one('res.partner', string='Customer',readonly=True) #

    email_from = fields.Char('Email' ,readonly=True ) #

    team_id = fields.Many2one('crm.team', string='Sales Team' ,readonly=True )  #

    tag_ids = fields.Many2one('crm.lead.tag', string='Tags' ,readonly=True  ) #

    date_closed = fields.Datetime('Closed Date', readonly=True)

    stage_id = fields.Many2one('crm.stage', string='Stage', readonly=True)

    user_id = fields.Many2one('res.users', string='Opportunity Owner',readonly=True)    #

    probability = fields.Float('Probability',readonly=True)  #

    planned_revenue = fields.Char('Expected Revenue', readonly=True)  #

    expected_revenue = fields.Char('Prorated Revenue',readonly=True)  #

    date_deadline = fields.Date('Expected Closing',readonly=True) #

    property_product_pricelist = fields.Many2one('product.pricelist',string='Pricelist',readonly=True) #

    amount = fields.Float(string='Amount',readonly=True) #

    amount_usd = fields.Float(string='Amount USD',readonly=True )#

    customer_owner= fields.Many2one( 'res.users',string='Customer Owner',readonly=True)  #

    phone = fields.Char('Phone', readonly=True)  #

    parent_team_id = fields.Many2one(comodel_name='crm.team', string='Parent Team id',readonly=True)  #

    payment_team_id = fields.Many2one('crm.team', string='Delivery team',readonly=True)  #

    parent_payment_team_id = fields.Many2one(comodel_name='crm.team', string='Delivery team L1',readonly=True) #

    sf_no = fields.Char(string='sf no')  #

    cooperate_with_partner = fields.Boolean('Cooperate with Partner?', default=False)

    code = fields.Char('code')
    x_studio_service_product = fields.Char('x_studio_service_product')
    x_studio_role = fields.Char('x_studio_role')
    x_studio_offshore_effort_ = fields.Char('x_studio_offshore_effort_')
    x_studio_project_start_date = fields.Char('x_studio_project_start_date')
    x_studio_project_end_date = fields.Char('x_studio_project_end_date')
    x_studio_digital_code = fields.Char('x_studio_digital_code')

    create_date_lead = fields.Datetime(string='Create Date',readonly=True) #


   # 含税金额
    price_tax = fields.Float(string='Total Tax', readonly=True)

    # 税率
    tax_id = fields.Char(string='Taxes',readonly=True)
    # 不含税金额
    price_subtotal = fields.Float(string='Subtotal', readonly=True)

    cgm = fields.Float(string='CGM%',readonly=True)
    pid = fields.Char(string='PID',readonly=True)

    contract_number = fields.Char(string='Contract Number',readonly=True)

    name = fields.Char('Description', readonly=True)

    product_id = fields.Many2one("product.product",
                                 string="Product",readonly=True,)

    #tag_ids1 = fields.Many2one('crm.lead.tag', string='Tags1', readonly=True)  #

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
                create or replace view crm_business_opportunity_report as (
                    select 
                    line.id,
                    line.product_id as product_id,
                    line.name as name,
                    line.contract_number as contract_number,
                    line.pid as pid,
                    line.cgm as cgm,
                    line.price_subtotal as price_subtotal,
                    lead.source_id as source_id,
                    lead.rec_rev as rec_rev,
                    lead.create_uid as create_uid_lead,
                    lead.partner_id as partner_id,
                    lead.email_from as email_from,
                    lead.team_id as team_id,
                    lead.date_closed as date_closed,
                    lead.stage_id as stage_id,
                    lead.tag_ids as tag_ids,
                    lead.user_id as user_id,
                    lead.probability as probability,
                    lead.planned_revenue as planned_revenue,
                    lead.expected_revenue as expected_revenue,
                    lead.date_deadline as date_deadline,
                    lead.property_product_pricelist as property_product_pricelist,
                    lead.amount as amount,
                    lead.amount_usd as amount_usd,
                    (select user_id from res_partner where id=lead.partner_id) as customer_owner,
                    lead.phone as phone,
                    lead.parent_team_id as parent_team_id,
                    lead.payment_team_id as payment_team_id,
                    lead.parent_payment_team_id as parent_payment_team_id,
                    lead.sf_no as sf_no,
                    (
                    select name from account_tax where id=(SELECT   account_tax_id FROM	account_tax_crm_lead_line_rel WHERE crm_lead_line_id = line.id)) AS tax_id
                    ,lead.code,
                    lead.cooperate_with_partner,
                    lead.x_studio_service_product as x_studio_service_product,
                    lead.x_studio_role as x_studio_role,
                    lead.x_studio_offshore_effort_ as x_studio_offshore_effort_,
                    lead.x_studio_project_start_date as x_studio_project_start_date,
                    lead.x_studio_project_end_date as x_studio_project_end_date,
                    lead.x_studio_digital_code as x_studio_digital_code,
                    lead.create_date as create_date_lead,
                     LEAD.name as name_title,
                     	  line.price_tax  as price_tax 
									  from crm_lead_line  line   
                    left join crm_lead lead on lead.id = line.lead_id
                    WHERE LEAD.stage_id=4
                    order by lead.create_date asc
                )
            """)
