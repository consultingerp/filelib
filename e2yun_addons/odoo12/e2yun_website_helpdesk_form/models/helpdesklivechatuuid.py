# coding=utf-8

from odoo import models, fields


class HeldeskLivechatuuid(models.Model):
    _name = 'helpdesk.livechat.uuid'
    _description = u'服务订单用户会话ID'

    uuid = fields.Char('会话ID')
    channel_id = fields.Many2one('mail.channel', readonly=False)  #
    last_uuid_time = fields.Datetime('会话ID时间')
    uuid_user_id = fields.Many2one('res.users', readonly=False)  # 用户ID
    anonymous_name = fields.Char('anonymous_name')
    team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team', index=True)
