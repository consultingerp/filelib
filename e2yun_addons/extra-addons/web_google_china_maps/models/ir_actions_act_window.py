# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.addons import base
if 'map' not in base.models.ir_actions.VIEW_TYPES:
    base.models.ir_actions.VIEW_TYPES.append(('map', _('Map')))
class IrActionsActWindow(models.Model):
    _inherit = 'ir.actions.act_window'

    view_type = fields.Selection(selection_add=[('map', _('Map'))])
