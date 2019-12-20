# -*- coding: utf-8 -*-
from odoo import http

# class YcWebsiteHome(http.Controller):
#     @http.route('/yc_website_home/yc_website_home/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/yc_website_home/yc_website_home/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('yc_website_home.listing', {
#             'root': '/yc_website_home/yc_website_home',
#             'objects': http.request.env['yc_website_home.yc_website_home'].search([]),
#         })

#     @http.route('/yc_website_home/yc_website_home/objects/<model("yc_website_home.yc_website_home"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('yc_website_home.object', {
#             'object': obj
#         })