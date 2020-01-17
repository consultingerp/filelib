# -*- coding: utf-8 -*-
from odoo import http

# class E2yunHhjcCrmLeadExtends(http.Controller):
#     @http.route('/e2yun_hhjc_crm_lead_extends/e2yun_hhjc_crm_lead_extends/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_hhjc_crm_lead_extends/e2yun_hhjc_crm_lead_extends/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_hhjc_crm_lead_extends.listing', {
#             'root': '/e2yun_hhjc_crm_lead_extends/e2yun_hhjc_crm_lead_extends',
#             'objects': http.request.env['e2yun_hhjc_crm_lead_extends.e2yun_hhjc_crm_lead_extends'].search([]),
#         })

#     @http.route('/e2yun_hhjc_crm_lead_extends/e2yun_hhjc_crm_lead_extends/objects/<model("e2yun_hhjc_crm_lead_extends.e2yun_hhjc_crm_lead_extends"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_hhjc_crm_lead_extends.object', {
#             'object': obj
#         })