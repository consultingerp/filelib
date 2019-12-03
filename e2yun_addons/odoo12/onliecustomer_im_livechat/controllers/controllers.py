# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo import models, fields, api
from odoo.http import request
import datetime
import logging

from odoo import http

_logger = logging.getLogger(__name__)


class OnliecustomerImLivechat(http.Controller):
    @http.route('/ordercontact/<int:order_id>', type='http', auth='public', website=True)
    def order_contact(self, order_id, **kwargs):
        # 根据服务团队ID
        order = request.env['sale.order'].browse(order_id)
        anonymous_name = None
        if request.session.geoip:
            anonymous_name = anonymous_name + " (" + request.requestsession.geoip.get('country_name', "") + ")"
        if request.session.uid:
            anonymous_name = request.env.user.name
        uuid_type = 'USER'
        partner = request.env.user.partner_id
        author = request.env['res.users'].sudo().browse(request.session.uid).partner_id
        content = '你好，%s发起订单咨询，订单编号%s，请处理订单。' % (anonymous_name, order.name)
        if order.partner_id.user_id:  # 当前用户存在导购 联系导购
            uuid_session = request.env['wx.user.uuid'].sudo().search(
                [('partner_id', '=', partner.id), ('uuid_type', '=', uuid_type)], limit=1)
        else:  # 联系客服
            uuid_type = 'service'
            uuid_session = request.env['wx.user.uuid'].sudo().search(
                [('partner_id', '=', partner.id), ('uuid_type', '=', uuid_type)], limit=1)
        if uuid_session.exists():  # 存在会话，在此会话上发送信息
            uuid = uuid_session['uuid']
            channel = request.env["mail.channel"].sudo().search([('uuid', '=', uuid)], limit=1)
            active_id = channel["id"]
        else:  # 不存在会话创建会话
            _logger.info('不存在会话创建会话')
            if order.partner_id.user_id:  # 直接联系导购
                partners_to = [order.partner_id.user_id.partner_id.id]  # 增加导购到会话
                session_info = request.env["mail.channel"].channel_get(partners_to)
            else:  # 联系客服
                wx_channel = request.env.ref('wx_tools.channel_wx')
                channel_id = wx_channel.id
                session_info = request.env["im_livechat.channel"].get_mail_channel(channel_id, anonymous_name)
                if not session_info:  # 看是否有在线客服
                    session_info = request.env["im_livechat.channel"].with_context(lang=False).get_online_mail_channel(channel_id, anonymous_name)
            if session_info:
                active_id = session_info["id"]
                uuid = session_info['uuid']
                request.env['wx.user.uuid'].sudo().create({
                    'openid': partner.wx_user_id.openid if partner.wx_user_id else None, 'uuid': uuid, 'last_uuid_time': fields.Datetime.now(),
                    'uuid_type': uuid_type, 'uuid_user_id': request.env.user.id, 'wx_user_id': partner.wx_user_id.id if partner.wx_user_id else None,
                    'partner_id': partner.id
                })
            channel = request.env["mail.channel"].sudo().search([('uuid', '=', uuid)], limit=1)
        message = channel.sudo().with_context(mail_create_nosubscribe=True). \
            message_post(author_id=author.id, email_from=False, body=content,
                         message_type='comment', subtype='mail.mt_comment', website_published=False)
        _logger.info("信息已发送%s" % message.id)
        channel_partner_name = channel.channel_partner_ids - author

        messagebody = '尊敬的%s您好，我是专属经理%s,您的订单%s，我们已收到，你有什么需要可直接联系我，我随时为您提供服务，谢谢。' % (anonymous_name, channel_partner_name.name,order.name)
        message = channel.sudo().with_context(mail_create_nosubscribe=True). \
            message_post(author_id=channel_partner_name.id, email_from=False,
                         body=messagebody,
                         message_type='comment', subtype='mail.mt_comment')

        wxuserinfo = request.env['wx.user'].sudo().search([('id', '=', channel_partner_name.wx_user_id.id)])
        channel_partner_name.wx_user_id.consultation_reminder(request.env.user.partner_id, wxuserinfo.openid,
                                                              content,
                                                              active_id, reminder_type='订单咨询')
        _logger.info("信息已发送%s" % message.id)
        request.session.helpdeskuuid = uuid
        action = request.env.ref('mail.action_discuss').id
        menu_id = request.env.ref('mail.menu_root_discuss').id
        url = '/web#action=%s&active_id=%s&menu_id=%s' % (action, active_id, menu_id)
        return http.local_redirect(url)
