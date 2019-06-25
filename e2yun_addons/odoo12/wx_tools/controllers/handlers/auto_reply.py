# coding=utf-8
import re
import logging
import base64
import os
import datetime
from odoo import fields


from odoo.http import request
import odoo
from .. import client

_logger = logging.getLogger(__name__)


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


def main(robot):
    def input_handle(message, session):
        _logger.info(message)
        from .. import client
        entry = client.wxenv(request.env)
        client = entry
        serviceid = message.target
        openid = message.source
        mtype = message.type
        _logger.info('>>> wx msg: %s' % message.__dict__)
        if message.message_id == entry.OPENID_LAST.get(openid):
            _logger.info('>>> 重复的微信消息')
            return ''
        entry.OPENID_LAST[openid] = message.message_id
        origin_content = ''
        attachment_ids = []
        if mtype == 'image':
            pic_url = message.img
            media_id = message.__dict__.get('MediaId', '')
            _logger.info(pic_url)
            _data = get_img_data(pic_url)
            _filename = datetime.datetime.now().strftime("%m%d%H%M%S") + os.path.basename(pic_url)
            attachment = request.env['ir.attachment'].sudo().create({
                'name': '__wx_image|%s' % media_id,
                'datas': base64.encodestring(_data),
                'datas_fname': _filename,
                'res_model': 'mail.compose.message',
                'res_id': int(0)
            })
            attachment_ids.append(attachment.id)
        elif mtype in ['voice']:
            media_id = message.media_id
            media_format = message.format
            r = client.wxclient.download_media(media_id)
            _filename = '%s.%s' % (media_id, media_format)
            _data = r.content
            attachment = request.env['ir.attachment'].sudo().create({
                'name': '__wx_voice|%s' % message.media_id,
                'datas': base64.encodestring(_data),
                'datas_fname': _filename,
                'res_model': 'mail.compose.message',
                'res_id': int(0)
            })
            attachment_ids.append(attachment.id)
        elif mtype == 'location':
            origin_content = '对方发送位置: %s 纬度为：%s 经度为：%s' % (message.label, message.location[0], message.location[1])
        elif mtype == 'text':
            origin_content = message.content

        content = origin_content.lower()
        wxuserinfo = request.env()['wx.autoreply'].sudo().search([])
        for rc in wxuserinfo:
            _key = rc.key.lower()
            if rc.type == 1:
                if content == _key:
                    ret_msg = rc.action.get_wx_reply()
                    return ret_msg
            elif rc.type == 2:
                if _key in content:
                    ret_msg = rc.action.get_wx_reply()
                    return ret_msg
            elif rc.type == 3:
                try:
                    flag = re.compile(_key).match(content)
                except:
                    flag = False
                if flag:
                    ret_msg = rc.action.get_wx_reply()
                    return ret_msg

        partner = request.env['res.partner'].sudo().search([('wx_user_id.openid', '=', openid)])
        partner_user_id = None
        if partner.exists():
            if partner[0].user_id:  # 存在导购
                partner_user_id = partner[0].user_id  # 联系当前导购

        # 客服对话 uuid:对话UUID
        # uuid, record_uuid = entry.get_uuid_from_openid(openid)
        ret_msg = ''
        cr, uid, context, db = request.cr, request.uid or odoo.SUPERUSER_ID, request.context, request.db
        uuid = ''  # 获取上次连接会话
        wxuserinfo = request.env['wx.user'].sudo().search([('openid', '=', openid)])
        if not wxuserinfo.exists():
            info = client.wxclient.get_user_info(openid)  # 获取用户信息
            info['group_id'] = ''
            wx_user = request.env['wx.user'].sudo().create(info)
        else:
            wx_user = wxuserinfo[0]
        wxuseruuid = request.env['wx.user'].sudo().search([('openid', '=', openid)])
        if wxuseruuid:
            channel = request.env['mail.channel'].sudo().search([('uuid', '=', wxuseruuid.last_uuid)])
            if channel.exists():
                uuid = wxuseruuid.last_uuid
        uuid_type = None
        if partner_user_id and uuid:  # 需要联系客服要 存在上次会话
            _logger.info('需要联系客服要 存在上次会话')
            # 查询上次会话是否是用户类型
            uuid_type = 'USER'
            uuid_session = request.env['wx.user.uuid'].sudo().search(
                [('uuid', '=', uuid), ('uuid_type', '=', uuid_type)], limit=1)
            if uuid_session.exists():
                _now = fields.datetime.now()
                if _now - uuid_session.last_uuid_time >= datetime.timedelta(seconds=30 * 60):
                    entry.send_text(openid, "正在联系你的专属客户经理%s，请稍等[咖啡][咖啡] " % (partner_user_id.name))
            else:  # 如果不满足条件重新选择发起会话
                uuid = None
        if partner_user_id and not uuid:
            _logger.info('需要联系客服要 没有会话')
            entry.send_text(openid, "正在联系你的专属客户经理%s，请稍等[咖啡][咖啡] " % (partner_user_id.name))
        if not uuid:  # 没有会话创建会话
            anonymous_name = wx_user.nickname
            if not partner_user_id:  # 联系在线客户
                channel = request.env.ref('wx_tools.channel_wx')
                channel_id = channel.id
                # 创建一个channel
                session_info, ret_msg = request.env["im_livechat.channel"].create_mail_channel(channel_id,
                                                                                               anonymous_name,
                                                                                               content)
            else:  # 联系客户经理
                _logger.info('需要联系客服要，创建新的会话')
                obj = request.env['wx.user.odoouser'].sudo().search([('openid', '=', openid)])
                uid = request.session.authenticate(request.session.db, obj.user_id.login, obj.password)
                # partners_to = [partner_user_id.partner_id.id, partner.id]
                partners_to = [partner_user_id.partner_id.id]
                # session_info = request.env["mail.channel"].create_user(partners_to);
                session_info = request.env["mail.channel"].channel_get(partners_to);
                _logger.info('需要联系客服要，创建新的会话')
            if session_info:
                uuid = session_info['uuid']
                entry.create_uuid_for_openid(openid, uuid)
                # if not record_uuid:
                wx_user.update_last_uuid(uuid, partner_user_id.id if partner_user_id else None, uuid_type)

        if uuid:
            consultation_reminder(request, partner_user_id.partner_id.wx_user_id.openid, origin_content, 60)
            wx_user.update_last_uuid(uuid, partner_user_id.id if partner_user_id else None, uuid_type)
            localkwargs = {'weixin_id': openid, 'wx_type': 'wx'}
            message_type = "message"
            message_content = origin_content
            request_uid = request.session.uid or odoo.SUPERUSER_ID
            author_id = False  # message_post accept 'False' author_id, but not 'None'
            author = request.env['res.partner'].sudo().search([('wx_user_id.openid', '=', openid)])
            if author:
                author_id = author.id
            else:
                pater_id = request.env['res.partner'].sudo().search([('wx_user_id.openid', '=', openid)])
                if pater_id:
                    author = request.env['res.users'].sudo().search([('partner_id', '=', pater_id.id)])
                    author_id = author.id
            if request.session.uid:
                author_id = request.env['res.users'].sudo().browse(request.session.uid).partner_id.id
            mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
            msg = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(
                author_id=author_id, email_from=mail_channel.anonymous_name, body=message_content,
                message_type='comment', subtype='mail.mt_comment', content_subtype='plaintext',
                attachment_ids=attachment_ids, weixin_id=localkwargs)
        if ret_msg:
            return ret_msg

    def consultation_reminder(self, openid, message, active_id):
        data = {
            "first": {
                "value": "客户咨询服务提醒",
                "color": "#173177"
            },
            "keyword1": {
                "value": '微信客户'
            },
            "keyword2": {
                "value": '微信客户'
            }, "keyword3": {
                "value": '公众号'
            }, "keyword4": {
                "value": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            "remark": {
                "value": "信息：" + message
            }
        }
        template_id = 'mZMBZn7KcAtNiRYMUYa0GTnO_zZBAdtb5aCJp8wVgqU'
        url = client.wxenv(
            self.env).server_url + '/web/login?usercode=message&codetype=wx&' \
                                   'redirect=/web#action=94&active_id=%s&menu_id=75' % (active_id)
        client.send_template_message(self, openid, template_id, data, url, 'message')
        return True

    robot.add_handler(input_handle, type='text')
    robot.add_handler(input_handle, type='image')
    robot.add_handler(input_handle, type='voice')
    robot.add_handler(input_handle, type='location')
