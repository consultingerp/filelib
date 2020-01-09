# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    authority_group_control = fields.Boolean('权限组控制',default=False)

class ResGroups(models.Model):
    _inherit = 'res.groups'

    authority_group_control = fields.Boolean('权限组控制',default=False)


    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.authority_group_control:
            args = args + [('authority_group_control','=',True)]
            
        return super(ResGroups, self).search(args, offset=offset, limit=limit, order=order, count=count)

