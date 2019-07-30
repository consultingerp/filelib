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
    obtain_location = fields.Boolean(string="获取用户位置", config_parameter='base_setup.obtain_location')
    collect_user_location = fields.Boolean(string="允许收集用户位置", config_parameter='base_setup.collect_user_location')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update({
            'auth_signup_reset_password_qrcodeimg': '%s' % params.get_param('auth_signup_reset_password_qrcodeimg')

        })
        return res

    def qrcode_rest(self):
        crm_team_pool = self.env['crm.team'].search([])
        for crm_team in crm_team_pool:
            crm_team.write({
                'longitude': 0.0,
                'longitude': 0.0,
                'qrcode_ticket': ''
            });
        crm_team_pool = self.env['crm.team'].search_read([])

        res_users_pool = self.env['res.users'].search([])
        for res_users in res_users_pool:
            res_users.write({
                'qrcode_ticket': '',
            });
        res_users_pool = self.env['res.users'].search_read([])

        res_company_pool = self.env['res.company'].search([])
        for res_company in res_company_pool:
            res_company.write({
                'qrcode_ticket': '',
                'qrcode_ticket_external': '',
            });
        res_users_pool = self.env['res.company'].search_read([])

        sale_coupon_pool = self.env['sale.coupon.program'].search([])
        for sale_coupon in sale_coupon_pool:
            sale_coupon.write({
                'qrcode_ticket': ''
            });
        return {
            'warning': {
                'title': 'Tips',
                'message': '更新成功'
            }
        }

    @api.one
    def _get_qrcodeimg(self):
        if not self.auth_signup_reset_password_qrcode_ticket:
            _logger.info("生成二维码%s" % self.company_id.name)
            from ..controllers import client
            entry = client.wxenv(self.env)
            qrcodedatastr = 'RESPASSWORD|%s|%s' % (self.company_id.id, self.company_id.name)
            qrcodedata = {"action_name": "QR_LIMIT_STR_SCENE",
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
