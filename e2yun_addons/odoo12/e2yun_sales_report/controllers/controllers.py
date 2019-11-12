# -*- coding: utf-8 -*-
from odoo import http

# class E2yunSalesReport(http.Controller):
#     @http.route('/e2yun_sales_report/e2yun_sales_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_sales_report/e2yun_sales_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_sales_report.listing', {
#             'root': '/e2yun_sales_report/e2yun_sales_report',
#             'objects': http.request.env['e2yun_sales_report.e2yun_sales_report'].search([]),
#         })

#     @http.route('/e2yun_sales_report/e2yun_sales_report/objects/<model("e2yun_sales_report.e2yun_sales_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_sales_report.object', {
#             'object': obj
#         })