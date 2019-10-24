# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
# from openerp import models, api
from odoo import models, api


class GenerateModelAccess(models.TransientModel):
    _name = 'generate.model.access'
    _description = "generate model access"

    @api.one
    def batch_generate_model_access(self):
        group_obj = self.env['res.groups']
        active_ids = self.env.context.get('active_ids', [])
        groups = group_obj.browse(active_ids)
        groups.generate_model_access()
        return True
