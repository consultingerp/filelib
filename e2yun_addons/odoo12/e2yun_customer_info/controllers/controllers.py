# -*- coding: utf-8 -*-
from odoo import http

# class E2yunCustomerInfo(http.Controller):
#     @http.route('/e2yun_customer_info/e2yun_customer_info/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_customer_info/e2yun_customer_info/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_customer_info.listing', {
#             'root': '/e2yun_customer_info/e2yun_customer_info',
#             'objects': http.request.env['e2yun_customer_info.e2yun_customer_info'].search([]),
#         })

#     @http.route('/e2yun_customer_info/e2yun_customer_info/objects/<model("e2yun_customer_info.e2yun_customer_info"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_customer_info.object', {
#             'object': obj
#         })