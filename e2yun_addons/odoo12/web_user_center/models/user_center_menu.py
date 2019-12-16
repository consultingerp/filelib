# -*- coding: utf-8 -*-

import inspect
import logging
import hashlib
import re

from werkzeug import urls
from werkzeug.exceptions import NotFound

from odoo import api, fields, models, tools

from odoo.tools import pycompat
from odoo.http import request
from odoo.osv import expression
from odoo.osv.expression import FALSE_DOMAIN
from odoo.tools.translate import _

logger = logging.getLogger(__name__)


class UserCenterMenu(models.Model):
    _name = "usercenter.menu"
    _description = "个人中心菜单"

    _order = "sequence, id"

    def _default_sequence(self):
        menu = self.search([('display_Position', '=', self.display_Position)], limit=1, order="sequence DESC")
        return menu.sequence + 1 or 0

    name = fields.Char('名称', required=True)
    title = fields.Char('描述', default='')
    key_word = fields.Char('关键字', default='')
    url = fields.Char('URL', default='')
    new_window = fields.Boolean('新窗口')
    sequence = fields.Integer(default=_default_sequence, string='排序')
    display_Position = fields.Selection([('top', '顶部'), ('footer', '底部'), ('one', '第一行'), ('two', '第二行'), ('list', '列表')], default='list', string='显示位置')
    is_visible = fields.Boolean(string='是否显示', default=True)
    is_divHeight = fields.Boolean(string='分格显示')
    sys_menu = fields.Many2one('ir.ui.menu', string='关联系统菜单')
    web_icon_data = fields.Binary(string='图标', attachment=True)
    code = fields.Text(string='Python Code', groups='base.group_system',
                       help="Write Python code that the action will execute. Some variables are "
                            "available for use; help about python expression is given in the help tab.")
    groups_id = fields.Many2many('res.groups', 'ir_ui_menu_group_rel',
                                 'menu_id', 'gid', string='Groups',
                                 help="If you have groups, the visibility of this menu will be based on these groups. " \
                                      "If this field is empty, Odoo will compute visibility based on the related object's read access.")

    @api.onchange('display_Position')
    def _onchange_action(self):
        menu = self.search([('display_Position', '=', self.display_Position)], limit=1, order="sequence DESC")
        self.sequence = menu.sequence + 1 or 0
