# coding=utf-8
import logging
import base64
from .. import client
from odoo import fields
import datetime
from odoo.http import request

_logger = logging.getLogger(__name__)


def main(robot):
    def get_img_data(pic_url):
        import requests
        headers = {
            'Accept': 'textml,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'Cache-Control': 'no-cache',
            'Host': 'mmbiz.qpic.cn',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }
        r = requests.get(pic_url, headers=headers, timeout=50)
        return r.content

    @robot.subscribe
    def subscribe(message):
        from .. import client
        entry = client.wxenv(request.env)
        serviceid = message.target
        openid = message.source
        _logger.info('>>> wx msg: %s' % message.__dict__)
        info = entry.wxclient.get_user_info(openid)
        info['group_id'] = str(info['groupid'])
        env = request.env()
        rs = env['wx.user'].sudo().search([('openid', '=', openid)])
        if not rs.exists():
            wxuserinfo = env['wx.user'].sudo().create(info)  # 创建微信用户。
            resuser = env['res.users'].sudo().search([('login', '=', info['openid'])])
            user_id = None
            defpassword = '123456'
            if message.EventKey:  # 如果关注的时候事有事件
                if entry.subscribe_auto_msg:
                    ret_msg = entry.subscribe_auto_msg
                else:
                    ret_msg = "您终于来了！欢迎关注"
                entry.send_text(openid, ret_msg)
                ret_msg = ''
                eventkey = message.EventKey.split('|')
                if eventkey[0] == 'qrscene_USERS':
                    _logger.info('USERS')
                    ret_msg = "您的客户经理：%s\n 欢迎咨询[玫瑰][玫瑰][玫瑰]" % (eventkey[3])
                    user_id = eventkey[1]
                elif eventkey[0] == 'qrscene_TEAM':
                    _logger.info('TEAM')
                    ret_msg = "门店：%s \n 欢迎咨询" % (eventkey[2])
            else:
                if entry.subscribe_auto_msg:
                    ret_msg = entry.subscribe_auto_msg
                else:
                    ret_msg = "您终于来了！欢迎关注"
            _data = get_img_data(str(info['headimgurl']))
            if not resuser.exists():
                resuser = env['res.users'].sudo().create({
                    "login": info['openid'],
                    "password": defpassword,
                    "name": info['nickname'],
                    "groups_id": request.env.ref('base.group_user'),  # base.group_public，base.group_portal
                    "wx_user_id": wxuserinfo.id,
                    "login_date": datetime.datetime.now(),
                    "image": base64.b64encode(_data)

                })
                resuser.partner_id.write({
                    'supplier': True,
                    'customer': True,
                    "wx_user_id": wxuserinfo.id,
                    "user_id": user_id,
                    "image": base64.b64encode(_data)
                })
                odoo_user = env['wx.user.odoouser'].sudo().search([('openid', '=', openid)])
                if not odoo_user.exists():
                    resuser = env['wx.user.odoouser'].sudo().create({
                        "openid": info['openid'],
                        "wx_user_id": wxuserinfo.id,
                        "password": defpassword,
                        "user_id": resuser.id,
                        "codetype": 'wx'
                    })

        return ret_msg

    @robot.unsubscribe
    def unsubscribe(message):

        serviceid = message.target
        openid = message.source
        env = request.env()
        rs = env['wx.user'].sudo().search([('openid', '=', openid)])
        if rs.exists():
            rs.unlink()
        odoouser = env['wx.user.odoouser'].sudo().search([('openid', '=', openid)])
        if odoouser.exists():
            odoouser.unlink()
        uuid = request.env['wx.user.uuid'].sudo().search([('openid', '=', openid)])
        if uuid.exists():
            uuid.unlink()

        return ""

    @robot.scan
    def scan(message):
        ret_msg = ""
        entry = client.wxenv(request.env)
        serviceid = message.target
        openid = message.source
        mtype = message.type
        _logger.info('>>> wx msg: %s' % message.__dict__)
        env = request.env()
        rs = env['wx.user'].sudo().search([('openid', '=', openid)])
        if rs.exists():
            eventkey = message.EventKey.split('|')
            if eventkey[0] == 'USERS':
                _logger.info('USERS')
                ret_msg = "您的客户经理：%s\n 欢迎咨询[玫瑰][玫瑰][玫瑰]" % (eventkey[3])
            elif eventkey[0] == 'TEAM':
                _logger.info('TEAM')
                ret_msg = "门店：%s \n 欢迎咨询" % (eventkey[2])
        return ret_msg

    @robot.scancode_push
    def scancode_push(message):
        _logger.info('>>> wx msg: %s' % message.__dict__)
        serviceid = message.target
        openid = message.source
        env = request.env()
        rs = env['wx.user'].sudo().search([('openid', '=', openid)])
        return ""

    @robot.scancode_waitmsg
    def scancode_waitmsg(message):
        _logger.info('>>> wx msg: %s' % message.__dict__)
        serviceid = message.target
        openid = message.source
        env = request.env()
        rs = env['wx.user'].sudo().search([('openid', '=', openid)])
        return ""

    @robot.view
    def url_view(message):
        print('obot.view---------%s' % message)
