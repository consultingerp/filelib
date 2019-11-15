# -*- coding: utf-8 -*-
from odoo import http

# class E2yunOnlineShopExtends(http.Controller):
#     @http.route('/e2yun_online_shop_extends/e2yun_online_shop_extends/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_online_shop_extends/e2yun_online_shop_extends/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_online_shop_extends.listing', {
#             'root': '/e2yun_online_shop_extends/e2yun_online_shop_extends',
#             'objects': http.request.env['e2yun_online_shop_extends.e2yun_online_shop_extends'].search([]),
#         })

#     @http.route('/e2yun_online_shop_extends/e2yun_online_shop_extends/objects/<model("e2yun_online_shop_extends.e2yun_online_shop_extends"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_online_shop_extends.object', {
#             'object': obj
#         })