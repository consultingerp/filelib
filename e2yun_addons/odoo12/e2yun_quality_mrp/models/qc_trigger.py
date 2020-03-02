
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcTrigger(models.Model):
    _inherit = 'qc.trigger'

    code = fields.Selection(related='picking_type_id.code', readonly=False)
