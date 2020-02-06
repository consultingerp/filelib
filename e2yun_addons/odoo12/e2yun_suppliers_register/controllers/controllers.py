# -*- coding: utf-8 -*-
from odoo import http

# class E2yunSupplyerRegist(http.Controller):
#     @http.route('/e2yun_supplyer_regist/e2yun_supplyer_regist/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_supplyer_regist/e2yun_supplyer_regist/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_supplyer_regist.listing', {
#             'root': '/e2yun_supplyer_regist/e2yun_supplyer_regist',
#             'objects': http.request.env['e2yun_supplyer_regist.e2yun_supplyer_regist'].search([]),
#         })

#     @http.route('/e2yun_supplyer_regist/e2yun_supplyer_regist/objects/<model("e2yun_supplyer_regist.e2yun_supplyer_regist"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_supplyer_regist.object', {
#             'object': obj
#         })