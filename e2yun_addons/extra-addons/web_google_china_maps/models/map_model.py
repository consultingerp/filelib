# Copyright 2011-2012 Nicolas Bessi (Camptocamp SA)
# Copyright 2016 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models, tools
from odoo.exceptions import except_orm, MissingError


class MapModel(models.AbstractModel):
    """ Extend Base class.
    """
    _inherit = 'base'

    @api.model
    def _get_map_view(self):
        map_view = self.env['ir.ui.view'].search(
            [('model', '=', self._name),
             ('type', '=', 'map')], limit=1)
        if not map_view:
            raise except_orm(
                _('No Mapview defined for the model %s') % self._name,
                _('Please create a view or modify view mode'))
        return map_view

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """Returns information about the available fields of the class.
           If view type == 'map' returns geographical columns available"""
        view_obj = self.env['ir.ui.view']
        field_obj = self.env['ir.model.fields']

        def set_field_real_name(in_tuple):
            if not in_tuple:
                return in_tuple
            name = field_obj.browse(in_tuple[0]).name
            out = (in_tuple[0], name, in_tuple[1])
            return out
        if view_type == "map":
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

