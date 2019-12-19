# -*- coding: utf-8 -*-
from odoo import http

# class E2yunCgeNetShopDefault(http.Controller):
#     @http.route('/e2yun_cge_net_shop_default/e2yun_cge_net_shop_default/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_cge_net_shop_default/e2yun_cge_net_shop_default/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_cge_net_shop_default.listing', {
#             'root': '/e2yun_cge_net_shop_default/e2yun_cge_net_shop_default',
#             'objects': http.request.env['e2yun_cge_net_shop_default.e2yun_cge_net_shop_default'].search([]),
#         })

#     @http.route('/e2yun_cge_net_shop_default/e2yun_cge_net_shop_default/objects/<model("e2yun_cge_net_shop_default.e2yun_cge_net_shop_default"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_cge_net_shop_default.object', {
#             'object': obj
#         })