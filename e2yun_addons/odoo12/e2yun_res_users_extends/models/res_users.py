# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    vacation_status = fields.Boolean(string='Vacation status')
    gender = fields.Selection([('male','Male'),('female','Female')])
    function = fields.Char('Operating Post')
    wx_id = fields.Char('WeChat ID')

    @api.model_create_multi
    def create(self, vals_list):
        for vl in vals_list:
            if vl.get('pos_groups'):
                pos_groups = vl.get('pos_groups')
                pos_groups.append(self.env.ref('base.group_user').id)
                vl['groups_id'] = pos_groups
                del vl['pos_groups']

        return super(ResUsers, self).create(vals_list)

    @api.multi
    def write(self, vals):
        if vals.get('pos_groups'):
            pos_groups =  vals.get('pos_groups')
            pos_groups.append(self.env.ref('base.group_user').id)
            pos_groups = [(6, 0, pos_groups)]
            vals['groups_id'] = pos_groups
            del vals['pos_groups']
        ret = super(ResUsers, self).write(vals)
        return ret


