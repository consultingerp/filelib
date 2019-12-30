# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class OlineShopResCompnay(models.Model):
    _inherit = 'res.company'

    display_show_area = fields.Boolean(string='显示地区')
    area_text_mate = fields.Char(string='地区匹配值')
    show_area_text = fields.Char(string='地区名称')
