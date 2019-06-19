# Copyright 2018 joytao zhu (e2yun)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models, tools
from odoo.exceptions import except_orm, MissingError


class FormModel(models.AbstractModel):
    """ Extend Base class.
    """
    _inherit = 'base'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        view_obj = self.env['ir.ui.view']

        if view_type == "form":
            if not view_id:
                view = self._get_map_view()
            else:
                view = view_obj.browse(view_id)
            res = super().fields_view_get(
                view_id=view.id, view_type='form', toolbar=toolbar,
                submenu=submenu)
        else:
            return super().fields_view_get(
                view_id=view_id, view_type=view_type, toolbar=toolbar,
                submenu=submenu)
        return res

