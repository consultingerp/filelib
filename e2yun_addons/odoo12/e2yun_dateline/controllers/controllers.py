# -*- coding: utf-8 -*-
from odoo import http

# class E2yunDateline(http.Controller):
#     @http.route('/e2yun_dateline/e2yun_dateline/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_dateline/e2yun_dateline/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_dateline.listing', {
#             'root': '/e2yun_dateline/e2yun_dateline',
#             'objects': http.request.env['e2yun_dateline.e2yun_dateline'].search([]),
#         })

#     @http.route('/e2yun_dateline/e2yun_dateline/objects/<model("e2yun_dateline.e2yun_dateline"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_dateline.object', {
#             'object': obj
#         })