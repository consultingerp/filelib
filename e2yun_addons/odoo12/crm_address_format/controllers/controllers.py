# -*- coding: utf-8 -*-
from odoo import http

# class CrmAddressFormat(http.Controller):
#     @http.route('/crm_address_format/crm_address_format/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_address_format/crm_address_format/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_address_format.listing', {
#             'root': '/crm_address_format/crm_address_format',
#             'objects': http.request.env['crm_address_format.crm_address_format'].search([]),
#         })

#     @http.route('/crm_address_format/crm_address_format/objects/<model("crm_address_format.crm_address_format"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_address_format.object', {
#             'object': obj
#         })