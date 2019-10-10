# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import logging

logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    parent_team_id = fields.Many2one(comodel_name='crm.team', compute='_compute_parent_team_id', store=True)
    real_create_uid = fields.Many2one('res.users', string='Real Create User', help='Real Create User Info.')

    @api.one
    @api.depends('team_id')
    def _compute_parent_team_id(self):
        self.parent_team_id = self.team_id.parent_id.id

    @api.model
    def create(self, vals):
        if 'customer' in vals and vals['customer'] and ('parent_id' not in vals or vals['parent_id'] is False) and self.env.ref(
                'e2yun_customer_info.group_crm_sale') in self.env.user.groups_id:
            raise exceptions.Warning(_('You can not craete customer!'))
        res = super(res_partner, self).create(vals)
        return res

    name = fields.Char(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange')
    title = fields.Many2one(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    parent_name = fields.Char(track_visibility='onchange')
    child_ids = fields.One2many(track_visibility='onchange')  # force "active_test" domain to bypass _search() override
    ref = fields.Char(track_visibility='onchange')
    lang = fields.Selection(track_visibility='onchange')
    user_id = fields.Many2one(track_visibility='onchange')
    vat = fields.Char(track_visibility='onchange')
    bank_ids = fields.One2many(track_visibility='onchange')
    website = fields.Char(track_visibility='onchange')

    category_id = fields.Many2many(track_visibility='onchange')
    credit_limit = fields.Float(track_visibility='onchange')
    barcode = fields.Char(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    customer = fields.Boolean(track_visibility='onchange')
    supplier = fields.Boolean(track_visibility='onchange')
    employee = fields.Boolean(track_visibility='onchange')
    function = fields.Char(track_visibility='onchange')
    type = fields.Selection(track_visibility='onchange')
    street = fields.Char(track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    zip = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    state_id = fields.Many2one(track_visibility='onchange')
    country_id = fields.Many2one(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    mobile = fields.Char(track_visibility='onchange')
    is_company = fields.Boolean(track_visibility='onchange')
    industry_id = fields.Many2one(track_visibility='onchange')
    company_type = fields.Selection(strack_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    color = fields.Integer(track_visibility='onchange')
    user_ids = fields.One2many(track_visibility='onchange')
    partner_share = fields.Boolean(track_visibility='onchange')
    contact_address = fields.Char(track_visibility='onchange')
    commercial_partner_id = fields.Many2one(track_visibility='onchange')
    commercial_company_name = fields.Char(track_visibility='onchange')
    company_name = fields.Char(track_visibility='onchange')
