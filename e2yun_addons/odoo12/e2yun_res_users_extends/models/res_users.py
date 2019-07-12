# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    vacation_status = fields.Boolean(string='Vacation status')
    gender = fields.Selection([('male','Male'),('female','Female')])
    function = fields.Selection([
        ('店长','店长'),
        ('店员','店员'),
        ('司机','司机'),
        ('库工','库工'),
        ('内勤','内勤'),
        ('采购','采购'),
        ('送货员','送货员'),
        ('安装员','安装员'),
        ('片区长','片区长'),
        ('备用一','备用一'),
        ('备用二','备用二'),
        ('备用三','备用三'),
        ('备用四','备用四'),
        ('备用五','备用五'),
        ('回访专员','回访专员'),
        ('公司设计师','公司设计师')
         ],'Operating Post')
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


