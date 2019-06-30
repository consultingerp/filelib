# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
