# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api

class Users(models.Model):
    _inherit = 'res.users'

    transfer_user = fields.Many2one('res.users', string='Transfer the user', track_visibility='onchange')


    @api.multi
    def write(self, values):
        if 'transfer_user' in values.keys():
            #销售员交接
            sql='update crm_lead set user_id=%s where  user_id=%s'
            self._cr.execute(sql, (values['transfer_user'], self.id))

        res = super(Users, self).write(values)

