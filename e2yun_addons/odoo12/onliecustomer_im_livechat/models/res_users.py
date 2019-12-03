# -*-coding:utf-8-*-
import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class OnlieLivechatResUsers(models.Model):
    _inherit = 'res.users'

    is_defaultlivechat = fields.Boolean(
        string='设置为主要认员',
        help="当客服不在线的时候，发送信息到些用户")
