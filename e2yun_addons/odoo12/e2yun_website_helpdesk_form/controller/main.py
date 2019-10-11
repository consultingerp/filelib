# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.http_routing.models.ir_http import slug
from bs4 import BeautifulSoup
import requests
import datetime
import logging

_logger = logging.getLogger(__name__)


class WebsiteForm(WebsiteForm):

    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        request.params['userip'] = request.httprequest.access_route[0]
        if request.params.get('order_datetime'):
            paraorder_datetime = request.params['order_datetime']
            order_datetime = datetime.datetime.strptime(request.params['order_datetime'], "%Y-%m-%d %H:%M")
            lang = request.env['ir.qweb.field'].user_lang()
            strftime_format = (u"%s %s" % (lang.date_format, lang.time_format))
            request.params['order_datetime'] = datetime.datetime.strftime(order_datetime, strftime_format)
        reponse_website = super(WebsiteForm, self).website_form(model_name, **kwargs)
        return reponse_website

    @http.route('''/helpdesk/<model("helpdesk.team", "[('use_website_helpdesk_form','=',True)]"):team>/submit''', type='http', auth="public", website=True)
    def website_helpdesk_form(self, team, **kwargs):
        website_helpdesk_form = super(WebsiteForm, self).website_helpdesk_form(team, **kwargs)
        teams = request.env['helpdesk.team'].sudo().search([])
        street = request.env.user.partner_id._display_address()
        website_helpdesk_form.qcontext['default_values'].update({
            'phone': request.env.user.partner_id.phone,
            'mobile': request.env.user.partner_id.mobile,
            'street': street,
            'userip': request.httprequest.access_route[0],
            'partner_id': request.env.user.partner_id.id,
            'teams': teams
        })
        # 更新JSDK以备使用定位功能,获取当前用户地址报修。
        url_ = request.httprequest.url;
        website_helpdesk_form.qcontext.update(request.env.user.get_jsapi_ticket(url_))
        return website_helpdesk_form

    @http.route('/website_form/common_problems', type='http', auth="public", methods=['GET', 'POST'], website=True)
    def website_common_problems(self, **kwargs):
        return request.render("e2yun_website_helpdesk_form.common_problems")

    @http.route('/website_form/userhelpdesk', type='http', auth="public", methods=['GET', 'POST'], website=True)
    def website_userhelpdesk(self, **kwargs):
        # ('/helpdesk/' + slug(team) + '/submit')
        userip = request.httprequest.access_route[0]
        url = "http://ip138.com/ips138.asp"
        ip_check = {'ip': userip}
        r = requests.request('GET', url, params=ip_check)
        r.encoding = 'gbk'
        demo = r.text
        soup = BeautifulSoup(demo, "html.parser")
        soup = soup.ul
        # print(r.request.url)
        region_user = soup.contents[0].string[5:7]
        team_id = request.env['helpdesk.team'].search([('name', 'like', region_user)], limit=1).id
        if not team_id:
            team_id = request.env['helpdesk.team'].search([], limit=1, order='id asc').id
        _logger.info("地区：%s:%s" % (userip, region_user))
        _logger.info("查询接口1：%s", soup.contents[0].string[5:])
        _logger.info("查询接口2：%s", soup.contents[1].string[6:])
        _logger.info("查询接口3：%s", soup.contents[2].string[6:])
        helpdeskurl = '/helpdesk/' + str(team_id) + '/submit'
        return http.local_redirect(helpdeskurl)

    def getuserip(self, request):
        userip = request.httprequest.remote_addr
        print(userip)
        if userip == '127.0.0.1':
            userip = request.httprequest.headers.get('X-Forwarded-For')
        return userip
