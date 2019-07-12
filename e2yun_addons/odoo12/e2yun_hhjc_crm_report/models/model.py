# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api,exceptions
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    @api.model
    def get_customer_loss_data(self):
        datas = []
        parent_obj = self.env['res.partner']

        v1 = parent_obj.search_count([('customer','=',True)])
        v2 = parent_obj.search_count([('customer','=',True),('state','in',['intention_customer','intention_customer_loss','target_customer','target_customer_loss','contract_customers'])])
        v3 = parent_obj.search_count([('customer','=',True),('state','in',['target_customer','target_customer_loss','contract_customers'])])
        v4 = parent_obj.search_count([('customer','=',True),('state','in',['contract_customers'])])
        datas.append({'value':v1,'name':'潜在客户'})
        datas.append({'value':v2,'name':'意向客户'})
        datas.append({'value':v3,'name':'准客户'})
        datas.append({'value':v4,'name':'成交客户'})

        return datas