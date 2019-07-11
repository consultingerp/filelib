# -*- coding: utf-8 -*-
from odoo import http

# class E2yunUserCenter(http.Controller):
#     @http.route('/e2yun_user_center/e2yun_user_center/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_user_center/e2yun_user_center/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_user_center.listing', {
#             'root': '/e2yun_user_center/e2yun_user_center',
#             'objects': http.request.env['e2yun_user_center.e2yun_user_center'].search([]),
#         })

#     @http.route('/e2yun_user_center/e2yun_user_center/objects/<model("e2yun_user_center.e2yun_user_center"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_user_center.object', {
#             'object': obj
#         })