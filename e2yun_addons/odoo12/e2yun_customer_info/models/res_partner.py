# -*- coding: utf-8 -*-

from odoo import models, fields, api
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
