# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class crm_team(models.Model):
    _inherit = 'crm.team'

    parent_id = fields.Many2one('crm.team', 'Parent Team')
