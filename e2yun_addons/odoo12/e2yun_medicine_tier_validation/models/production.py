# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ['mrp.production', 'tier.validation']
    _state_from = ['draft']
    _state_to = ['','confirmed']
