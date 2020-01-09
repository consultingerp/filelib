# -*-coding:utf-8-*-
from odoo import http, _
from odoo.http import request
from odoo import models, fields, api
from odoo.http import request
import datetime
import logging
import urllib
from odoo.tools.safe_eval import safe_eval
from odoo.addons.utils_tools.iptools.IpAddress import IpAddress

from odoo import http

_logger = logging.getLogger(__name__)


class WebUserInfoController(http.Controller):
    @http.route('/onlineshopuserinfo', type='json', auth="public", csrf=False, cors="*", website=True)
    def onlineshopuserinfo(self, **kwargs):
        # request.jsonrequest   # 可以获取传入参数信息
        company = request.env['res.company'].sudo().search_read([('display_show_area', '=', True)], ['name', 'id', 'show_area_text'])
        if not request.session.companys:  # 将显示的公司参数加载到session
            request.session.showcompanys = company
        self.get_show_userinfo(refresh=True)
        rest = dict()
        rest['company'] = company
        if request.session['area_id']:
            rest['user_company'] = request.session['area_id']
        else:
            rest['user_company'] = request.session.usronlineinfo['company_id']
        return {
            'rest': rest
        }

    @api.model
    def get_show_userinfo(self, refresh=False):
        # 如果存在session and 有时间参数
        if request.session.usronlineinfo and not refresh:
            _now = fields.datetime.now()
            # 如果session时间 在一天内不重新获取IP
            if _now - request.session.usronlineinfo['time'] <= datetime.timedelta(seconds=60 * 60 * 24):
                return
        userip = request.httprequest.access_route[0]
        ipinfo = IpAddress.getregion(userip)
        userinfo_region = {}
        if ipinfo:
            userregion = ipinfo['region']
            userinfo_region['time'] = fields.datetime.now()
            _logger.info("来源地区：%s" % userregion)
            # 根据公司配置显示用户所在公司
            user_company = request.env['res.company'].sudo().search([('area_text_mate', 'like', '%' + userregion)], limit=1)
            if user_company:
                _logger.info("地区对对应公司：%s" % user_company.id)
                userinfo_region['region'] = user_company.show_area_text
                userinfo_region['company_id'] = user_company.id
                request.session['select_area_id'] = user_company.select_area_id
            else:  # 默认显示北京公司
                userinfo_region['region'] = '北京'
                company = request.env['res.company'].sudo().search([('company_code', '=', '1000')], limit=1)
                userinfo_region['company_id'] = company.id
                _logger.info("地区对对应公司默认公司：%s" % company.id)
                request.session['select_area_id'] = user_company.select_area_id
        # 要显示的公司列表
        if not request.session.usronlineinfo or refresh:
            request.session.usronlineinfo = userinfo_region
        return userinfo_region
