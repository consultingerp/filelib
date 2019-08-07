# coding=utf-8
import base64
import datetime
import logging

import odoo
from odoo import _
from odoo.fields import Datetime
from odoo.http import request
from .. import client


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
        if messag_info == entry.wxclient.session.get(openid):     # entry.OPENID_LAST.get(openid):
            _logger.info('>>> 重复的微信消息')
            return ''
        # entry.OPENID_LAST[openid] = messag_info
        entry.wxclient.session.set(openid, messag_info);
        guideorreferrer = 'guide'
        max_goal_user = None  # 获取销售团队下面评分最高用户
        shop_code = None  # 门店
        rs = env['wx.user'].sudo().search([('openid', '=', openid)], limit=1)
        wxuserinfo = None
        scene_userinfo = None  # 被扫描人员
        company_id = None  # 公司ID
        guide = ["店长", "店员"]
        if not rs.exists():  # 不存在微信用户在
            wxuserinfo = env['wx.user'].sudo().create(info)  # 创建微信用户。
            resuser = env['res.users'].sudo().search([('login', '=', info['openid'])], limit=1)  # 查询登录名与微信名一样的
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
                befocus_username = ''
                eventkey = message.EventKey.split('|')
                if eventkey[0] == 'qrscene_USERS':
                    scene_userinfo = env['res.users'].sudo().search([('id', '=', int(eventkey[1]))], limit=1)
                    befocus_username = scene_userinfo.name
                    tracelog_type = 'qrscene_USERS'
                    _logger.info('USERS')
                    uuid_type = 'USER'
                    tracelog_title = "扫描用户%s关注,微信用户%s" % (befocus_username, str(info['nickname']))
                    ret_msg = "正在联系您的专属客户经理%s。\n" \
                              "请点击屏幕下方左侧小键盘打开对话框与您的客户经理联系。\n我们将竭诚为您服务，欢迎咨询！" % (befocus_username)
                    user_id = eventkey[1]
                    users_ids.append(user_id)
                    team_id = env['crm.team'].sudo().search([('member_ids', 'in', [int(eventkey[1])])], limit=1)
                    if team_id.exists():
                        shop_code = team_id.id
                    company_id = scene_userinfo.company_id.id
                elif eventkey[0] == 'qrscene_TEAM':
                    tracelog_type = 'qrscene_TEAM'
                    _logger.info('TEAM')
                    crm_team = env['crm.team'].sudo().search([('id', '=', int(eventkey[1]))], limit=1)
                    eventkey[2] = crm_team.name
                    tracelog_title = "扫描门店%s关注,微信用户%s" % (eventkey[2], str(info['nickname']))
                    ret_msg = "%s \n 欢迎您：我们将竭诚为您服务，欢迎咨询！" % (eventkey[2])
                    shop_code = eventkey[1]
                    max_goal_user = crm_team.tearm_high_goal()  # 获取销售团队下面评分最高用户
                    if max_goal_user:  # 需要联系门店的导购
                        users_ids.append(int(max_goal_user.user_id.id))
                        tracelog_title = '%s扫描门店二维码关注公众号，将客户分配给%s,根据评分规则,的团队评分(%s)，' % (
                            str(info['nickname']), max_goal_user.user_id.name, max_goal_user.current)
                        #traceuser_id = max_goal_user.user_id
                        user_id = max_goal_user.user_id.id
                        scene_userinfo = max_goal_user.user_id
                        ismail_channel = True
                        company_id = scene_userinfo.company_id.id
                elif eventkey[0] == 'qrscene_COMPANY':
                    company = env['res.company'].sudo().search([('id', '=', int(eventkey[1]))], limit=1)
                    eventkey[2] = company.name
                    tracelog_type = 'qrscene_COMPANY'
                    _logger.info('公司二维码进入')
                    iscompanyuser = True
                    tracelog_title = "扫描公司%s关注,微信用户%s" % (eventkey[2], str(info['nickname']))
                    ret_msg = "%s \n 欢迎您：我们将竭诚为您服务，欢迎咨询！" % (eventkey[2])
                    company_id = company.id
                elif eventkey[0] == 'qrscene_COMPANYEXTERNAL':
                    tracelog_type = 'qrscene_COMPANYEXTERNAL'
                    company = env['res.company'].sudo().search([('id', '=', int(eventkey[1]))], limit=1)
                    company_id = company.id
                    eventkey[2] = company.name
                    _logger.info('公司外部二维码进入')
                    tracelog_title = "扫描公司%s外部二维码关注,微信用户%s" % (eventkey[2], str(info['nickname']))
                    ret_msg = "%s \n 欢迎您：我们将竭诚为您服务，欢迎咨询！" % (eventkey[2])
            else:  # 没有带参数进入公众号
                if entry.subscribe_auto_msg:
                    ret_msg = entry.subscribe_auto_msg
                else:
                    ret_msg = "您终于来了！欢迎关注"
            _data = get_img_data(str(info['headimgurl']))
            if not company_id:
                company = env['res.company']._get_main_company();
                company_id = company.id
            if not iscompanyuser:
                if not resuser.exists():  # 如果用户不存在查询用户的微信字段以前有没有用，是不是从门店同步过来的
                    resuser = env['res.users'].sudo().search([('wx_id', '=', info['openid'])], limit=1)
                if not resuser.exists():  # 不存在odoo用户 而且不是扫描公司二给码进入的，公司二维码进不不用创建用户
                    resuser = env['res.users'].sudo().create({
                        "login": info['openid'],
                        "password": defpassword,
                        "name": info['nickname'],
                        "groups_id": request.env.ref('base.group_customer'),  # base.group_public，base.group_portal
                        "wx_user_id": wxuserinfo.id,
                        "login_date": datetime.datetime.now(),
                        "image": base64.b64encode(_data),
                        "email": 'HH',
                        "wx_id": info['openid'],
                        'company_ids': [(6, 0, [company_id])],
                        'company_id': company_id
                    })
                    res_guideorreferrer = env['res.users'].sudo().search([('id', '=', user_id)], limit=1)
                    if res_guideorreferrer.function in guide or max_goal_user:  # 导购 或者 排名导购
                        ismail_channel = True
                        guideorreferrer = 'guide'
                        resuser.partner_id.write({
                            'supplier': True,
                            'customer': True,
                            'shop_code': shop_code,
                            "wx_user_id": wxuserinfo.id,
                            "user_id": user_id if user_id else None,
                            "image": base64.b64encode(_data),
                            "customer_source": tracelog_type,
                            'related_guide': [(6, 0, users_ids)],
                            'company_id': company_id
                        })
                    elif tracelog_type == 'qrscene_USERS':  # 推荐人
                        guideorreferrer = 'referrer'
                        tracelog_title = "扫描推荐人%s关注,微信用户%s" % (befocus_username, str(info['nickname']))
                        ret_msg = "欢迎您%s：\n 我们将竭诚为您服务，欢迎咨询！" % str(info['nickname'])
                        resuser.partner_id.write({
                            'supplier': True,
                            'customer': True,
                            'shop_code': shop_code,
                            "wx_user_id": wxuserinfo.id,
                            "user_id": user_id if user_id else None,
                            "image": base64.b64encode(_data),
                            "customer_source": tracelog_type,
                            "referrer": user_id,
                            'company_id': company_id
                        })
                    else:
                        tracelog_title = "关注了公众号,微信用户%s" % (str(info['nickname']))
                        ret_msg = "欢迎您%s：\n 我们将竭诚为您服务，欢迎咨询！" % str(info['nickname'])
                        resuser.partner_id.write({
                            'supplier': True,
                            'customer': True,
                            'shop_code': shop_code,
                            "user_id": user_id if user_id else None,
                            "wx_user_id": wxuserinfo.id,
                            "image": base64.b64encode(_data),
                            "customer_source": tracelog_type,
                        })
                    traceuser_id = resuser
                else:  # 已存在odoo用户，关联用户到微信
                    traceuser_id = resuser  # 记录已存在有的ID
                    company_ids = resuser.company_ids.ids;
                    company_ids.append(company_id)
                    tracelog_title = tracelog_title + '已存在用户%s，重新关联微信用户%s' % (resuser.login, str(info['nickname']))
                    _logger.info('已存在用户，重新关联微信账号')
                    resuser.write({
                        "wx_user_id": wxuserinfo.id,
                        "image": base64.b64encode(_data),
                        "company_id":company_id,
                        'company_ids': [(6, 0, company_ids)],
                    })
                    res_guideorreferrer = env['res.users'].sudo().search([('id', '=', user_id)], limit=1)
                    if res_guideorreferrer.function in guide or max_goal_user:  # 导购 或者 排名导购
                        ismail_channel = True
                        guideorreferrer = 'guide'
                        resuser.partner_id.write({
                            'supplier': True,
                            'customer': True,
                            "wx_user_id": wxuserinfo.id,
                            "user_id": user_id,
                            "customer_source": tracelog_type,
                            "image": base64.b64encode(_data),
                            'related_guide': [(6, 0, users_ids)],
                            'company_id': company_id
                        })
                    elif tracelog_type == 'qrscene_USERS':  # 推荐人
                        guideorreferrer = 'referrer'
                        tracelog_title = "扫描推荐人%s关注,微信用户%s" % (befocus_username, str(info['nickname']))
                        ret_msg = "欢迎您%s：\n 我们将竭诚为您服务，欢迎咨询！" % str(info['nickname'])
                        resuser.partner_id.write({
                            'supplier': True,
                            'customer': True,
                            'shop_code': shop_code,
                            "wx_user_id": wxuserinfo.id,
                            "image": base64.b64encode(_data),
                            "customer_source": tracelog_type,
                            "referrer": user_id,
                            'company_id': company_id
                        })
                    else:
                        tracelog_title = "关注了公众号,微信用户%s" % (str(info['nickname']))
                        ret_msg = "欢迎您%s：\n 我们将竭诚为您服务，欢迎咨询！" % str(info['nickname'])
                        resuser.partner_id.write({
                            'supplier': True,
                            'customer': True,
                            'shop_code': shop_code,
                            "wx_user_id": wxuserinfo.id,
                            "image": base64.b64encode(_data),
                            "customer_source": tracelog_type,
                        })
                # 记录微信用户到 微信用户与odoo用户映射关系
                odoo_user = env['wx.user.odoouser'].sudo().search([('openid', '=', openid)], limit=1)
                if not odoo_user.exists():
                    resuser = env['wx.user.odoouser'].sudo().create({
                        "openid": info['openid'],
                        "wx_user_id": wxuserinfo.id,
                        "password": defpassword,
                        "user_id": resuser.id,
                        "codetype": 'wx'
                    })
            else:  # 公司用户不创建用户
                if resuser.exists():  # 如果是公司用户，找到同名微信用户也绑定用户。
                    resuser.write({
                        "wx_user_id": wxuserinfo.id,
                        "image": base64.b64encode(_data)
                    })
                else:
                    # 查询从门店同步过来的用户是否存在，存在自动绑定微信
                    resuser = env['res.users'].sudo().search([('wx_id', '=', info['openid'])], limit=1)
                    if resuser.exists():  # 如果是公司用户，找到同名微信用户也绑定用户。
                        resuser.write({
                            "wx_user_id": wxuserinfo.id,
                            "image": base64.b64encode(_data)
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
            if max_goal_user:
                origin_content = '%s扫描门店二维码关注公众号，根据评分规则,你的团队评分(%s)，将客户分配给您，点击连接直接发起会话。' % (
                    str(info['nickname']), max_goal_user.current)
                message_content = '%s扫描门店二维码关注公众号，根据评分规则,你的团队评分(%s)，将客户分配给您，现在您可以联系客户了。' % (
                    str(info['nickname']), max_goal_user.current)
                ret_goal_user_msg = "正在联系您的专属客户经理%s。" % (max_goal_user.user_id.name)
                entry.send_text(openid, ret_goal_user_msg)

            else:
                origin_content = '%s扫描二维码关注公众号，点击连接直接发起会话。' % (str(info['nickname']))
                message_content = '您好，%s通过扫描关注了公众号。' % (str(info['nickname']))
            if session_info:
                localkwargs = {'weixin_id': openid, 'wx_type': 'wx'}
                uuid = session_info['uuid']
                request_uid = request.session.uid or odoo.SUPERUSER_ID
                mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
                msg = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(
                    author_id=traceuser_id.partner_id.id, email_from=mail_channel.anonymous_name, body=message_content,
                    message_type='comment', subtype='mail.mt_comment', content_subtype='plaintext',
                    weixin_id=localkwargs)
                entry.create_uuid_for_openid(openid, uuid)
                wxuserinfo.update_last_uuid(uuid, traceuser_id.id if traceuser_id else None, uuid_type, wxuserinfo)
            active_id = session_info["id"]
            if traceuser_id.user_id.wx_user_id:  # 导购存在二维码
                wxuserinfo.consultation_reminder(traceuser_id.partner_id,
                                                 traceuser_id.user_id.wx_user_id.openid,
                                                 origin_content,
                                                 active_id)

        return ret_msg

    @robot.unsubscribe
    def unsubscribe(message):
        defpassword = '123456'
        tracelog_type = 'unsubscribe'
        tracelog_title = '取消关注公众号'
        entry = client.wxenv(request.env)
        serviceid = message.target
        openid = message.source
        env = request.env()
        messag_info = message.CreateTime + "" + message.FromUserName
        if messag_info == entry.wxclient.session.get(openid):  # entry.OPENID_LAST.get(openid):
            _logger.info('>>> 重复的微信消息')
            return ''
        entry.wxclient.session.set(openid, messag_info)
        info = entry.wxclient.get_user_info(openid)
        user = env['res.users'].sudo().search([('wx_user_id.openid', '=', openid)], limit=1)
        wx_user = env['wx.user'].sudo().search([('openid', '=', openid)], limit=1)
        odoouser = env['wx.user.odoouser'].sudo().search([('openid', '=', openid)], limit=1)
        uuid = request.env['wx.user.uuid'].sudo().search([('openid', '=', openid)])
        if user.exists():
            user.write({
                "wx_id": None,
                "password": defpassword
            })
        if wx_user.exists():
            wx_user.unlink()
        if odoouser.exists():
            tracetype = env['wx.tracelog.type'].sudo().search([('code', '=', tracelog_type)])
            if tracetype.exists():
                env['wx.tracelog'].sudo().create({
                    "tracelog_type": tracetype.id,
                    "title": tracelog_title,
                    "user_id": user.id,
                })
            odoouser.unlink()
        if uuid.exists():
            uuid.unlink()
        request.session.logout(keep_db=True)
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
        if messag_info == entry.wxclient.session.get(openid):  # entry.OPENID_LAST.get(openid):
            _logger.info('>>> 重复的微信消息')
            return ''
        # entry.OPENID_LAST[openid] = messag_info
        entry.wxclient.session.set(openid, messag_info);
        tracelog_type = 'subscribe'
        tracelog_title = '扫描进入公众号'
        traceuser_id = None
        ismail_channel = False
        uuid_type = None
        defpassword = "123456"
        guideorreferrer = 'guide'  # 导购或者推荐人
        max_goal_user = None  # 获取销售团队下面评分最高用户
        rs = env['wx.user'].sudo().search([('openid', '=', openid)])
        wx_user = None
        if rs.exists():
            wx_user = rs[0]
            eventkey = message.EventKey.split('|')
            resuser = env['res.users'].sudo().search([('login', '=', info['openid'])], limit=1)
            if not resuser.exists():  # 如果用户不存在查询绑定的微信
                resuser = env['res.users'].sudo().search([('wx_user_id.openid', '=', info['openid'])], limit=1)
            users_ids = resuser.partner_id.related_guide.ids
            befocus_username = ''
            company_id = None  # 公司ID
            if eventkey[0] == 'USERS':
                _logger.info('USERS')
                scene_userinfo = env['res.users'].sudo().search([('id', '=', int(eventkey[1]))], limit=1)
                befocus_username = scene_userinfo.name
                tracelog_type = 'qrscene_USERS'
                tracelog_title = "扫描用户%s进入微信公众号，微信用户%s" % (befocus_username, str(info['nickname']))
                ret_msg = "您好！正在联系您的专属客户经理：%s\n" % (befocus_username)
                user_id = eventkey[1]  # 客户经理
                res_guideorreferrer = env['res.users'].sudo().search([('id', '=', user_id)], limit=1)
                guide = ["店长", "店员"]
                if res_guideorreferrer.function in guide:  # 导购
                    users_ids.append(int(eventkey[1]))
                    guideorreferrer = 'guide'
                    uuid_type = 'USER'
                    ismail_channel = True
                    if resuser.exists():
                        traceuser_id = resuser
                        # 将客户公司归宿导购的公司
                        company_id = res_guideorreferrer.company_id.id
                        company_ids = resuser.company_ids.ids;
                        company_ids.append(company_id)
                        resuser.write({
                            "company_id": company_id,
                            'company_ids': [(6, 0, company_ids)],
                        })
                        resuser.partner_id.write({
                            "customer_source": tracelog_type,
                            "user_id": user_id,
                            'related_guide': [(6, 0, users_ids)]
                        })
                else:  # 推荐人
                    guideorreferrer = 'referrer'
                    ret_msg = "欢迎您%s：\n 我们将竭诚为您服务，欢迎咨询！" % str(info['nickname'])
                    tracelog_title = "扫描推荐人%s进入微信公众号，微信用户%s" % (befocus_username, str(info['nickname']))
                    _logger.info('推荐人%s' % user_id)
                    if resuser.exists():
                        resuser.partner_id.write({
                            "customer_source": tracelog_type,
                            "referrer": user_id if not resuser.partner_id.user_id else resuser.partner_id.user_id.id
                        })
            elif eventkey[0] == 'TEAM':
                tracelog_type = 'qrscene_TEAM'
                crm_team = env['crm.team'].sudo().search([('id', '=',  int(eventkey[1]))], limit=1)
                eventkey[2] = crm_team.name
                tracelog_title = "扫描门店%s进入公众号,微信用户%s" % (eventkey[2], str(info['nickname']))
                ret_msg = "%s 欢迎您：\n 我们将竭诚为您服务，欢迎咨询！" % (eventkey[2])

                max_goal_user = crm_team.tearm_high_goal()  # 获取销售团队下面评分最高用户
                users_ids.append(int(max_goal_user.user_id.id))
                if resuser.exists() and max_goal_user:
                    traceuser_id = resuser
                    ismail_channel = True
                    # # 将客户公司归宿导购的公司
                    # company_id = max_goal_user.user_id.company_id.id
                    # company_ids = resuser.company_ids.ids;
                    # company_ids.append(company_id)
                    # resuser.write({
                    #     "company_id": company_id,
                    #     'company_ids': [(6, 0, company_ids)],
                    # })
                    resuser.partner_id.write({
                        "customer_source": tracelog_type,
                        'user_id': resuser.partner_id.user_id.id if resuser.partner_id.user_id.id else max_goal_user.user_id.id,
                        'related_guide': [(6, 0, users_ids)]
                    })
                elif resuser.exists():
                    traceuser_id = resuser
                    resuser.partner_id.write({
                        "customer_source": tracelog_type,
                    })

                _logger.info('TEAM')
            elif eventkey[0] == 'COMPANY':
                tracelog_type = 'qrscene_COMPANY'
                company = env['res.company'].sudo().search([('id', '=',  int(eventkey[1]))], limit=1)
                eventkey[2] = company.name
                tracelog_title = "扫描公司%s二维码进入公众号,微信用户%s" % (eventkey[2], str(info['nickname']))
                _logger.info('TEAM')
                ret_msg = "%s欢迎您：\n 我们将竭诚为您服务，欢迎咨询！" % (eventkey[2])
                if resuser.exists():
                    traceuser_id = resuser
                    resuser.partner_id.write({
                        "customer_source": tracelog_type,
                    })
            elif eventkey[0] == 'COMPANYEXTERNAL':
                company = env['res.company'].sudo().search([('id', '=', int(eventkey[1]))], limit=1)
                eventkey[2] = company.name
                tracelog_type = 'qrscene_COMPANYEXTERNAL'
                tracelog_title = "扫描公司%sq外部二维码进入公众号,微信用户%s" % (eventkey[2], str(info['nickname']))
                _logger.info('TEAM')
                ret_msg = "%s欢迎您：\n 我们将竭诚为您服务，欢迎咨询！" % (eventkey[2])
                if resuser.exists():
                    traceuser_id = resuser
                    # 将客户公司归宿导购的公司
                    # company_id = company.id
                    # company_ids = resuser.company_ids.ids;
                    # company_ids.append(company_id)
                    # resuser.write({
                    #     'groups_id': [(4, request.env.ref('base.group_customer').id, False)],
                    #     'company_ids': [(4, company_id, False)],
                    #     "company_id": company_id,
                    # })
                    resuser.partner_id.write({
                        "customer_source": tracelog_type,
                    })
            elif eventkey[0] == 'RESPASSWORD':
                tracelog_type = 'qrscene_RESPASSWORD'
                tracelog_title = "扫描二维码找回密码,微信用户%s" % (str(info['nickname']))
                _logger.info('qrscene_RESPASSWORD')
                traceuser_id = resuser
                if resuser.exists() and resuser.wx_user_id:
                    resuser.action_wx_user_reset_password()
                else:
                    env['res.users'].wx_reset_password(user=None, openid=openid, nickname=str(info['nickname']))
                ret_msg = ""
            elif eventkey[0] == 'COUPON':
                tracelog_type = 'qrscene_COUPON'
                tracelog_title = "扫描二维码领取优惠券,微信用户%s" % (str(info['nickname']))
                _logger.info('qrscene_COUPON')
                traceuser_id = resuser
                if resuser.exists() and resuser.wx_user_id:
                    sale_coupon_program = env['sale.coupon.program'].sudo().search([('id', '=', eventkey[1])], limit=1)
                    vals = {'program_id': sale_coupon_program.id, 'partner_id': resuser.partner_id.id}
                    coupon_id = env['sale.coupon'].sudo().create(vals)

                ret_msg = _(
                    "优惠券领取成功\n优惠券金额：%s\n优惠券编号：%s" % (coupon_id.program_id.discount_fixed_amount, coupon_id.code))
        tracetype = env['wx.tracelog.type'].sudo().search([('code', '=', tracelog_type)])
        if tracetype.exists():
            env['wx.tracelog'].sudo().create({
                "tracelog_type": tracetype.id,
                "title": tracelog_title,
                "user_id": traceuser_id.id if traceuser_id else None,
                "wx_user_id": wx_user.id if wx_user else None
            })

        if ismail_channel:  # 联系客户 或者 取销售团队下面评分最高用户
            _logger.info('发起客户会话')
            oduserinfo = request.env['wx.user.odoouser'].sudo().search([('user_id', '=', traceuser_id.id)])
            if oduserinfo:  # 如果当前用户在微信中登录了
                uid = request.session.authenticate(request.session.db, traceuser_id.login, oduserinfo.password)
                partners_to = [traceuser_id.partner_id.user_id.partner_id.id]  # 增加导购到会话
                session_info = request.env["mail.channel"].channel_get(partners_to)
                if max_goal_user:
                    origin_content = '%s扫描门店二维码关注公众号，根据评分规则,你的团队评分(%s)，将客户分配给您，点击连接直接发起会话。' % (
                        str(info['nickname']), max_goal_user.current)
                    message_content = '%s扫描门店二维码关注公众号，根据评分规则,你的团队评分(%s)，将客户分配给您。' % (
                        str(info['nickname']), max_goal_user.current)
                else:
                    origin_content = '%s扫描二维码关注公众号，点击连接直接发起会话。' % (str(info['nickname']))
                    message_content = '您好，%s通过扫描关注了公众号。' % (str(info['nickname']))
                if session_info:
                    uuid = session_info['uuid']
                    localkwargs = {'weixin_id': openid, 'wx_type': 'wx'}
                    request_uid = request.session.uid or odoo.SUPERUSER_ID

                    mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
                    msg = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(
                        author_id=traceuser_id.partner_id.id, email_from=mail_channel.anonymous_name, body=message_content,
                        message_type='comment', subtype='mail.mt_comment', content_subtype='plaintext',
                        weixin_id=localkwargs)
                    entry.create_uuid_for_openid(openid, uuid)
                    wx_user.update_last_uuid(uuid, traceuser_id.id if traceuser_id else None, uuid_type, wx_user)
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
        entry = client.wxenv(request.env)
        serviceid = message.target
        openid = message.source
        mtype = message.type
        _logger.info('>>> wx msg: %s' % message.__dict__)
        env = request.env()
        info = entry.wxclient.get_user_info(openid)
        messag_info = message.CreateTime + "" + message.FromUserName
        if messag_info == entry.wxclient.session.get(openid):  # entry.OPENID_LAST.get(openid):
            _logger.info('>>> 重复的微信消息')
            return ''
        # entry.OPENID_LAST[openid] = messag_info
        entry.wxclient.session.set(openid, messag_info);
        serviceid = message.target
        openid = message.source
        env = request.env()
        user = env['res.users'].sudo().search([('wx_user_id.openid', '=', openid)], limit=1)
        collect_user_location = env['ir.config_parameter'].sudo().get_param('base_setup.collect_user_location')
        if collect_user_location:
            if user.exists():  # 存在用户更新用户关联客户
                user.partner_id.write({
                    'wxlatitude': message.latitude,
                    'wxlongitude': message.longitude,
                    'wxprecision': message.precision,
                    'location_write_date': Datetime.now()
                })
                user.setpartnerteamanduser(request,message.latitude,message.longitude)
        return ""

    @robot.view
    def url_view(message):
        print('obot.view---------%s' % message)
