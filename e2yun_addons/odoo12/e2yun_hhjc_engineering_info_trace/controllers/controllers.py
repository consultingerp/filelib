# -*- coding: utf-8 -*-
from odoo import http

# class E2yunHhjcEngineeringInfoTrace(http.Controller):
#     @http.route('/e2yun_hhjc_engineering_info_trace/e2yun_hhjc_engineering_info_trace/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_hhjc_engineering_info_trace/e2yun_hhjc_engineering_info_trace/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_hhjc_engineering_info_trace.listing', {
#             'root': '/e2yun_hhjc_engineering_info_trace/e2yun_hhjc_engineering_info_trace',
#             'objects': http.request.env['e2yun_hhjc_engineering_info_trace.e2yun_hhjc_engineering_info_trace'].search([]),
#         })

#     @http.route('/e2yun_hhjc_engineering_info_trace/e2yun_hhjc_engineering_info_trace/objects/<model("e2yun_hhjc_engineering_info_trace.e2yun_hhjc_engineering_info_trace"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_hhjc_engineering_info_trace.object', {
#             'object': obj
#         })