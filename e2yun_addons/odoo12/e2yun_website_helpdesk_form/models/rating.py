# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class Rating(models.Model):
    _inherit = "rating.rating"

    @api.multi
    def write(self, values):
        rating_super = super(Rating, self).write(values)
        if self.res_model and self.res_model == 'helpdesk.ticket':
            tickets = self.env['helpdesk.ticket'].search([('id', '=', self.res_id)])
            tickets.synserviceorderrating()
        return rating_super
