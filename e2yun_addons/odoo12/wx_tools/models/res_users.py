# -*-coding:utf-8-*-
import logging
import datetime
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_partner import now

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

    @api.multi
    def write(self, vals):
        partner = super(WxResUsers, self).write(vals)
        if vals.get('wx_user_id') and self.partner_id.wx_user_id.id != vals.get('wx_user_id'):
            self.partner_id.wx_user_id = vals.get('wx_user_id')
            self.wx_id = self.partner_id.wx_user_id.openid
        return partner

    @api.one
    def _get_qrcodeimg(self):
        if not self.qrcode_ticket:
            _logger.info("生成二维码")
            from ..controllers import client
            entry = client.wxenv(self.env)
            qrcodedatastr = 'USERS|%s|%s|%s|' % (self.id, self.login, self.name)
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

    @api.model
    def change_password(self, old_passwd, new_passwd):
        if new_passwd:
            wxobj = self.env['wx.user.odoouser'].sudo().search([('user_id', '=', self.env.user.id)])
            if wxobj.exists():
                wxobj.write({'password': new_passwd})
        return super(WxResUsers, self).change_password(old_passwd, new_passwd)

    @api.multi
    def action_wx_user_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)

        for user in self:
            with self.env.cr.savepoint():
                if not user.wx_user_id:
                    raise UserError("用户没有绑定微信，不能发送微信重置密码")
                logging.info("密码重置OK.")
                data = {
                    "first": {
                        "value": "用户密码重置",
                        "color": "#173177"
                    },
                    "keyword1": {
                        "value": user.login
                    },
                    "keyword2": {
                        "value": (datetime.datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                    },
                    "remark": {
                        "value": "点击此信息重置密码"
                    }
                }
                url = '/web/reset_password?token=%s' % self.signup_token
                self.env['wx.user'].send_template_message(data, user=user, template_name='密码重置提醒', url=url,
                                                          usercode='RESPASSWORD')
                #template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)


class ChangePasswordUser(models.TransientModel):
    _inherit = 'change.password.user'

    @api.multi
    def change_password_button(self):
        for line in self:
            wxobj = self.env['wx.user.odoouser'].sudo().search([('user_id', '=', line.user_id.id)])
            if wxobj.exists():
                wxobj.write({'password': line.new_passwd})
        return super(ChangePasswordUser, self).change_password_button()
