# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo import models, fields, api
from odoo.http import request
import datetime
import urllib
import logging

from odoo.addons.web_user_center.controllers.webcentercontroller import WebCenterController

from odoo import http

_logger = logging.getLogger(__name__)


class WebOlineMallController(WebCenterController):
    @http.route('/onlinemallcenter', type='http', auth='user', methods=['GET', 'POST'], website=True)
    def onlinemallcenter(self, **kwargs):
        usercenter_menu = request.env['usercenter.menu'].sudo().search([], order='display_Position,sequence')
        usercenter_menu_used = usercenter_menu
        no_footer = request.params.get('no_footer')
        no_footer = False if no_footer else True
        no_affix_top_menu = request.params.get('no_affix_top_menu')
        no_affix_top_menu = False if no_affix_top_menu else True
        values = {
            'no_footer': no_footer,
            'no_affix_top_menu': no_affix_top_menu,
            'usercenter_menu': usercenter_menu_used,
            'execute_code': super().execute_code,
            'urllib': urllib,
            'online_malljscss': True
        }
        return request.render("web_online_mall.miancenter", values)

    @http.route('/productinfo', type='http', auth='user', methods=['GET', 'POST'], website=True)
    def productinfo(self, **kwargs):
        usercenter_menu = request.env['usercenter.menu'].sudo().search([], order='display_Position,sequence')
        usercenter_menu_used = usercenter_menu
        no_footer = request.params.get('no_footer')
        no_footer = False if no_footer else True
        no_affix_top_menu = request.params.get('no_affix_top_menu')
        no_affix_top_menu = False if no_affix_top_menu else True
        values = {
            'no_footer': no_footer,
            'no_affix_top_menu': no_affix_top_menu,
            'usercenter_menu': usercenter_menu_used,
            'execute_code': super().execute_code,
            'urllib': urllib,
            'product_infojscss': True
        }
        return request.render("web_online_mall.productmain", values)
