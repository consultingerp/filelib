# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    vacation_status = fields.Boolean(string='Vacation status')
    gender = fields.Selection([('male','Male'),('female','Female')])
    function = fields.Selection([
        ('通用','通用'),
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


    @api.model
    def is_user_exist(self,login):
        sql = """select * from res_users where login = '"""+login+"""'"""
        self._cr.execute(sql)
        users = self.env.cr.dictfetchall()
        if users and len(users) > 0:
            return [users[0]['id']]
        else:
            return []

    @api.model_create_multi
    def create(self, vals_list):
        is_pos = False
        for vl in vals_list:
            if vl.get('pos_groups',False):
                pos_groups = vl.get('pos_groups')
                pos_groups.append(self.env.ref('base.group_user').id)
                vl['groups_id'] = pos_groups
                del vl['pos_groups']
            if vl.get('pos_flag',False):
                is_pos = True
                del vl['pos_flag']
                if vl.get('company_ids', False):
                    company_ids = vl.get('company_ids')
                    vl['company_ids'] = [(6,0,[company_ids,])]
        if is_pos:
            return super(ResUsers, self.sudo()).create(vals_list)

        return super(ResUsers, self).create(vals_list)

    @api.multi
    def write(self, vals):
        if vals.get('pos_groups',False):
            pos_groups =  vals.get('pos_groups')
            pos_groups.append(self.env.ref('base.group_user').id)
            pos_groups = [(6, 0, pos_groups)]
            vals['groups_id'] = pos_groups
            del vals['pos_groups']

        if vals.get('pos_flag', False):
            del vals['pos_flag']
            if vals.get('company_ids',False):
                company_ids = vals.get('company_ids')
                vals['company_ids'] = [(6,0,[company_ids,])]

            return super(ResUsers, self.sudo()).write(vals)
        else:
            return super(ResUsers, self).write(vals)