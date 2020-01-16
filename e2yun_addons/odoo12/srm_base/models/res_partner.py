# -*- coding: utf-8 -*-

from odoo import models, fields, api,exceptions
class res_partner(models.Model):
    _inherit = 'res.partner'

    order_confirm = fields.Boolean('Confirmation of purchase order',default=False)
    schedule_confirm = fields.Boolean('Schedule confirmed',default=False)
    allow_create_days = fields.Integer(String='Allow create days',default=0)
    allow_no_schedule_create = fields.Boolean(String='Allow No Schedule Create', default=False)
    purchae_order_cancel = fields.Boolean(String='Purchase Order Cancel Email', default=False)
    auto_send_email=fields.Boolean(String='auto send email', default=False)

    supplier_code = fields.Char(string='Supplier code', required=True)
    seal_of_pictures = fields.Binary("seal of pictures")
    user_signature = fields.Binary("The user signature")
    short_name = fields.Char("Short Name")

    _sql_constraints = [('supplier_code_uniq', 'unique(supplier_code)', 'error message dec supplier_code uniq')]

    @api.constrains('supplier_code')
    def check_supplier_code(self):
        if self.supplier_code:
            sql = "select supplier_code,name from res_partner where supplier_code='" + str(
                self.supplier_code) + "' and supplier='t' and id<>" + str(self.id) + ""
            self.env.cr.execute(sql)
            isf = self.env.cr.fetchone()
            if isf:
                raise exceptions.ValidationError("Supplier Code:" + str(self.supplier_code) + " Repetition")





