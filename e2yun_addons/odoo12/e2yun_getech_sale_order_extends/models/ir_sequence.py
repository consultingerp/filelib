# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api
import datetime
import suds.client
import json


class Product(models.Model):
    _inherit = 'ir.sequence'

    def get_next_code_info_if_no_create(self, type, prefix, suffix, padding):
        force_company = self._context.get('force_company')
        if not force_company:
            force_company = self.env.user.company_id.id
        sequence_code = '%s-%s-%s' % (type, prefix, suffix)
        seq_ids = self.search([('code', '=', sequence_code), ('company_id', 'in', [force_company, False])], order='company_id')

        if not seq_ids:
            data = {}
            data['prefix'] = prefix
            data['suffix'] = suffix
            data['name'] = sequence_code
            data['code'] = sequence_code
            data['implementation'] = 'standard'
            data['padding'] = padding
            seq_ids = self.create(data)
        seq_id = seq_ids[0]
        return seq_id._next()
