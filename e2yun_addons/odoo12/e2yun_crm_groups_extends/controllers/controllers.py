# -*- coding: utf-8 -*-
from odoo import http

# class E2yunCrmGroupsExtends(http.Controller):
#     @http.route('/e2yun_crm_groups_extends/e2yun_crm_groups_extends/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_crm_groups_extends/e2yun_crm_groups_extends/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_crm_groups_extends.listing', {
#             'root': '/e2yun_crm_groups_extends/e2yun_crm_groups_extends',
#             'objects': http.request.env['e2yun_crm_groups_extends.e2yun_crm_groups_extends'].search([]),
#         })

#     @http.route('/e2yun_crm_groups_extends/e2yun_crm_groups_extends/objects/<model("e2yun_crm_groups_extends.e2yun_crm_groups_extends"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_crm_groups_extends.object', {
#             'object': obj
#         })