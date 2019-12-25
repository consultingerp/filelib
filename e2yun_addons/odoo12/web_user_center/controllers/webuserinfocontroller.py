# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo import models, fields, api
from odoo.http import request
from ..controllers import webcentercontroller
import datetime
import logging
import urllib
from odoo.tools.safe_eval import safe_eval

from odoo import http

_logger = logging.getLogger(__name__)


class WebUserInfoController(webcentercontroller.WebCenterController):
    @http.route('/user_info', type='http', auth='user', methods=['GET', 'POST'], website=True)
    def user_info(self, **kwargs):
        no_footer = request.params.get('no_footer')
        no_footer = False if no_footer else True
        no_affix_top_menu = request.params.get('no_affix_top_menu')
        no_affix_top_menu = False if no_affix_top_menu else True
        values = {
            'no_footer': no_footer,
            'no_affix_top_menu': no_affix_top_menu,
            'execute_code': self.execute_code,
            'urllib': urllib,
            'centerjscss': True,
            'd-none': True
        }
        return request.render("web_user_center.user_info", values)
