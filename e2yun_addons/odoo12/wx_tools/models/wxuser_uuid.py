# coding=utf-8

from odoo import models, fields, api


class WxUserUUID(models.Model):
    _name = 'wx.user.uuid'
    _description = u'公众号会话记录'

    openid = fields.Char('微信用户ID')
    uuid = fields.Char('会话ID')
    uuid_type = fields.Char('会话类型')
    last_uuid_time = fields.Datetime('会话ID时间')
    uuid_user_id = fields.Many2one('res.users', readonly=False)  # 用户ID

