# -*-coding:utf-8-*-
import datetime
import logging
from datetime import timedelta
from ..controllers import client

from odoo.addons.auth_signup.models.res_partner import now

import odoo
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.fields import Datetime

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
            from ..controllers import client
            entry = client.wxenv(self.env)
            qrcodedatastr = 'USERS|%s|%s|%s|' % (self.id, self.login, self.name)
            _logger.info("生成二维码%s" % qrcodedatastr)
            # "expire_seconds": 2592000,
            if len(qrcodedatastr) > 30:
                qrcodedatastr = qrcodedatastr[:30]
            qrcodedata = {"action_name": "QR_LIMIT_STR_SCENE", "action_info": {"scene": {"scene_str": qrcodedatastr}}}
            try:
                qrcodeinfo = entry.wxclient.create_qrcode(qrcodedata)
                self.write({'qrcode_ticket': qrcodeinfo['ticket'],
                            'qrcode_url': qrcodeinfo['url']})
                self.qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                                 'height="100px" />' % (qrcodeinfo['ticket'] or '/wx_tools/static/description/icon.png')
            except Exception as e:
                _logger.error("生成二维码失败：%s" % e)
        else:
            self.qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                             'height="100px" />' % (self.qrcode_ticket or '/wx_tools/static/description/icon.png')

    @api.multi
    def get_jsapi_ticket(self, url):
        try:
            url_ = url;
            url_ = url_.replace(":80", "")
            from ..controllers import client
            entry = client.wxenv(self.env)
            wx_appid, timestamp, noncestr, signature = entry.get_jsapi_ticket(url_)
        except Exception as e:
            _logger.error("加载微信jsapi_ticket错误。%s" % e)
        return {
            'wx_appid': wx_appid,
            'timestamp': timestamp,
            'noncestr': noncestr,
            'signature': signature
        }

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
                self.wx_reset_password(user)
                # template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)

    @api.model
    def wx_reset_password(self, user=None, openid=None, nickname=None):
        if not user:
            first = "查询微信未绑定内部用户，不能重置密码。"
            keyword1 = nickname
            remark = "查询微信未绑定内部用户，不能重置密码，可以点击连接直接登录，"
            url = '/web/login'
        else:
            first = "用户密码重置"
            keyword1 = user.display_name
            remark = "点击此信息重置密码"
            url = '/web/reset_password?token=%s' % self.signup_token
        data = {
            "first": {
                "value": first,
                "color": "#173177"
            },
            "keyword1": {
                "value": keyword1
            },
            "keyword2": {
                "value": (datetime.datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            },
            "remark": {
                "value": remark,
                "color": "#FF0000"
            }
        }

        self.env['wx.user'].send_template_message(data, user=user, template_name='密码重置提醒', url=url,
                                                  usercode='RESPASSWORD', url_type='out', openid=openid)

    @api.multi
    def setpartnerteamanduser(self, request, latitude, longitude):
        users_ids = []
        entry = client.wxenv(request.env)
        if not self.function:  # 岗位为空为客户
            if not self.partner_id.user_id:  # 不存在导购
                team = self.env['crm.team'].getrecenttearm(latitude, longitude)
                if team:
                    max_goal_user = team.tearm_high_goal()  # 获取销售团队下面评分最高用户
                    if max_goal_user:
                        tracelog_type = 'location_allocation'
                        tracelog_title = '%s客户没有关联门店,根据位置分配最近门店，将客户分配给%s,根据评分规则,的团队评分(%s)，' % (
                            self.wx_user_id.nickname, max_goal_user.user_id.name, max_goal_user.current)
                        origin_content = tracelog_title
                        users_ids.append(max_goal_user.user_id.id)
                        self.partner_id.write({
                            "user_id": max_goal_user.user_id.id,
                            'shop_code': team.id,
                            'related_guide': [(6, 0, users_ids)],
                            'wxlatitude': latitude,
                            'wxlongitude': longitude,
                            'wxprecision': '-1',
                            'location_write_date': Datetime.now()
                        })
                        self.env.cr.commit()
                        tracetype = self.env['wx.tracelog.type'].sudo().search([('code', '=', tracelog_type)])
                        if tracetype.exists():
                            self.env['wx.tracelog'].sudo().create({
                                "tracelog_type": tracetype.id,
                                "title": tracelog_title,
                                "user_id": self.id,
                                "wx_user_id": self.wx_user_id.id
                            })
                        oduserinfo = request.env['wx.user.odoouser'].sudo().search([('user_id', '=', self.id)])
                        wx_user = oduserinfo.wx_user_id
                        uid = request.session.authenticate(request.session.db, self.login, oduserinfo.password)
                        partners_to = [max_goal_user.user_id.partner_id.id]  # 增加导购到会话
                        session_info = request.env["mail.channel"].channel_get(partners_to)
                        traceuser_id = max_goal_user.user_id
                        if session_info:
                            ret_msg = "正在联系您的专属客户经理%s。\n" \
                                      "请点击屏幕下方左侧小键盘打开对话框与您的客户经理联系。\n我们将竭诚为您服务，欢迎咨询！" % max_goal_user.user_id.name
                            entry.send_text(wx_user.openid, ret_msg)
                            uuid = session_info['uuid']
                            localkwargs = {'weixin_id': self.wx_user_id.openid, 'wx_type': 'wx'}
                            request_uid = request.session.uid or odoo.SUPERUSER_ID
                            mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)],
                                                                                                limit=1)
                            msg = mail_channel.sudo(request_uid).with_context(
                                mail_create_nosubscribe=True).message_post(
                                author_id=traceuser_id.partner_id.id, email_from=mail_channel.anonymous_name,
                                body=origin_content,
                                message_type='comment', subtype='mail.mt_comment', content_subtype='plaintext',
                                weixin_id=localkwargs)
                            uuid_type = 'USER'
                            entry.create_uuid_for_openid(self.wx_user_id.openid, uuid)
                            wx_user.update_last_uuid(uuid, traceuser_id.id if traceuser_id else None, uuid_type,
                                                     wx_user)
                        active_id = session_info["id"]
                        if traceuser_id.wx_user_id:  # 导购存在二维码
                            wx_user.consultation_reminder(traceuser_id.partner_id,
                                                          traceuser_id.wx_user_id.openid,
                                                          origin_content,
                                                          active_id)
                    else:
                        self.writepartner_id(latitude, longitude)
                else:  # 存在导购
                    self.writepartner_id(latitude, longitude)
            else:  # 存在导购 更新信息
                self.writepartner_id(latitude, longitude)
        else:  # self.function:
            self.writepartner_id(latitude, longitude)

    @api.model
    def writepartner_id(self, latitude, longitude):
        self.partner_id.write({
            'wxlatitude': latitude,
            'wxlongitude': longitude,
            'wxprecision': '-1',
            'location_write_date': Datetime.now()
        })


class ChangePasswordUser(models.TransientModel):
    _inherit = 'change.password.user'

    @api.multi
    def change_password_button(self):
        for line in self:
            wxobj = self.env['wx.user.odoouser'].sudo().search([('user_id', '=', line.user_id.id)])
            if wxobj.exists():
                wxobj.write({'password': line.new_passwd})
        return super(ChangePasswordUser, self).change_password_button()
