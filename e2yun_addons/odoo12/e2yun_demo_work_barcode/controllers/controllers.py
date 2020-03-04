# -*- coding: utf-8 -*-
from odoo import http

# class E2yunDemoWorkBarcode(http.Controller):
#     @http.route('/e2yun_demo_work_barcode/e2yun_demo_work_barcode/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_demo_work_barcode/e2yun_demo_work_barcode/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_demo_work_barcode.listing', {
#             'root': '/e2yun_demo_work_barcode/e2yun_demo_work_barcode',
#             'objects': http.request.env['e2yun_demo_work_barcode.e2yun_demo_work_barcode'].search([]),
#         })

#     @http.route('/e2yun_demo_work_barcode/e2yun_demo_work_barcode/objects/<model("e2yun_demo_work_barcode.e2yun_demo_work_barcode"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_demo_work_barcode.object', {
#             'object': obj
#         })