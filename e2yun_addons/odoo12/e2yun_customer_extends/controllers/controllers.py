# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.mail.controllers import main

class MailController(main.MailController):
    _cp_path = '/mail'

    @http.route('/mail/init_messaging', type='json', auth='user')
    def mail_init_messaging(self):
        result = super(MailController, self).mail_init_messaging()
        result['mail_failures'] = []

        return result


# class E2yunCsutomerExtends(http.Controller):
#     @http.route('/e2yun_csutomer_extends/e2yun_csutomer_extends/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/e2yun_csutomer_extends/e2yun_csutomer_extends/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_csutomer_extends.listing', {
#             'root': '/e2yun_csutomer_extends/e2yun_csutomer_extends',
#             'objects': http.request.env['e2yun_csutomer_extends.e2yun_csutomer_extends'].search([]),
#         })

#     @http.route('/e2yun_csutomer_extends/e2yun_csutomer_extends/objects/<model("e2yun_csutomer_extends.e2yun_csutomer_extends"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_csutomer_extends.object', {
#             'object': obj
#         })