# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'
    qrcode_ticket = fields.Char(u'二维码ticket')
    qrcode_url = fields.Char(u'二维码url')
    qrcodeimg = fields.Html(compute='_get_qrcodeimg', string=u'对内二维码', help="对内二维码关注的时候不生成用户。")

    qrcode_ticket_external = fields.Char(u'二维码ticket')
    qrcode_url_external = fields.Char(u'二维码url')
    qrcodeimg_external = fields.Html(compute='_get_qrcodeimg_external', string=u'对外二维码', help="对外二维码，用户关注的时候生成用户。")

    @api.one
    def _get_qrcodeimg(self):
        if not self.qrcode_ticket:
            _logger.info("生成二维码")
            from ..controllers import client
            entry = client.wxenv(self.env)
            qrcodedatastr = 'COMPANY|%s|%s' % (self.id, self.name)
            qrcodedata = {"action_name": "QR_LIMIT_STR_SCENE",
                          "action_info": {"scene": {"scene_str": qrcodedatastr}}}
            qrcodeinfo = entry.wxclient.create_qrcode(qrcodedata)
            self.write({'qrcode_ticket': qrcodeinfo['ticket'],
                        'qrcode_url': qrcodeinfo['url']})
            self.qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                             'height="100px" />' % (qrcodeinfo['ticket'] or '/wx_tools/static/description/icon.png')
        else:
            self.qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                             'height="100px" />' % (self.qrcode_ticket or '/wx_tools/static/description/icon.png')

    @api.one
    def _get_qrcodeimg_external(self):
        if not self.qrcode_ticket_external:
            _logger.info("生成二维码%s" % self.name)
            from ..controllers import client
            entry = client.wxenv(self.env)
            qrcodedatastr = 'COMPANYEXTERNAL|%s|%s' % (self.id, self.name)
            # "expire_seconds": 2592000,
            qrcodedata = {"action_name": "QR_LIMIT_STR_SCENE",
                          "action_info": {"scene": {"scene_str": qrcodedatastr}}}
            qrcodeinfo = entry.wxclient.create_qrcode(qrcodedata)
            self.write({'qrcode_ticket_external': qrcodeinfo['ticket'],
                        'qrcode_url_external': qrcodeinfo['url']})
            self.qrcodeimg_external = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                                      'height="100px" />' % (
                                              qrcodeinfo['ticket'] or '/wx_tools/static/description/icon.png')
        else:
            self.qrcodeimg_external = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                                      'height="100px" />' % (
                                              self.qrcode_ticket or '/wx_tools/static/description/icon.png')
