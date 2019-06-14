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



    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):

        domain=[]
        domain.append('|')

        list_domain_temp=[]
        list_domain_temp.append('user_id')
        list_domain_temp.append('=')
        list_domain_temp.append(self._uid)
        domain.append(list_domain_temp)

        list_domain_temp = []
        list_domain_temp.append('create_uid')
        list_domain_temp.append('=')
        list_domain_temp.append(self._uid)
        domain.append(list_domain_temp)

        records = self.search(domain or [], offset=offset, limit=limit, order=order)
        if not records:
            return []
        if fields and fields == ['id']:
            # shortcut read if we only want the ids
            return [{'id': record.id} for record in records]
        # read() ignores active_test, but it would forward it to any downstream search call
        # (e.g. for x2m or function fields), and this is not the desired behavior, the flag
        # was presumably only meant for the main search().
        # TODO: Move this to read() directly?
        if 'active_test' in self._context:
            context = dict(self._context)
            del context['active_test']
            records = records.with_context(context)

        result = records.read(fields)
        if len(result) <= 1:
            return result
        # reorder read
        index = {vals['id']: vals for vals in result}
        return [index[record.id] for record in records if record.id in index]
