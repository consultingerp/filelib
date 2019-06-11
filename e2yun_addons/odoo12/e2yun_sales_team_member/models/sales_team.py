# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,api

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.onchange('member_ids')
    def onchange_member(self):
        msg = ''
        for user in self.member_ids:
            sql = """select sale_team_id from res_users where id = %s """
            self._cr.execute(sql,(user.id,))
            st_id = self._cr.fetchone()
            if st_id and st_id[0] and st_id[0] != self._origin.id:
                old_team_name = self.browse(st_id[0]).name
                msg = msg + '用户 ' + user.name + ' 从 ' + old_team_name + ' 销售团队\n'

        if msg:
            msg = msg + '更新到当前销售团队'
            return {
                'warning': {
                    'title': '提示',
                    'message':msg
                }
            }