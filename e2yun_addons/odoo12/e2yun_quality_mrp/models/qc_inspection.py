# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models



class QcInspection(models.Model):
    _inherit = 'qc.inspection'
    production_id = fields.Many2one(
        comodel_name='mrp.production', compute="_compute_production", store=True)
    workorder_id = fields.Many2one(
        comodel_name='mrp.workorder', compute="_compute_workorder", store=True)

    operation_id = fields.Many2one(comodel_name='mrp.routing.workcenter', string='Step',
                                   compute="_compute_operation", store=True)

    lot_id = fields.Many2one(
        comodel_name='stock.production.lot', compute="_compute_lot",
        store=True)

    @api.multi
    def object_selection_values(self):
        result = super().object_selection_values()
        result.extend([
            ('mrp.production', "Production Order"), ('mrp.workorder', "Work Order")])
        return result

    @api.multi
    @api.depends('object_id')
    def _compute_operation(self):
        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == 'mrp.workorder':
                    inspection.operation_id = inspection.object_id.operation_id

    @api.multi
    @api.depends('object_id')
    def _compute_workorder(self):
        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == 'mrp.workorder':
                    inspection.workorder_id = inspection.object_id

    @api.multi
    @api.depends('object_id')
    def _compute_production(self):
        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == 'mrp.workorder':
                    inspection.production_id = inspection.object_id.production_id
                elif inspection.object_id._name == 'mrp.production':
                    inspection.production_id = inspection.object_id
                elif inspection.object_id._name == 'mrp.product.produce':
                    inspection.production_id = inspection.object_id.production_id


    @api.multi
    @api.depends('object_id')
    def _compute_lot(self):



        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == 'stock.move.line':
                    inspection.lot_id = inspection.object_id.lot_id
                elif inspection.object_id._name == 'stock.move':
                    moves = self.filtered(
                        lambda i: i.object_id and
                                  i.object_id._name == 'stock.move').mapped('object_id')
                    move_lines = self.env['stock.move.line'].search([
                        ('lot_id', '!=', False),
                        ('move_id', 'in',  moves.ids)])
                    lines = move_lines.filtered(
                        lambda line: line.move_id == inspection.object_id
                    )
                    if len(lines) > 0:
                        inspection.lot_id = lines[-1].lot_id
                elif inspection.object_id._name == 'mrp.workorder':
                    inspection.lot_id =inspection.object_id.final_lot_id
                elif inspection.object_id._name == 'mrp.production':
                    move_ids = inspection.object_id.move_dest_ids.filtered(
                        lambda line: line.production_id == inspection.object_id
                    )
                    if len(move_ids) > 0:
                        lines = self.env['stock.move.line'].search([
                            ('lot_id', '!=', False),
                            ('move_id', 'in',  move_ids.ids)])
                        if len(lines) > 0:
                            inspection.lot_id = lines.mappped('lot_id')[-1]
                    if not inspection.lot_id:
                        move_ids = inspection.object_id.move_finished_ids.filtered(
                            lambda line: line.production_id == inspection.object_id
                        )
                        if len(move_ids) > 0:
                            lines = self.env['stock.move.line'].search([
                                ('lot_id', '!=', False),
                                ('move_id', 'in', move_ids.ids)])
                            if len(lines) > 0:
                                inspection.lot_id = lines.mapped('lot_id')[-1]
                elif inspection.object_id._name == 'mrp.product.produce':
                    inspection.lot_id = inspection.object_id.lot_id
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
            elif self.object_id._name == 'mrp.workorder':
                self.product_id = self.object_id.product_id
            elif self.object_id._name == 'mrp.production':
                self.product_id = self.object_id.product_id
            elif self.object_id._name == 'mrp.product.produce':
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
            elif self.object_id._name == 'mrp.production':
                self.qty = self.object_id.product_qty
            elif self.object_id._name == 'mrp.workorder':
                self.qty = self.object_id.qty_producing
            elif self.object_id._name == 'mrp.product.produce':
                self.qty = self.object_id.product_qty

    @api.multi
    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super(QcInspection, self)._prepare_inspection_header(
            object_ref, trigger_line)
        # Fill qty when coming from pack operations
        if object_ref and object_ref._name == 'stock.move.line':
            res['qty'] = object_ref.product_qty
        elif object_ref and object_ref._name == 'stock.move':
            res['qty'] = object_ref.product_uom_qty
        elif object_ref and object_ref._name == 'mrp.production':
            res['qty'] = object_ref.product_qty
        elif object_ref and object_ref._name == 'mrp.workorder':
            res['qty'] = object_ref.qty_producing
        elif object_ref and object_ref._name == 'mrp.product.produce':
            res['qty'] = object_ref.product_qty
        return res


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    production_id = fields.Many2one(
        comodel_name="mrp.production", related="inspection_id.production_id",
        store=True)
    workorder_id = fields.Many2one(
        comodel_name="mrp.workorder", related="inspection_id.workorder_id",
        store=True)
    operation_id = fields.Many2one(
        comodel_name="mrp.routing.workcenter", related="inspection_id.operation_id",
        store=True)

