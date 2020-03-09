# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models,fields

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    property_line_ids = fields.One2many('lot.property.line', 'lot_id', string='Lot Properties')

    # {'property_line_ids': [[1, 22, {'value_ids': [[6, False, [1, 3]]]}], [4, 20, False], [4, 21, False]]}
    # def write(self, values):
    #     if 'property_line_ids' in values:
    #         for item in values['property_line_ids']:
    #             item[2]['lot_id'] = self.id
    #
    #     res = super(ProductionLot, self).write(values)
    #
    #     return res
    def create(self, values):
        if 'property_line_ids' not in values:
            values['property_line_ids'] = []
            for item in self.env['base.property'].search([]):
                property_line = [0,0,{'property_id':item.id}]
                values['property_line_ids'].append(property_line)
        res = super(ProductionLot, self).create(values)

        return res