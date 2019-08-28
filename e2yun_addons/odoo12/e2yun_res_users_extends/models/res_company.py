# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    company_code = fields.Char('公司代码')