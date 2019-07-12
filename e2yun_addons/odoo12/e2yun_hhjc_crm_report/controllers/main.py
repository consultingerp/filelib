# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class MainController(http.Controller):

    @http.route(['/crm_report/customer_loss_data/'], type='http', auth='user')
    def get_customer_loss_data(self, debug=False, **k):
        datas = []
        parent_obj = self.env['res.partner']

        v1 = parent_obj.search_count([('customer','=',True)])
        v2 = parent_obj.search_count([('customer','=',True),('state','in',['intention_customer','intention_customer_loss','target_customer','target_customer_loss','contract_customers'])])
        v3 = parent_obj.search_count([('customer','=',True),('state','in',['target_customer','target_customer_loss','contract_customers'])])
        v4 = parent_obj.search_count([('customer','=',True),('state','in',['contract_customers'])])
        datas.append({'value':v1,'name':'n1'})
        datas.append({'value':v2,'name':'n2'})
        datas.append({'value':v3,'name':'n3'})
        datas.append({'value':v4,'name':'n4'})



        return request.render('srm_stock_delivery.delivery_barcode_index')