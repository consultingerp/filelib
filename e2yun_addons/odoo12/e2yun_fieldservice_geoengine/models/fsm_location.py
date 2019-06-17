# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models



class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    @api.multi
    def write(self, vals):
        res = super(FSMLocation, self).write(vals)
        if (('street' in vals) or ('street2' in vals) or ('city' in vals) or
                  ('country_id' in vals) or ('zip' in vals) or ('state_id' in vals)):
            self.geo_localize()
            self._update_order_geometries()
        return res
