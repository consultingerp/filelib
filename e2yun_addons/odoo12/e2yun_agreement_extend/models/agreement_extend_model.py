# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class Agreement(models.Model):
    _inherit = "agreement"

    agreement_code=fields.Char('Agreement Code',default="/")

    @api.model
    def create(self, vals):
        vals['code'] = ""
        if 'agreement_subtype_id' in vals.keys() and vals['agreement_subtype_id']:
          agreement_subtype_obj = self.env['agreement.subtype'].browse(vals['agreement_subtype_id'])

          if agreement_subtype_obj.for_code and not (agreement_subtype_obj.name in '集团转包'
                                                     or agreement_subtype_obj.name in 'Other（其他）'):
            sequence_obj = self.env['ir.sequence']
            if 'agreement_type_id' in vals.keys():
                agreement_type_id=vals['agreement_type_id']
            else:
                agreement_type_id=self.agreement_type_id.id

            if agreement_type_id==1:
                agreement_code=sequence_obj.next_by_code('agreement.sale.code')
            elif agreement_type_id==2:
                agreement_code = sequence_obj.next_by_code('agreement.purchase.code')
            if agreement_code:
                verse_one=agreement_code[0:len(agreement_code)-4]
                verse_two=agreement_code[-4:]
                vals['agreement_code'] =verse_one+agreement_subtype_obj.for_code+verse_two
                vals['code'] = vals['agreement_code']

        return super(Agreement, self).create(vals)

    def write(self, vals):
        if 'agreement_subtype_id' in vals.keys() and vals['agreement_subtype_id']:
          agreement_subtype_obj = self.env['agreement.subtype'].browse(vals['agreement_subtype_id'])

          if agreement_subtype_obj.for_code and not (agreement_subtype_obj.name in'集团转包'
                                                  or agreement_subtype_obj.name in '其他' ):
            sequence_obj = self.env['ir.sequence']
            if 'agreement_type_id' in vals.keys():
                agreement_type_id=vals['agreement_type_id']
            else:
                agreement_type_id=self.agreement_type_id.id

            if agreement_type_id==1:
                agreement_code=sequence_obj.next_by_code('agreement.sale.code')
            elif agreement_type_id==2:
                agreement_code = sequence_obj.next_by_code('agreement.purchase.code')
            if agreement_code:
                verse_one=agreement_code[0:len(agreement_code)-4]
                verse_two=agreement_code[-4:]
                vals['agreement_code'] =verse_one+agreement_subtype_obj.for_code+verse_two
                vals['code'] = vals['agreement_code']
        return super(Agreement,self).write(vals)

    def import_file(self):
        print(self.id)
        wizard = self.env.ref(
            'e2yun_agreement_extend.view_agreement_file_import')
        return {
            'name': '导入文件',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'agreement.file.upload',
            'views': [(wizard.id, 'form')],
            'view_id': wizard.id,
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }




class AgreementSubtype(models.Model):
    _inherit = "agreement.subtype"

    for_code = fields.Char(string="For Code", required=True)


