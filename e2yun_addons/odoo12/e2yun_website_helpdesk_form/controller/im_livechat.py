# -*-coding:utf-8-*-

import base64
import odoo
import datetime

from odoo import http, _
from odoo.http import request
from odoo import models, fields, api
from odoo.addons.im_livechat.controllers.main import LivechatController


class LivechatController(LivechatController):

    @http.route('/im_livechat/loader/<int:channel_id>', type='http', auth='public')
    def loader(self, channel_id, **kwargs):
        # channel_id = 9
        reponse_website = super(LivechatController, self).loader(channel_id, **kwargs)
        return reponse_website

    @http.route('/im_livechat/user_helpdesk/<int:team_id>', type='http', auth='public')
    def user_helpdesk(self, team_id, **kwargs):
        # 根据服务团队ID
        team = request.env['helpdesk.team'].browse(team_id)
        tearm_feature = team.feature_livechat_channel_id
        channel_id = tearm_feature.id  # 团队在线客户ID
        # im_livechatchannel = request.env['im_livechat.channel'].sudo().browse(channel_id)
        author = request.env['res.users'].sudo().browse(request.session.uid).partner_id
        uuid = request.session.helpdeskuuid
        request_uid = request.session.uid
        anonymous_name = None
        if request.session.geoip:
            anonymous_name = anonymous_name + " (" + request.requestsession.geoip.get('country_name', "") + ")"
        if request.session.uid:
            anonymous_name = request.env.user.name
        helpdesk_useruuid = request.env['helpdesk.livechat.uuid'].sudo().search([('uuid_user_id', '=', request_uid), ('team_id', '=', team_id)], limit=1)
        if helpdesk_useruuid:  # 存在以前的对话UUID
            channel = helpdesk_useruuid.channel_id
            active_id = channel.id
            uuid = channel['uuid']
            helpdesk_useruuid.write({'last_uuid_time': fields.Datetime.now()})

        else:  # 创建新的会话
            if request.session.uid:
                session_info = request.env["im_livechat.channel"].with_context(lang=False).get_mail_channel(channel_id, anonymous_name)
                if session_info:  # 如果创建了session
                    uuid = session_info['uuid']
                else:
                    return request.render('e2yun_website_helpdesk_form.livechat_out')

            # localkwargs = {'weixin_id': 'web', 'wx_type': 'wx'}
            channel = request.env["mail.channel"].sudo().search([('uuid', '=', uuid)], limit=1)
            active_id = channel["id"]
            request.env['helpdesk.livechat.uuid'].sudo().create({
                'channel_id': session_info['id'], 'uuid': uuid, 'last_uuid_time': fields.Datetime.now(),
                'uuid_user_id': request_uid, 'anonymous_name': anonymous_name, 'team_id': team_id
            })
        userbody = '你好，%s发起售后咨询。' % anonymous_name
        message = channel.sudo().with_context(mail_create_nosubscribe=True). \
            message_post(author_id=author.id, email_from=False, body=userbody,
                         message_type='comment', subtype='mail.mt_comment', website_published=False)
        # _now = fields.datetime.now()
        # if _now - helpdesk_useruuid.last_uuid_time >= datetime.timedelta(seconds=5 * 60):
        channel_partner_name = channel.channel_partner_ids - author
        message = channel.sudo().with_context(mail_create_nosubscribe=True). \
            message_post(author_id=channel_partner_name.id, email_from=False,
                         body='尊敬的%s您好，我是售后服务经理%s，有任何问题都可以问我哦~' % (anonymous_name, channel_partner_name.name),
                         message_type='comment', subtype='mail.mt_comment')

        wxuserinfo = request.env['wx.user'].sudo().search([('id', '=', channel_partner_name.wx_user_id.id)])
        channel_partner_name.wx_user_id.consultation_reminder(request.env.user.partner_id, wxuserinfo.openid,
                                                              userbody,
                                                              active_id)

        request.session.helpdeskuuid = uuid
        action = request.env.ref('mail.action_discuss').id
        menu_id = request.env.ref('mail.menu_root_discuss').id
        url = '/web#action=%s&active_id=%s&menu_id=%s' % (action, active_id, menu_id)
        return http.local_redirect(url)

    @http.route('/im_livechat/user_rating/<int:res_id>', type='http', auth='public')
    def user_helpdesk(self, res_id, **kwargs):
        rating = request.env['rating.rating'].sudo().search([('res_id', '=', res_id)])
        if not rating:
            return request.not_found()
        lang = rating.partner_id.lang or 'en_US'
        helpdesk_ticket = request.env['helpdesk.ticket'].sudo().search([('id', '=', rating.res_id)])
        return request.env['ir.ui.view'].with_context(lang=lang).render_template('e2yun_website_helpdesk_form.user_rating', {
            'web_base_url': request.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            'rating': rating,
            'helpdesk_ticket': helpdesk_ticket
        })
