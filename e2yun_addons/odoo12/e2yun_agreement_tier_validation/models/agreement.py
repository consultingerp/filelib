# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Agreement(models.Model):
    _name = "agreement"
    _inherit = ['agreement', 'tier.validation']
    _stage_id_from = ['1', '2', '3']
    _stage_id_to = ['4']
