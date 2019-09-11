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
import werkzeug
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
        provider_id = kw.get('state', 'default')
        # 以下微信相关 #
        code = kw.get('code', '')
        codetype = kw.get('codetype', '')
        wx_user_info = {}
        # 获取从WX过来的code
        # wx_client_code = client.wxenv(request.env)
        # wxcode = wx_client_code.WX_CODE
        # if not wxcode:
        #     wxcode = {}
        # logging.info(wxcode)
        values = request.params.copy()
        user_agent = request.httprequest.headers.get('user-agent').lower()
        is_wx_client = True if 'micromessenger' in user_agent else False
        if code is False:
            return super(LoginHome, self).web_login(redirect, **kw)
        if code:  # code换取token
            entry = client.wxenv(request.env)
            # if code not in wxcode:  # 判断用户code是使用
            if not entry.wxclient.session.get(code):  # code 没有使用，用code 换取
                # 将获取到的用户放到Session中
                if codetype == 'corp':
                    wx_user_info = corp_client.get_user_info(request, code)  # code 换取微信登录信息 企业号
                else:
                    wx_user_info = client.get_user_info(request, code, code)  # code 换取微信登录信息 微信号
                    wx_user_info['UserId'] = wx_user_info['openid']
                kw.pop('code')
                wx_user_info['codetype'] = codetype
                request.session.wx_user_info = wx_user_info
                entry.wxclient.session.set(code, code)
                # wx_client_code.WX_CODE[code] = code
            else:  # 如果使用，直接用session中的用户信息
                wx_user_info = request.session.wx_user_info
            if not wx_user_info or 'UserId' not in wx_user_info:
                return super(LoginHome, self).web_login(redirect, **kw)
            odoouser = request.env['wx.user.odoouser'].sudo().search([('openid', '=', wx_user_info['UserId'])], limit=1)
            if odoouser.exists():
                kw['login'] = odoouser.user_id.login
                kw['password'] = odoouser.password
                request.params['login'] = odoouser.user_id.login
                request.params['password'] = odoouser.password
                tracetype = request.env['wx.tracelog.type'].sudo().search([('code', '=', provider_id)])
                if tracetype.exists():
                    request.env['wx.tracelog'].sudo().create({
                        "tracelog_type": tracetype.id,
                        "title": '菜单访问%s' % tracetype.name,
                        "user_id": odoouser.user_id.id if odoouser.user_id else None,
                        "wx_user_id": odoouser.wx_user_id.id if odoouser.wx_user_id else None
                    })
                login_as = super(LoginHome, self).web_login(redirect, **kw)
                if 'error' in login_as.qcontext:
                    return login_as
                logging.info("登录用户%s:%s" % (odoouser.user_id.login, wx_user_info['UserId']))
                try:
                    uid = request.session.authenticate(request.session.db, odoouser.user_id.login, odoouser.password)
                except Exception as e:
                    logging.info("登录用户出错：%s:%s:%s" % (odoouser.user_id.login, wx_user_info['UserId'], e))
                    return http.local_redirect('/web/login')
                if redirect:
                    return http.local_redirect(redirect)
                else:
                    return http.local_redirect('/')
            else:
                # request.session.logout()
                # uid = request.session.authenticate(request.session.db, obj.user_id.login, '')
                request.session.uid = None
                return http.local_redirect('/web/login')
                ## return super(LoginHome, self).web_login(redirect, **kw)
        elif request.session.wx_user_info:  # 存在微信登录访问
            wx_user_info = request.session.wx_user_info
            wx_user_info['openid'] = wx_user_info['UserId']
            request.session.wx_user_info = wx_user_info
            # 查询当前微信号绑定的用户信息
            userinfo = request.env['wx.user.odoouser'].sudo().search([('openid', '=', wx_user_info['UserId'])])
            # 查询前面用户日否已存在
            userinfo_exist = request.env['res.users'].sudo().search([('wx_id', '=', wx_user_info['UserId'])])
            if 'login' in values:
                for user_e in userinfo_exist:  # 在用里面已存在微信登录
                    if user_e.login != kw.get('login') and kw.get('login'):
                        error_message = "微信账号%s(%s)已绑定账号%s(%s),请联系管理员。" % (
                            wx_user_info['UserId'], wx_user_info['nickname'], user_e.login, user_e.name)
                        error_str = "此微信已绑定账号%s(%s),请联系管理员。" % (user_e.name, user_e.login)
                        tracetype = request.env['wx.tracelog.type'].sudo().search([('code', '=', provider_id)])
                        if tracetype.exists():
                            request.env['wx.tracelog'].sudo().create({
                                "tracelog_type": tracetype.id,
                                "title": '登录出错%s' % error_message,
                                "user_id": userinfo.user_id.id if userinfo.user_id else None,
                                "wx_user_id": userinfo.wx_user_id.id if userinfo.wx_user_id else None
                            })
                        return werkzeug.utils.redirect('/web/login?error=%s' % error_str)
                userinfo_login = request.env['wx.user.odoouser'].sudo().search([('user_id.login', '=', kw['login'])])
                for user_l in userinfo_login:  # 检查用户否在其它微信登录
                    if user_l.openid != wx_user_info['UserId']:
                        error_message = "账号%s(%s)已在微信登录%s(%s),请先注销登录,如问题无法解决请联系管理员。" % (
                            kw['login'], user_l.user_id.name, user_l.openid,
                            user_l.wx_user_id.nickname if user_l.wx_user_id else '')
                        tracetype = request.env['wx.tracelog.type'].sudo().search([('code', '=', provider_id)])
                        if tracetype.exists():
                            request.env['wx.tracelog'].sudo().create({
                                "tracelog_type": tracetype.id,
                                "title": '登录出错%s' % error_message,
                                "user_id": userinfo.user_id.id if userinfo.user_id else None,
                                "wx_user_id": userinfo.wx_user_id.id if userinfo.wx_user_id else None
                            })
                        return werkzeug.utils.redirect('/web/login?error=%s' % error_message)

            if 'login' not in values or 'password' not in values:
                request.params['login_success'] = False
                return super(LoginHome, self).web_login(redirect, **kw)
            login_as = super(LoginHome, self).web_login(redirect, **kw)
            if 'error' in login_as.qcontext:
                return login_as
            logging.info("登录用户%s" % request.params['login'])
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                wx_user_info['user_id'] = uid
                wx_user_info['password'] = request.params['password']
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
                    odoouser = userinfo.write(wx_user_info)
                else:
                    wxuserinfo = request.env['wx.user'].sudo().search([('openid', '=', wx_user_info['UserId'])])
                    wx_user_info['wx_user_id'] = wxuserinfo.id
                    odoouser = request.env['wx.user.odoouser'].sudo().create(wx_user_info)
                    resuser = request.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
                    if resuser:
                        _data = client.get_img_data(str(wx_user_info['headimgurl']))
                        resuser.write({
                            "wx_user_id": wxuserinfo.id,
                            "wx_id": wx_user_info['UserId'],
                            "image": base64.b64encode(_data),
                        })
                        tracetype = request.env['wx.tracelog.type'].sudo().search([('code', '=', "login")])
                        if tracetype.exists():
                            request.env['wx.tracelog'].sudo().create({
                                "tracelog_type": tracetype.id,
                                "title": '通过微信登录',
                                "user_id": odoouser.user_id.id if odoouser.user_id else None,
                                "wx_user_id": odoouser.wx_user_id.id if odoouser.wx_user_id else None
                            })
                if redirect:
                    return http.local_redirect(redirect)
                else:
                    return http.local_redirect('/web#home')
        else:
            if kw.get('login') and kw.get('password'):
                userinfo = request.env['wx.user.odoouser'].sudo().search([('user_id.login', '=', kw['login'])])
                if userinfo.exists():
                    userinfo.write({'password': kw['password']})
        if is_wx_client and  kw.get('login') and kw.get('password'):
            return werkzeug.utils.redirect('/web/login?error=请从微信菜单发起登录')

        return super(LoginHome, self).web_login(redirect, **kw)

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        web_ = super(LoginHome, self).web_client(s_action, **kw)
        entry = client.wxenv(request.env)
        try:
            url_ = request.httprequest.url;
            url_ = url_.replace(":80", "")
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
        if wx_user_info:
            userinfo_all = request.env['wx.user.odoouser'].sudo().search(
                [('user_id', '=', uid), ('codetype', '=', wx_user_info['codetype'])])
            for userinfo in userinfo_all:
                tracetype = request.env['wx.tracelog.type'].sudo().search([('code', '=', 'logout')])
                if tracetype.exists():
                    request.env['wx.tracelog'].sudo().create({
                        "tracelog_type": tracetype.id,
                        "title": '退出登录%s' % wx_user_info['nickname'],
                        "user_id": userinfo.user_id.id if userinfo.user_id else None,
                        "wx_user_id": userinfo.wx_user_id.id if userinfo.wx_user_id else None
                    })
                userinfo.unlink()
                userinfo_exist = request.env['res.users'].sudo().search([('wx_id', '=', wx_user_info['UserId'])])
                for user_e in userinfo_exist:
                    user_e.write({
                        'wx_id': '',
                        'wx_user_id': None,
                    })

        return super(WxSession, self).logout(redirect)


# class DataSet(DataSet):
#     @http.route(['/web/dataset/call_kw', '/web/dataset/call_kw/<path:path>'], type='json', auth="user")
#     def call_kw(self, model, method, args, kwargs, path=None):
#         kw = super(DataSet, self).call_kw(model, method, args, kwargs, path)
#         return kw


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
    def mp_pt4mgexxx4zxjtpp(self, **kwargs):
        # response = http.send_file('MP_verify_xobfOnBKmFpc9HEU.txt')
        return 'PT4MgExxX4ZXjTpP'

    @http.route(['/MP_verify_lGcbHdpG5SNOx6tn.txt'], type='http', auth="public")
    def mp_lh(self, **kwargs):
        # response = http.send_file('MP_verify_xobfOnBKmFpc9HEU.txt')
        return 'lGcbHdpG5SNOx6tn'

    @http.route(['/MP_verify_6KqjIDY4BloxX3Vc.txt'], type='http', auth="public")
    def mp_kqjidy4bloxx3vc(self, **kwargs):
        # response = http.send_file('MP_verify_xobfOnBKmFpc9HEU.txt')
        return '6KqjIDY4BloxX3Vc'
