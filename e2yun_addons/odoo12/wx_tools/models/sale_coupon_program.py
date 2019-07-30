# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SaleCouponProgram(models.Model):
    _inherit = 'sale.coupon.program'

    qrcode_ticket = fields.Char(u'二维码ticket')
    qrcode_url = fields.Char(u'二维码url')
    qrcodeimg = fields.Html(compute='_get_qrcodeimg', string=u'二维码')

    @api.one
    def _get_qrcodeimg(self):
        if not self.qrcode_ticket:
            _logger.info("生成二维码%s" % self.name)
            from ..controllers import client
            entry = client.wxenv(self.env)
            qrcodedatastr = 'COUPON|%s|%s' % (self.id, self.name)
            qrcodedata = {"action_name": "QR_LIMIT_STR_SCENE","action_info": {"scene": {"scene_str": qrcodedatastr}}}
            qrcodeinfo = entry.wxclient.create_qrcode(qrcodedata)
            self.write({'qrcode_ticket': qrcodeinfo['ticket'],
                        'qrcode_url': qrcodeinfo['url']})
            self.qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                             'height="100px" />' % (qrcodeinfo['ticket'] or '/wx_tools/static/description/icon.png')
        else:
            self.qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                             'height="100px" />' % (self.qrcode_ticket or '/wx_tools/static/description/icon.png')
