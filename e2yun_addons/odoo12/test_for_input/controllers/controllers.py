# -*- coding: utf-8 -*-
from odoo import http

# class TestForInput(http.Controller):
#     @http.route('/test_for_input/test_for_input/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_for_input/test_for_input/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_for_input.listing', {
#             'root': '/test_for_input/test_for_input',
#             'objects': http.request.env['test_for_input.test_for_input'].search([]),
#         })

#     @http.route('/test_for_input/test_for_input/objects/<model("test_for_input.test_for_input"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_for_input.object', {
#             'object': obj
#         })