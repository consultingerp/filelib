# -*- coding: utf-8 -*-
from odoo import http

# class E2yunHhjcTargetCompletion(http.Controller):
#     @http.route('/e2yun_hhjc_target_completion/e2yun_hhjc_target_completion/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_hhjc_target_completion/e2yun_hhjc_target_completion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_hhjc_target_completion.listing', {
#             'root': '/e2yun_hhjc_target_completion/e2yun_hhjc_target_completion',
#             'objects': http.request.env['e2yun_hhjc_target_completion.e2yun_hhjc_target_completion'].search([]),
#         })

#     @http.route('/e2yun_hhjc_target_completion/e2yun_hhjc_target_completion/objects/<model("e2yun_hhjc_target_completion.e2yun_hhjc_target_completion"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_hhjc_target_completion.object', {
#             'object': obj
#         })