# coding=utf-8
import logging
import base64
from .. import client
from odoo import fields
import datetime
import odoo
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
        tracelog_type = 'subscribe'
        tracelog_title = '关注公众号'
        traceuser_id = None
        ismail_channel = False
        uuid_type = None
        env = request.env()
        # FromUserName + CreateTime
        messag_info = message.CreateTime + "" + message.FromUserName
        if messag_info == entry.OPENID_LAST.get(openid):
            _logger.info('>>> 重复的微信消息')
            return ''
        entry.OPENID_LAST[openid] = messag_info
        rs = env['wx.user'].sudo().search([('openid', '=', openid)])
        if not rs.exists():  # 不存在微信用户在
            wxuserinfo = env['wx.user'].sudo().create(info)  # 创建微信用户。
            resuser = env['res.users'].sudo().search([('login', '=', info['openid'])])
            user_id = None
            defpassword = '123456'
            iscompanyuser = False
            users_ids = []
            if message.EventKey:  # 如果关注的时候事有事件
                if entry.subscribe_auto_msg:
                    ret_msg = entry.subscribe_auto_msg
                else:
                    ret_msg = "您终于来了！欢迎关注"
                entry.send_text(openid, ret_msg)
                ret_msg = ''
                eventkey = message.EventKey.split('|')
                if eventkey[0] == 'qrscene_USERS':
                    tracelog_type = 'qrscene_USERS'
                    _logger.info('USERS')
                    uuid_type = 'USER'
                    tracelog_title = "扫描用户%s关注,微信用户%s" % (eventkey[3], str(info['nickname']))
                    ret_msg = "正在联系您的专属客户经理%s。\n" \
                              "请点击屏幕下方左侧小键盘打开对话框与您的客户经理联系。\n我们将竭诚为您服务，欢迎咨询！" % (eventkey[3])
                    user_id = eventkey[1]
                    users_ids.append(user_id)
                    ismail_channel = True
                elif eventkey[0] == 'qrscene_TEAM':
                    tracelog_type = 'qrscene_TEAM'
                    _logger.info('TEAM')
                    tracelog_title = "扫描门店%s关注,微信用户%s" % (eventkey[2] , str(info['nickname']))
                    ret_msg = "%s \n 欢迎您：我们将竭诚为您服务，欢迎咨询！" % (eventkey[2])
                elif eventkey[0] == 'qrscene_COMPANY':
                    tracelog_type = 'qrscene_COMPANY'
                    _logger.info('公司二维码进入')
                    iscompanyuser = True
                    tracelog_title = "扫描公司%s关注,微信用户%s" % (eventkey[2] , str(info['nickname']))
                    ret_msg = "%s \n 欢迎您：我们将竭诚为您服务，欢迎咨询！" % (eventkey[2])
            else:
                if entry.subscribe_auto_msg:
                    ret_msg = entry.subscribe_auto_msg
                else:
                    ret_msg = "您终于来了！欢迎关注"
            _data = get_img_data(str(info['headimgurl']))
            if not iscompanyuser:
                # if not resuser.exists():  # 如果用户不存在查询绑定的微信
                #     resuser = env['res.users'].sudo().search([('wx_user_id.openid', '=', info['openid'])], limit=1)
                if not resuser.exists() :  # 不存在odoo用户 而且不是扫描公司二给码进入的，公司二维码进不不用创建用户
                    resuser = env['res.users'].sudo().create({
                        "login": info['openid'],
                        "password": defpassword,
                        "name": info['nickname'],
                        "groups_id": request.env.ref('base.group_user'),  # base.group_public，base.group_portal
                        "wx_user_id": wxuserinfo.id,
                        "login_date": datetime.datetime.now(),
                        "image": base64.b64encode(_data),
                        "email": info['openid'],
                        "wx_id": info['openid']
                    })
                    resuser.partner_id.write({
                        'supplier': True,
                        'customer': True,
                        "wx_user_id": wxuserinfo.id,
                        "user_id": user_id,
                        "image": base64.b64encode(_data),
                        "customer_source": tracelog_type,
                        'related_guide': [(6, 0, users_ids)]
                    })
                    traceuser_id = resuser
                else:  # 已存在odoo用户，关联用户到微信
                    traceuser_id = resuser  # 记录已存在有的ID
                    tracelog_title = tracelog_title + '已存在用户%s，重新关联微信用户%s' % (resuser.login, str(info['nickname']))
                    _logger.info('已存在用户，重新关联微信账号')
                    resuser.write({
                        "wx_user_id": wxuserinfo.id,
                        "image": base64.b64encode(_data)
                    })
                    resuser.partner_id.write({
                        'supplier': True,
                        'customer': True,
                        "wx_user_id": wxuserinfo.id,
                        "user_id": user_id,
                        "customer_source": tracelog_type,
                        "image": base64.b64encode(_data),
                        'related_guide': [(6, 0, users_ids)]
                    })
                # 记录微信用户到 微信用户与odoo用户映射关系
                odoo_user = env['wx.user.odoouser'].sudo().search([('openid', '=', openid)])
                if not odoo_user.exists():
                    resuser = env['wx.user.odoouser'].sudo().create({
                        "openid": info['openid'],
                        "wx_user_id": wxuserinfo.id,
                        "password": defpassword,
                        "user_id": resuser.id,
                        "codetype": 'wx'
                    })
        else:  # '已存微信用户，重新进入'
            _logger.info('已存微信用户，重新进入')
        tracetype = env['wx.tracelog.type'].sudo().search([('code', '=', tracelog_type)])
        if tracetype.exists():
            env['wx.tracelog'].sudo().create({
                "tracelog_type": tracetype.id,
                "title": tracelog_title,
                "user_id": traceuser_id.id if traceuser_id else None,
                "wx_user_id": wxuserinfo.id if wxuserinfo else None
            })
        env.cr.commit()
        if ismail_channel:  # 联系客户
            _logger.info('发起客户会话')
            uid = request.session.authenticate(request.session.db, traceuser_id.login, defpassword)
            partners_to = [traceuser_id.partner_id.user_id.partner_id.id]  # 增加导购到会话
            session_info = request.env["mail.channel"].channel_get(partners_to)
            origin_content = '%s扫描二维码关注公众号，点击连接直接发起会话。'% (str(info['nickname']))
            if session_info:
                localkwargs = {'weixin_id': openid, 'wx_type': 'wx'}
                uuid = session_info['uuid']
                request_uid = request.session.uid or odoo.SUPERUSER_ID
                message_content = '您好，%s通过扫描关注了公众号。'% (str(info['nickname']))
                mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
                msg = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(
                    author_id=traceuser_id.partner_id.id, email_from=mail_channel.anonymous_name, body=message_content,
                    message_type='comment', subtype='mail.mt_comment', content_subtype='plaintext',
                    weixin_id=localkwargs)
                entry.create_uuid_for_openid(openid, uuid)
                wxuserinfo.update_last_uuid(uuid, traceuser_id.id if traceuser_id else None, uuid_type,wxuserinfo)
            active_id = session_info["id"]
            if traceuser_id.user_id.wx_user_id:  # 导购存在二维码
                wxuserinfo.consultation_reminder(traceuser_id.partner_id,
                                                 traceuser_id.user_id.wx_user_id.openid,
                                                 origin_content,
                                                 active_id)

        return ret_msg

    @robot.unsubscribe
    def unsubscribe(message):
        tracelog_type = 'unsubscribe'
        tracelog_title = '取消关注公众号'
        entry = client.wxenv(request.env)
        serviceid = message.target
        openid = message.source
        env = request.env()
        info = entry.wxclient.get_user_info(openid)
        user = env['res.users'].sudo().search([('wx_user_id.openid', '=', openid)])
        rs = env['wx.user'].sudo().search([('openid', '=', openid)])
        if rs.exists():
            rs.unlink()
        odoouser = env['wx.user.odoouser'].sudo().search([('openid', '=', openid)])
        if odoouser.exists():
            tracetype = env['wx.tracelog.type'].sudo().search([('code', '=', tracelog_type)])
            if tracetype.exists():
                env['wx.tracelog'].sudo().create({
                    "tracelog_type": tracetype.id,
                    "title": tracelog_title,
                    "user_id": user.id,
                })
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
        info = entry.wxclient.get_user_info(openid)
        messag_info = message.CreateTime + "" + message.FromUserName
        if messag_info == entry.OPENID_LAST.get(openid):
            _logger.info('>>> 重复的微信消息')
            return ''
        entry.OPENID_LAST[openid] = messag_info

        tracelog_type = 'subscribe'
        tracelog_title = '扫描进入公众号'
        traceuser_id = None
        ismail_channel = False
        uuid_type = None
        defpassword = "123456"
        rs = env['wx.user'].sudo().search([('openid', '=', openid)])
        if rs.exists():
            wx_user = rs[0]
            eventkey = message.EventKey.split('|')
            resuser = env['res.users'].sudo().search([('login', '=', info['openid'])], limit=1)
            if not resuser.exists():  # 如果用户不存在查询绑定的微信
                resuser = env['res.users'].sudo().search([('wx_user_id.openid', '=', info['openid'])], limit=1)
            users_ids = resuser.partner_id.related_guide.ids
            if eventkey[0] == 'USERS':
                _logger.info('USERS')
                tracelog_type = 'qrscene_USERS'
                tracelog_title = "扫描用户%s进入微信公众号，微信用户%s" % (eventkey[3], str(info['nickname']))
                ret_msg = "您好！正在联系您的专属客户经理：%s\n" % (eventkey[3])
                ismail_channel = True
                user_id = eventkey[1]
                users_ids.append(int(eventkey[1]))
                uuid_type = 'USER'
                if resuser.exists():
                    traceuser_id = resuser
                    resuser.partner_id.write({
                        "customer_source": tracelog_type,
                        "user_id": user_id,
                        'related_guide': [(6, 0, users_ids)]
                    })
            elif eventkey[0] == 'TEAM':
                tracelog_type = 'qrscene_TEAM'
                tracelog_title = "扫描门店%s进入公众号,微信用户%s" % (eventkey[2], str(info['nickname']))
                _logger.info('TEAM')
                ret_msg = "%s 欢迎您：\n 我们将竭诚为您服务，欢迎咨询！" % (eventkey[2])
                if resuser.exists():
                    traceuser_id = resuser
                    resuser.partner_id.write({
                        "customer_source": tracelog_type,
                    })
            elif eventkey[0] == 'COMPANY':
                tracelog_type = 'qrscene_COMPANY'
                tracelog_title = "扫描公司%s二维码进入公众号,微信用户%s" % (eventkey[2], str(info['nickname']))
                _logger.info('TEAM')
                ret_msg = "%s欢迎您：\n 我们将竭诚为您服务，欢迎咨询！" % (eventkey[2])
                if resuser.exists():
                    traceuser_id = resuser
                    resuser.partner_id.write({
                        "customer_source": tracelog_type,
                    })
            elif eventkey[0] == 'RESPASSWORD':
                tracelog_type = 'qrscene_RESPASSWORD'
                tracelog_title = "扫描二维码找回密码,微信用户%s" % ( str(info['nickname']))
                _logger.info('qrscene_RESPASSWORD')
                traceuser_id = resuser
                resuser.action_wx_user_reset_password()
                ret_msg = ""
        tracetype = env['wx.tracelog.type'].sudo().search([('code', '=', tracelog_type)])
        if tracetype.exists():
            env['wx.tracelog'].sudo().create({
                "tracelog_type": tracetype.id,
                "title": tracelog_title,
                "user_id": traceuser_id.id if traceuser_id else None,
                "wx_user_id": wx_user.id if wx_user else None
            })

        if ismail_channel:  # 联系客户
            _logger.info('发起客户会话')
            oduserinfo = request.env['wx.user.odoouser'].sudo().search([('user_id', '=', traceuser_id.id)])
            uid = request.session.authenticate(request.session.db, traceuser_id.login, oduserinfo.password)
            partners_to = [traceuser_id.partner_id.user_id.partner_id.id]  # 增加导购到会话
            session_info = request.env["mail.channel"].channel_get(partners_to)
            origin_content = '%s扫描二维码关注公众号，点击连接直接发起会话。' % (str(info['nickname']))
            if session_info:
                uuid = session_info['uuid']
                localkwargs = {'weixin_id': openid, 'wx_type': 'wx'}
                request_uid = request.session.uid or odoo.SUPERUSER_ID
                message_content = '您好，%s通过扫描关注了公众号。'% (str(info['nickname']))
                mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
                msg = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(
                    author_id=traceuser_id.partner_id.id, email_from=mail_channel.anonymous_name, body=message_content,
                    message_type='comment', subtype='mail.mt_comment', content_subtype='plaintext',
                    weixin_id=localkwargs)
                entry.create_uuid_for_openid(openid, uuid)
                wx_user.update_last_uuid(uuid, traceuser_id.id if traceuser_id else None, uuid_type,wx_user)
            active_id = session_info["id"]
            if traceuser_id.user_id.wx_user_id:  # 导购存在二维码
                wx_user.consultation_reminder(traceuser_id.partner_id,
                                              traceuser_id.user_id.wx_user_id.openid,
                                              origin_content,
                                              active_id)

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

    @robot.location_event
    def location_event(message):
        _logger.info('>>>location_event wx msg: %s' % message.__dict__)
        serviceid = message.target
        openid = message.source
        env = request.env()
        rs = env['wx.user'].sudo().search([('openid', '=', openid)])
        return ""



    @robot.view
    def url_view(message):
        print('obot.view---------%s' % message)
