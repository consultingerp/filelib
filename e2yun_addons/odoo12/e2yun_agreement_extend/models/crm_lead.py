# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

class CrmLead(models.Model):
    _inherit = "crm.lead"
    agreement_amount=fields.Float(string='Agreement Amount',readonly=True)
    agreement_amount_usd = fields.Float(string='Agreement Amount USD',readonly=True)
    agreement_code = fields.Many2one(
        "agreement",
        string="Agreement Code",readonly=True)  # 合同编码
    agreement_partner_id = fields.Many2one(
        "res.partner",
        string="Agreement Partner",readonly=True) #