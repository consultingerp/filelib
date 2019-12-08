# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api,exceptions
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    new_signup = fields.Selection([('supplier','Supplier'),('new_signup','New Signup')],string='New Signup',default='supplier')

    @api.multi
    def approval_partner(self):
        self.supplier = True
        return True
