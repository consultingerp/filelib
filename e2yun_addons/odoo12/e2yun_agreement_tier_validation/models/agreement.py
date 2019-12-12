# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Agreement(models.Model):
    _name = "agreement"
    _inherit = ['agreement', 'tier.validation']
    _state_from = ['draft', 'active', 'inactive']
    _state_to = ['active', 'inactive']
