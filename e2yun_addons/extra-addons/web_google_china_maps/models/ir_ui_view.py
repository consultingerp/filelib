# -*- coding: utf-8 -*-
from odoo import fields, models, _, api

MAP_VIEW = ('map', _('Map'))

class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('map', _('Map'))])


    # @api.model
    # def _setup_fields(self):
    #     """Hack due since the field 'type' is not defined with the new api.
    #     """
    #     cls = type(self)
    #     type_selection = cls._fields['type'].selection
    #     if MAP_VIEW not in type_selection:
    #         tmp = list(type_selection)
    #         tmp.append(MAP_VIEW)
    #         cls._fields['type'].selection = tuple(set(tmp))
    #     super()._setup_fields()