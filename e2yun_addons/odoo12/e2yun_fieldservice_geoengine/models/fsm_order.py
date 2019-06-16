# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    @api.multi
    def geo_localize(self):
        super(FSMOrder, self).geo_localize()
        self.create_geometry()