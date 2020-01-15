# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _

class purchase_inquiry_redirect(models.Model):
    _name = 'purchase.inquiry.redirect'

    def inquiry_redirect(self):
        params = self._context.get('params')
        if params:
            #token = params.get('token')
            order_id = params.get('order_id')
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            #'url': '/quote_purchase/%s' % order_id
            'url': '/quote_purchase/%d' % order_id
        }
        #'url': '/quote_purchase/%d' % order_id + '/%str' % token