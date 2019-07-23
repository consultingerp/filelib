# -*- coding: utf-8 -*-
from odoo import http

# class E2yunCoupon(http.Controller):
#     @http.route('/e2yun_coupon/e2yun_coupon/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_coupon/e2yun_coupon/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_coupon.listing', {
#             'root': '/e2yun_coupon/e2yun_coupon',
#             'objects': http.request.env['e2yun_coupon.e2yun_coupon'].search([]),
#         })

#     @http.route('/e2yun_coupon/e2yun_coupon/objects/<model("e2yun_coupon.e2yun_coupon"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_coupon.object', {
#             'object': obj
#         })