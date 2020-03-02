# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import first

def _filter_trigger_lines(trigger_lines):
    filtered_trigger_lines = []
    unique_tests = []
    for trigger_line in trigger_lines:
        if not trigger_line.first_inspection and  trigger_line.test not in unique_tests:
            filtered_trigger_lines.append(trigger_line)
            unique_tests.append(trigger_line.test)
    return filtered_trigger_lines

def _filter_trigger_lines_first(trigger_lines):
    filtered_trigger_lines = []
    unique_tests = []
    for trigger_line in trigger_lines:
        if  trigger_line.first_inspection and  trigger_line.test not in unique_tests:
            filtered_trigger_lines.append(trigger_line)
            unique_tests.append(trigger_line.test)
    return filtered_trigger_lines

class QcInspection(models.Model):
    _inherit = 'qc.inspection'
    object_type = fields.Char(string='Object Type', compute="_compute_object_type",
        store=True)
    picking_id = fields.Many2one(
        comodel_name="stock.picking", compute="_compute_picking", store=True)
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot', compute="_compute_lot",
        store=True)

    @api.multi
    def object_selection_values(self):
        result = super().object_selection_values()
        result.extend([
            ('stock.picking', "Picking List"), ('stock.move', "Stock Move")])
        return result

    @api.multi
    @api.depends('object_id')
    def _compute_object_type(self):
        for inspection in self:
            if inspection.object_id:
                inspection.object_type = inspection.object_id._name
    @api.multi
    @api.depends('object_id')
    def _compute_picking(self):
        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == 'stock.move':
                    inspection.picking_id = inspection.object_id.picking_id
                elif inspection.object_id._name == 'stock.picking':
                    inspection.picking_id = inspection.object_id
                elif inspection.object_id._name == 'stock.move.line':
                    inspection.picking_id = inspection.object_id.picking_id

    @api.multi
    @api.depends('object_id')
    def _compute_lot(self):
        moves = self.filtered(
            lambda i: i.object_id and
            i.object_id._name == 'stock.move').mapped('object_id')
        move_lines = self.env['stock.move.line'].search([
            ('lot_id', '!=', False),
            ('move_id', 'in', [move.id for move in moves])])

        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == 'stock.move.line':
                    inspection.lot_id = \
                        inspection.object_id.lot_id
                elif inspection.object_id._name == 'stock.move':
                    inspection.lot_id = first(move_lines.filtered(
                        lambda line: line.move_id == inspection.object_id
                    )).lot_id
                elif inspection.object_id._name == 'stock.production.lot':
                    inspection.lot_id = inspection.object_id

    @api.multi
    @api.depends('object_id')
    def _compute_product_id(self):
        """Overriden for getting the product from a stock move."""
        self.ensure_one()
        super(QcInspection, self)._compute_product_id()
        if self.object_id:
            if self.object_id._name == 'stock.move':
                self.product_id = self.object_id.product_id
            elif self.object_id._name == 'stock.move.line':
                self.product_id = self.object_id.product_id
            elif self.object_id._name == 'stock.production.lot':
                self.product_id = self.object_id.product_id

    @api.onchange('object_id')
    def onchange_object_id(self):
        if self.object_id:
            if self.object_id._name == 'stock.move':
                self.qty = self.object_id.product_qty
            elif self.object_id._name == 'stock.move.line':
                self.qty = self.object_id.product_qty

    @api.multi
    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super(QcInspection, self)._prepare_inspection_header(
            object_ref, trigger_line)
        # Fill qty when coming from pack operations
        if object_ref and object_ref._name == 'stock.move.line':
            res['qty'] = object_ref.product_qty
        if object_ref and object_ref._name == 'stock.move':
            res['qty'] = object_ref.product_uom_qty
        return res


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    picking_id = fields.Many2one(
        comodel_name="stock.picking", related="inspection_id.picking_id",
        store=True)
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot", related="inspection_id.lot_id",
        store=True)
