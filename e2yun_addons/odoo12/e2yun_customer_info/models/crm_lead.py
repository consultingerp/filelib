# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)
from odoo.exceptions import UserError

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    parent_team_id = fields.Many2one(comodel_name='crm.team', string='Parent Team id',compute='_compute_parent_team_id', store=True, track_visibility='onchange')
    payment_team_id = fields.Many2one('crm.team', string='Delivery team', oldname='section_id', default=lambda self: self.env['crm.team'].sudo()._get_default_team_id(user_id=self.env.uid),
                                      index=True, track_visibility='onchange', help='When sending mails, the default email address is taken from the Sales Team.')
    parent_payment_team_id= fields.Many2one(comodel_name='crm.team', string='Delivery team L1',compute='_compute_parent_payment__team_id', store=True, track_visibility='onchange')
    sf_no = fields.Char('SF机会编号', track_visibility='onchange')

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
        return super(crm_lead, self).write(values)

    name = fields.Char(track_visibility='onchange')
    partner_id = fields.Many2one(track_visibility='onchange')
    date_action_last = fields.Datetime(track_visibility='onchange')
    website = fields.Char(track_visibility='onchange')
    type = fields.Selection(track_visibility='onchange')
    priority = fields.Selection(track_visibility='onchange')
    date_closed = fields.Datetime(track_visibility='onchange')
    date_open = fields.Datetime(track_visibility='onchange')
    date_last_stage_update = fields.Datetime(track_visibility='onchange')
    date_conversion = fields.Datetime(track_visibility='onchange')
    message_bounce = fields.Integer(track_visibility='onchange')

    probability = fields.Float(track_visibility='onchange')
    expected_revenue = fields.Monetary(track_visibility='onchange')
    date_deadline = fields.Date(track_visibility='onchange')
    color = fields.Integer(track_visibility='onchange')
    company_currency = fields.Many2one(track_visibility='onchange')
    user_email = fields.Char(track_visibility='onchange')
    user_login = fields.Char(track_visibility='onchange')

    street = fields.Char(track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    zip = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    state_id = fields.Many2one(track_visibility='onchange')
    country_id = fields.Many2one(track_visibility='onchange')
    mobile = fields.Char(track_visibility='onchange')
    function = fields.Char(track_visibility='onchange')
    title = fields.Many2one(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    meeting_count = fields.Integer(track_visibility='onchange')

    # x_studio_service_product = fields.Selection(track_visibility='onchange')
    # x_studio_proposal_type = fields.Selection(track_visibility='onchange')
    source_id = fields.Many2one(track_visibility='onchange')
    # x_studio_eatp = fields.Selection(track_visibility='onchange')
    rec_rev = fields.Selection(track_visibility='onchange')
    # x_studio_pre_sales_support = fields.Selection(track_visibility='onchange')
