# -*- coding: utf-8 -*-
import logging
import base64
from odoo.exceptions import AccessError

from odoo.addons.web.controllers.main import DataSet
from odoo.addons.web.controllers.main import Home
from odoo.addons.web.controllers.main import Session

from odoo import http
import werkzeug
from odoo.http import request

_logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# Odoo Web web Controllers
# ----------------------------------------------------------
class LoginHome(Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        web_ = super(LoginHome, self).web_client(s_action, **kw)
        if not request.session.uid:
            return web_
        try:
            if request.httprequest.referrer and 'structure_page'  in  request.httprequest.referrer:
                context = request.env['ir.http'].webclient_rendering_context()
                response = request.render('web.webclient_bootstrap', qcontext=context)
                response.headers['X-Frame-Options'] = 'SAMEORIGIN'
                return response
        except AccessError:
            return werkzeug.utils.redirect('/web/login?error=access')
        return web_
