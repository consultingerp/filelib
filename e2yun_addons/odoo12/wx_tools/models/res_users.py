# -*-coding:utf-8-*-
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class WxResUsers(models.Model):
    _inherit = 'res.users'

    wx_user_id = fields.Many2one('wx.user', '微信公众用户')
    qrcode_ticket = fields.Char(u'二维码ticket')
    qrcode_url = fields.Char(u'二维码url')
    qrcodeimg = fields.Html(compute='_get_qrcodeimg', string=u'二维码')

    # @api.multi
    # def _compute_im_status(self):
    #     super(WxResUsers, self)._compute_im_status()

    @api.one
    def _get_qrcodeimg(self):
        if not self.qrcode_ticket:
            _logger.info("生成二维码")
            from ..controllers import client
            entry = client.wxenv(self.env)
            qrcodedatastr = 'USERS|%s|%s|%s|'%(self.id,self.login,self.name)
            qrcodedata = {"expire_seconds": 2592000, "action_name": "QR_STR_SCENE",
                          "action_info": {"scene": {"scene_str": qrcodedatastr}}}
            qrcodeinfo = entry.wxclient.create_qrcode(qrcodedata)
            self.write({'qrcode_ticket': qrcodeinfo['ticket'],
                        'qrcode_url': qrcodeinfo['url']})
            self.qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                             'height="100px" />' % (qrcodeinfo['ticket'] or '/wx_tools/static/description/icon.png')
        else:
            self.qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                             'height="100px" />' % (self.qrcode_ticket or '/wx_tools/static/description/icon.png')
