# coding=utf-8
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class WxUserUUID(models.Model):
    _name = 'wx.user.uuid'
    _description = u'公众号会话记录'

    openid = fields.Char('微信用户ID')
    uuid = fields.Char('会话ID')
    uuid_type = fields.Char('会话类型')
    last_uuid_time = fields.Datetime('会话ID时间')
    uuid_user_id = fields.Many2one('res.users', '会话用户', readonly=False)  # 用户ID
    wx_user_id = fields.Many2one('wx.user', '微信公众用户')
    partner_id = fields.Many2one('res.partner', string='客户')

    @api.multi
    def unlink(self):
        _logger.info('wx.corpuser unlink >>> %s' % str(self))
        for obj in self:
            wx_user_uuid = self.env['wx.user'].sudo().search([('last_uuid', '=', obj.uuid)], limit=1)
            if wx_user_uuid:
                wx_user_uuid.write({'last_uuid': '', 'last_uuid_time': fields.Datetime.now()})
        ret = super(WxUserUUID, self).unlink()
        return ret
