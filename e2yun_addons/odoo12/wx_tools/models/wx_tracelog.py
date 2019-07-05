# -*-coding:utf-8-*-

from odoo import models, fields, api


class WXTracelogtype(models.Model):
    _name = 'wx.tracelog.type'
    _description = u'跟踪类型'

    code = fields.Char(u'类型', )
    name = fields.Char(u'显示名称', )


class WXTracelog(models.Model):
    _name = 'wx.tracelog'
    _description = u'微信跟踪记录'

    tracelog_type = fields.Many2one('wx.tracelog.type', '跟踪类型')
    title = fields.Char(string='记录', store=True)
    user_id = fields.Many2one('res.users', string='用户', readonly=False)  # 用户ID
    wx_user_id = fields.Many2one('wx.user', '微信公众用户')

