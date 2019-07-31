# -*-coding:utf-8-*-

from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home

from odoo import http
from odoo.http import request


class WXAuthSignupHome(Home):
    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        authsignuphome = super(WXAuthSignupHome, self).web_auth_reset_password(*args, **kw)
        get_param = request.env['ir.config_parameter'].sudo().get_param
        authsignuphome.qcontext.update({
            'auth_signup_reset_password_qrcode_ticket': get_param('auth_signup_reset_password_qrcode_ticket')
        })
        return authsignuphome
