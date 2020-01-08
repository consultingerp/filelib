# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo import models, fields, api
from odoo.http import request
import datetime
import logging
import urllib
from odoo.tools.safe_eval import safe_eval

from odoo import http

_logger = logging.getLogger(__name__)


class WebCenterController(http.Controller):
    @http.route('/usercenter', type='http', auth='user', methods=['GET', 'POST'], website=True)
    def usercenter(self, **kwargs):
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
            'execute_code': self.execute_code,
            'urllib': urllib,
            'centerjscss': True,
            'title': '个人中心'
        }
        return request.render("web_user_center.miancenter", values)

    @api.model
    def execute_code(self, code_exec):
        localdict = {
            'cr': request.env.cr,
            'uid': request.env.uid,
            'request': request,  # 请求
            'result': None,  # 用于存储返回结果
            '_': _,
        }
        safe_eval(code_exec, localdict, mode="exec", nocopy=True)
        result = localdict['result']
        return result

    @http.route('/structure_page', type='http', auth='user', methods=['GET', 'POST'], website=True)
    def structure_iframe_page(self, **kwargs):
        usercenter_menu = request.env['usercenter.menu'].sudo().search([], order='display_Position,sequence')
        usercenter_menu_used = usercenter_menu
        url = request.params.get('url')
        no_footer = request.params.get('no_footer')
        no_footer = False if no_footer else True
        no_affix_top_menu = request.params.get('no_affix_top_menu')
        no_affix_top_menu = False if no_affix_top_menu else True
        values = {
            'no_footer': no_footer,
            'no_affix_top_menu': no_affix_top_menu,
            'usercenter_menu': usercenter_menu_used,
            'url': url,
            'execute_code': self.execute_code,
            'urllib': urllib,
            'centerjscss': True,
            'title': '宏华骏成'
        }
        my_user_center_menu = request.env.ref('web_user_center.my_user_center').id
        if url == '/usercenter' or str(my_user_center_menu) in url:
            return request.render("web_user_center.miancenter", values)
        return request.render("web_user_center.structure_iframe_page", values)
