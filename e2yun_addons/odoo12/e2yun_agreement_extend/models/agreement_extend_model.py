# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class Agreement(models.Model):
    _inherit = "agreement"

    agreement_code=fields.Char('Agreement Code',default="/")


    # @api.onchange('agreement_subtype_id')
    # def _onchange_agreement_subtype_id(self):
    #     if self.agreement_subtype_id.id == 1:
    #         self.agreement_code = '销售'
    #     elif self.agreement_subtype_id.id == 2:
    #          self.agreement_code = '采购'



    def write(self, vals):
        if vals['agreement_subtype_id']:
          agreement_subtype_obj = self.env['agreement.subtype'].browse(vals['agreement_subtype_id'])
          if agreement_subtype_obj.for_code:
            sequence_obj = self.env['ir.sequence']
            if vals['agreement_type_id']:
                agreement_type_id=vals['agreement_type_id']
            if agreement_type_id==1:
                agreement_code=sequence_obj.next_by_code('agreement.sale.code')
            elif agreement_type_id==2:
                agreement_code = sequence_obj.next_by_code('agreement.purchase.code')
            if agreement_code:
                verse_one=agreement_code[0:len(agreement_code)-4]
                verse_two=agreement_code[-4:]
                vals['agreement_code'] =verse_one+agreement_subtype_obj.for_code+verse_two

        return super(Agreement,self).write(vals)



class AgreementSubtype(models.Model):
    _inherit = "agreement.subtype"

    for_code = fields.Char(string="For Code", required=True)
