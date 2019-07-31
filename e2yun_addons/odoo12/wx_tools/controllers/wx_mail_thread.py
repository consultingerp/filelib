# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
import os
import uuid
from datetime import datetime

from odoo import api, models
from odoo import exceptions
from odoo.modules.module import get_module_resource
from ..rpc import corp_client

_logger = logging.getLogger(__name__)


class WXMailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    @api.returns('self', lambda value: value.id)
    def message_post(self, body='', subject=None, message_type='notification', subtype=None, parent_id=False,
                     attachments=None, content_subtype='html', **kwargs):
        weixin_id = kwargs.get('weixin_id')
        message = super(WXMailThread, self).message_post(body=body, subject=subject, message_type=message_type,
                                                         subtype=subtype, parent_id=parent_id, attachments=attachments,
                                                         content_subtype=content_subtype, **kwargs)
        if not weixin_id:  # 不是发自来原微信的信息
            if hasattr(self, "anonymous_name"):  # self.anonymous_name:
                objs = self.env['wx.corpuser'].sudo().search([('userid', '=', self.anonymous_name)])
                if objs:  # 企业微信
                    _logger.info("wx.corpuser")
                    corp_client.send_message(self, self.anonymous_name, body)
                objs = self.env['wx.user'].sudo().search([('last_uuid', '=', self.uuid)])
                if objs:  # 公众号服务号
                    _logger.info("wx.user")
                    from ..controllers import client
                    entry = client.wxenv(self.env)
                    if message.attachment_ids:
                        wx_file_path = get_module_resource('wx_tools', 'static/wx')
                        wx_pic = os.path.join(wx_file_path, str(uuid.uuid4()) + message.attachment_ids.name)
                        with open(wx_pic, 'wb') as str2datas:
                            str2datas.write(base64.b64decode(message.attachment_ids.datas))
                        mimetype = message.attachment_ids.mimetype
                        if mimetype in ('image/jpeg', 'image/png', 'image/gif'):
                            with open(wx_pic, 'rb') as f:
                                r = entry.upload_media('image', f)
                                entry.send_image_message(objs.openid, r['media_id'])
                        elif mimetype in 'audio/mpeg' or message.attachment_ids.name.find('amr') >= 0:
                            with open(wx_pic, 'rb') as f:
                                r = entry.upload_media('voice', f)
                                entry.wxclient.send_voice_message(objs.openid, r['media_id'])
                        elif mimetype in 'audio/mpeg' or message.attachment_ids.name.find('mp4') >= 0:
                            with open(wx_pic, 'rb') as f:
                                r = entry.upload_media('video', f)
                                entry.wxclient.send_video_message(objs.openid, r['media_id'])
                        else:
                            _logger.info("附件不支持上传")
                            raise exceptions.UserError('发送微信信息不支持类型。只支持(PNG,JPEG,JPG,GIF,AMR,MP3,MP4)')
                        _logger.info("附件")
                    if body:
                        entry.send_text(objs.openid, body)
                    wxpartner = self.env['res.partner'].sudo().search([('wx_user_id.openid', '=', objs.openid)])
                    if wxpartner:
                        wx_attachment_ids = []
                        if message.attachment_ids.name:
                            attachment = self.env['ir.attachment'].sudo().create({
                                'name': '__wx_attachment|%s' % message.attachment_ids.name,
                                'datas': message.attachment_ids.datas,
                                'datas_fname': message.attachment_ids.datas_fname,
                                'res_model': 'res.partner',
                                'res_id': int(0)
                            })
                            wx_attachment_ids.append(attachment.id)
                        wxpartner.message_post(body=body, author_id=message.author_id.id,
                                               attachment_ids=wx_attachment_ids)

            for user in message.channel_ids.channel_partner_ids.ids:  # 消息发送来于chat
                _logger.info(user)
                if message.author_id.id == user:
                    continue
                partner = self.env['res.partner'].sudo().browse(user)
                if partner:
                    partner_weixin_id = partner.wxcorp_user_id.weixinid
                    if partner.wxcorp_user_id.weixinid and body:
                        corp_client.send_message(self, partner_weixin_id, body)
                _logger.info(partner)
                # self.ids   self.im_status  'offline'
            if hasattr(self, "wxcorp_user_id") and self.wxcorp_user_id.userid:
                corp_client.send_message(self, self.wxcorp_user_id.userid, body)
        if message.model == 'sale.order' and body:
            _logger.info('sale.order')
            for order in self:
                if order.state == 'draft':
                    continue
                to_wxid = None
                if message.author_id.id == self.partner_id.id:
                    to_wxid = order.create_uid  # 消息的作者是订单的供应商
                else:
                    to_wxid = self.partner_id
                title = '订单提醒'

                if to_wxid.wxcorp_user_id.userid:
                    date_ref = "收到新信息:" + body
                    data_body = "订单号:" + order.name
                    description = "<div class=\"gray\">" + date_ref + "</div> " \
                                                                      "<div class=\"normal\">" + data_body + "</div>" \
                                                                                                             "<div class=\"highlight\">" + \
                                  "时间:" + order.date_order + \
                                  "\n联系:" + message.author_id.name + "</div>"
                    url = corp_client.corpenv(
                        self.env).server_url + '/web/login?usercode=saleordermessage&codetype=corp&redirect=' + order.portal_url
                    url = corp_client.authorize_url(self, url, 'saleorder')
                    corp_client.send_text_card(self, to_wxid.wxcorp_user_id.userid, title, description, url, "详情")
                if to_wxid.wx_user_id.openid:
                    data = {
                        "first": {
                            "value": "收到新信息:" + body,
                            "color": "#173177"
                        },
                        "keyword1": {
                            "value": order.name
                        },
                        "keyword2": {
                            "value": message.author_id.name
                        }, "keyword3": {
                            "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            # "color": "#173177"
                        },
                        "remark": {
                            "value": "产品：" + '：'.join(order.order_line.mapped('product_id.display_name'))
                        }
                    }

                    template_id = ''
                    configer_para = self.env["wx.paraconfig"].sudo().search([('paraconfig_name', '=', '订单提醒')])
                    if configer_para:
                        template_id = configer_para[0].paraconfig_value
                    from ..controllers import client
                    url = client.wxenv(
                        self.env).server_url + '/web/login?usercode=saleorderwxmessage&codetype=wx&redirect=' + order.access_url
                    client.send_template_message(self, to_wxid.wx_user_id.openid, template_id, data, url,
                                                 'saleorder')
        if message.model == 'purchase.order' and body:
            _logger.info('purchase.order')
            for order in self:
                if order.state == 'draft':
                    continue
                to_wxid = None
                if message.author_id.id == self.partner_id.id:
                    to_wxid = order.create_uid  # 消息的作者是订单的供应商
                else:
                    to_wxid = self.partner_id
                title = '采购订单提醒'
                date_ref = "收到采购订单新信息:" + body
                data_body = "订单号:" + order.name
                description = "<div class=\"gray\">" + date_ref + "</div> " \
                                                                  "<div class=\"normal\">" + data_body + "</div>" \
                                                                                                         "<div class=\"highlight\">" + \
                              "时间:" + order.date_order + \
                              "\n联系:" + message.author_id.name + "</div>"
                if order.partner_id.wxcorp_user_id.userid:
                    url = corp_client.corpenv(
                        self.env).server_url + '/web/login?usercode=purchaseordermessage&codetype=corp&redirect=' + order.website_url
                    url = corp_client.authorize_url(self, url, 'saleorder')
                    corp_client.send_text_card(self, self.partner_id.wxcorp_user_id.userid, title, description,
                                               url, "详情")
                if order.partner_id.wx_user_id.openid:
                    data = {
                        "first": {
                            "value": "收到采购订单新信息:" + body,
                            "color": "#173177"
                        },
                        "keyword1": {
                            "value": order.name
                        },
                        "keyword2": {
                            "value": message.author_id.name
                        }, "keyword3": {
                            "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        },
                        "remark": {
                            "value": "产品：" + '：'.join(order.order_line.mapped('product_id.display_name'))
                        }
                    }
                    template_id = ''
                    configer_para = self.env["wx.paraconfig"].sudo().search([('paraconfig_name', '=', '订单提醒')])
                    if configer_para:
                        template_id = configer_para[0].paraconfig_value
                    from ..controllers import client
                    url = client.wxenv(
                        self.env).server_url + '/web/login?usercode=purchaseorderwxmessage&codetype=wx&redirect=' + order.website_url
                    client.send_template_message(self, self.partner_id.wx_user_id.openid, template_id, data,
                                                 url,
                                                 'saleorder')
        return message
