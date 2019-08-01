# -*- encoding: utf-8 -*-
##############################################################################
#
#    实现微信登录
##############################################################################

import logging
import base64

from odoo.addons.web.controllers.main import DataSet
from odoo.addons.web.controllers.main import Home
from odoo.addons.web.controllers.main import Session

from odoo import http
from odoo.http import request
from ..rpc import corp_client
from ..controllers import client
_logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# Odoo Web web Controllers
# ----------------------------------------------------------
class LoginHome(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        # OAuth提供商id
        provider_id = kw.get('state', '')
        # 以下微信相关 #
        code = kw.get('code', '')
        codetype = kw.get('codetype', '')
        wx_user_info = {}
        # 获取从WX过来的code
        wx_client_code = corp_client.corpenv(request.env)
        wxcode = wx_client_code.WX_CODE
        if not wxcode:
            wxcode = {}
        # logging.info(wxcode)
        if code is False:
            return super(LoginHome, self).web_login(redirect, **kw)
        if code:  # code换取token
            if code not in wxcode:  # 判断用户code是使用
                # 将获取到的用户放到Session中
                if codetype == 'corp':
                    wx_user_info = corp_client.get_user_info(request, code)
                else:
                    wx_user_info = client.get_user_info(request, code, code)
                    wx_user_info['UserId'] = wx_user_info['openid']
                kw.pop('code')
                wx_user_info['codetype'] = codetype
                request.session.wx_user_info = wx_user_info
                wx_client_code.WX_CODE[code] = code
            else:  # 如果使用，直接用session中的用户信息
                wx_user_info = request.session.wx_user_info
            if not wx_user_info or 'UserId' not in wx_user_info:
                return super(LoginHome, self).web_login(redirect, **kw)
            obj = request.env['wx.user.odoouser'].sudo().search([('openid', '=', wx_user_info['UserId'])])
            if obj.openid:
                kw['login'] = obj.user_id.login
                kw['password'] = obj.password
                request.params['login'] = obj.user_id.login
                request.params['password'] = obj.password
                tracetype = request.env['wx.tracelog.type'].sudo().search([('code', '=', provider_id)])
                if tracetype.exists():
                    request.env['wx.tracelog'].sudo().create({
                        "tracelog_type": tracetype.id,
                        "title": '菜单访问%s' % tracetype.name,
                        "user_id": obj.user_id.id if obj.user_id else None,
                        "wx_user_id": obj.wx_user_id.id if obj.wx_user_id else None
                    })
                uid = request.session.authenticate(request.session.db, obj.user_id.login, obj.password)
                if redirect:
                    return http.local_redirect(redirect)
                else:
                    return http.local_redirect('/')
            else:
                # request.session.logout()
                # uid = request.session.authenticate(request.session.db, obj.user_id.login, '')
                return super(LoginHome, self).web_login(redirect, **kw)
        elif request.session.wx_user_info:  # 存在微信登录访问
            if not request.params['login'] \
                    or not request.params['password']:
                return super(LoginHome, self).web_login(redirect, **kw)
            login_as = super(LoginHome, self).web_login(redirect, **kw)
            if 'error' in login_as.qcontext:
                return login_as
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                wx_user_info = request.session.wx_user_info
                wx_user_info['openid'] = wx_user_info['UserId']
                wx_user_info['user_id'] = uid
                wx_user_info['password'] = request.params['password']
                request.session.wx_user_info = wx_user_info
                userinfo = request.env['wx.user.odoouser'].sudo().search([('openid', '=', wx_user_info['UserId'])])
                if userinfo:
                    tracetype = request.env['wx.tracelog.type'].sudo().search([('code', '=', provider_id)])
                    if tracetype.exists():
                        request.env['wx.tracelog'].sudo().create({
                            "tracelog_type": tracetype.id,
                            "title": '菜单访问%s' % tracetype.name,
                            "user_id": userinfo.user_id.id if userinfo.user_id else None,
                            "wx_user_id": userinfo.wx_user_id.id if userinfo.wx_user_id else None
                        })
                    wxuserinfo = request.env['wx.user'].sudo().search([('openid', '=', wx_user_info['UserId'])])
                    wx_user_info['wx_user_id'] = wxuserinfo.id
                    request.env['wx.user.odoouser'].sudo().write(wx_user_info)
                else:
                    wxuserinfo = request.env['wx.user'].sudo().search([('openid', '=', wx_user_info['UserId'])])
                    wx_user_info['wx_user_id'] = wxuserinfo.id
                    obj = request.env['wx.user.odoouser'].sudo().create(wx_user_info)
                    resuser = request.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
                    if not resuser.wx_user_id:
                        _data = client.get_img_data(str(wx_user_info['headimgurl']))
                        resuser.write({
                            "wx_user_id": wxuserinfo.id,
                            "image": base64.b64encode(_data),
                        })


        else:
            if kw.get('login') and kw.get('password'):
                userinfo = request.env['wx.user.odoouser'].sudo().search([('user_id.login', '=', kw['login'])])
                if userinfo.exists():
                    userinfo.write({'password': kw['password']})

        return super(LoginHome, self).web_login(redirect, **kw)



    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        web_ = super(LoginHome, self).web_client(s_action, **kw)
        from ..controllers import client
        entry = client.wxenv(request.env)
        try:
            url_ = request.httprequest.url;
            #url_ = urljoin(request.httprequest.host_url, request.httprequest.full_path)
            # 解决urljoin 把参数只有一个?号去掉的问题
            #if request.httprequest.full_path.find("?") > 0 and url_.find("?") < 0:
            #    url_ = url_ + "%s" % '?'
            url_ = url_.replace(":80", "")
            #_logger.info("jsapi_ticket_url:%s" % url_)
            wx_appid, timestamp, noncestr, signature = entry.get_jsapi_ticket(url_)
            web_.qcontext.update({
                'wx_appid': wx_appid,
                'timestamp': timestamp,
                'noncestr': noncestr,
                'signature': signature
            })
        except Exception as e:
            _logger.error("加载微信jsapi_ticket错误。%s" % e)
        return web_


class WxSession(Session):
    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        uid = request.session.uid
        wx_user_info = request.session.wx_user_info
        ret = super(WxSession, self).logout(redirect)
        if wx_user_info:
            userinfo = request.env['wx.user.odoouser'].sudo().search(
                [('user_id', '=', uid), ('codetype', '=', wx_user_info['codetype'])])
            userinfo.unlink()
        return ret


class DataSet(DataSet):
    @http.route(['/web/dataset/call_kw', '/web/dataset/call_kw/<path:path>'], type='json', auth="user")
    def call_kw(self, model, method, args, kwargs, path=None):
        kw = super(DataSet, self).call_kw(model, method, args, kwargs, path)
        return kw


class WxMp(http.Controller):

    @http.route(['/MP_verify_xobfOnBKmFpc9HEU.txt'], type='http', auth="public")
    def mp(self, **kwargs):
        # response = http.send_file('MP_verify_xobfOnBKmFpc9HEU.txt')
        return 'xobfOnBKmFpc9HEU'

    @http.route(['/WW_verify_npgHFdA6yan51Qd5.txt'], type='http', auth="public")
    def mpcrop(self, **kwargs):
        # response = http.send_file('MP_verify_xobfOnBKmFpc9HEU.txt')
        return 'npgHFdA6yan51Qd5'

    @http.route(['/MP_verify_PT4MgExxX4ZXjTpP.txt'], type='http', auth="public")
    def mp_lh(self, **kwargs):
        # response = http.send_file('MP_verify_xobfOnBKmFpc9HEU.txt')
        return 'PT4MgExxX4ZXjTpP'
