# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class crm_lead(models.Model):
    _inherit = 'crm.lead'

    parent_team_id = fields.Many2one(comodel_name='crm.team', string='Parent Team id',compute='_compute_parent_team_id', store=True)

    @api.one
    @api.depends('team_id')
    def _compute_parent_team_id(self):
        self.parent_team_id = self.team_id.parent_id.id





