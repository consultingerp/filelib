# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
# from openerp import models, api
from odoo import models, api


class GenerateRuleGroups(models.TransientModel):
    _name = 'generate.rule.groups'
    _description = "generate rule groups"

    @api.one
    def batch_generate_rule_groups(self):
        group_obj = self.env['res.groups']
        active_ids = self.env.context.get('active_ids', [])
        groups = group_obj.browse(active_ids)
        groups.generate_rule_groups()
        return True
