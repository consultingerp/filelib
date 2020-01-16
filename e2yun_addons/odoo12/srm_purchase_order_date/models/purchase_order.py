# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    odate = fields.Date(string='Supplier confirm the deadline',required=True, readonly=True, states={'draft':[('readonly',False)]})

    qdate = fields.Datetime(string='Supplier confirmation date',readonly=True,states={
        'draft': [('invisible', True)],
        'sent': [('invisible', True)],
        'bid': [('invisible', True)]}
    )

    def write(self,vals):
        is_supplier = self.env['res.users']._get_default_supplier()
        if is_supplier!=0 :
            if 'state' in vals.keys() :
                if vals['state'] != 'supply_confirm':
                    raise exceptions.ValidationError('No operation permission')
            else:
                raise exceptions.ValidationError('No operation permission')
        order = super(PurchaseOrder, self).write(vals)
        return order