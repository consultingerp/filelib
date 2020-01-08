# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.exceptions import ValidationError

class TierDefinition(models.Model):
    _inherit = "tier.definition"

    rebut = fields.Boolean("驳回")
    reject = fields.Boolean("拒绝")

    _order = "model_id asc ,sequence asc "
    up_sequence = fields.Integer("up sequence")



    @api.model
    def _get_tier_validation_model_names(self):
        res = super(TierDefinition, self)._get_tier_validation_model_names()
        res.append("agreement")
        return res

