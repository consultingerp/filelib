# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)
from odoo.exceptions import UserError

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    parent_team_id = fields.Many2one(comodel_name='crm.team', string='Parent Team id',compute='_compute_parent_team_id', store=True)
    payment_team_id = fields.Many2one('crm.team', string='Delivery team', oldname='section_id', default=lambda self: self.env['crm.team'].sudo()._get_default_team_id(user_id=self.env.uid),
        index=True, track_visibility='onchange', help='When sending mails, the default email address is taken from the Sales Team.')
    parent_payment_team_id= fields.Many2one(comodel_name='crm.team', string='Delivery team L1',compute='_compute_parent_payment__team_id', store=True)

    @api.one
    @api.depends('team_id')
    def _compute_parent_team_id(self):
        self.parent_team_id = self.team_id.parent_id.id

    @api.one
    @api.depends('payment_team_id')
    def _compute_parent_payment__team_id(self):
        self.parent_payment_team_id = self.payment_team_id.parent_id.id

    @api.multi
    def write(self, values):
        #读取按钮权限组s
       groups_id=self.env.ref('e2yun_customer_info.groups_lead_stage_id_update').id
       sql='SELECT * from res_groups_users_rel where gid=%s and uid=%s'
       self._cr.execute(sql, (groups_id,self._uid,))
       groups_users=self._cr.fetchone()

       #状态 4 和 8 时 无法更新数据
       if self.stage_id.id==4 and not groups_users:
           raise UserError('当前状态下无法操作更新，请联系管理员')
       res = super(crm_lead, self).write(values)