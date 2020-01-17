import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    button_right_name = fields.Char('添加购物车按钮右侧按钮名称', config_parameter='online_shop_setup.button_right_name')