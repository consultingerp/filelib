# -*- coding: utf-8 -*-
import logging
import os
import base64
from odoo import models, fields, api
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auth_signup_reset_password_qrcode_ticket = fields.Char(u'二维码ticket')
    auth_signup_reset_password_qrcode_url = fields.Char(u'二维码url')
    auth_signup_reset_password_qrcodeimg = fields.Html(compute='_get_qrcodeimg', string=u'二维码')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update({
            'auth_signup_reset_password_qrcodeimg': '%s' % params.get_param('auth_signup_reset_password_qrcodeimg'),
        })
        return res

    @api.one
    def _get_qrcodeimg(self):
        if not self.auth_signup_reset_password_qrcode_ticket:
            _logger.info("生成二维码")
            from ..controllers import client
            entry = client.wxenv(self.env)
            qrcodedatastr = 'RESPASSWORD|%s|%s' % (self.company_id.id, self.company_id.name)
            qrcodedata = {"expire_seconds": 2592000, "action_name": "QR_STR_SCENE",
                          "action_info": {"scene": {"scene_str": qrcodedatastr}}}
            qrcodeinfo = entry.wxclient.create_qrcode(qrcodedata)
            self.write({'auth_signup_reset_password_qrcode_ticket': qrcodeinfo['ticket'],
                        'auth_signup_reset_password_qrcode_url': qrcodeinfo['url']})
            self.auth_signup_reset_password_qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s' \
                                                        ' width="100px" height="100px" />' % (qrcodeinfo['ticket'])
            Param = self.env["ir.config_parameter"].sudo()

            Param.set_param('auth_signup_reset_password_qrcodeimg', self.auth_signup_reset_password_qrcodeimg)
            Param.set_param('auth_signup_reset_password_qrcode_ticket',
                            'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s' % qrcodeinfo['ticket'])
        else:
            self.qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                             'height="100px" />' % (self.qrcode_ticket or '/wx_tools/static/description/icon.png')
