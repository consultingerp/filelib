# -*- coding: utf-8 -*-
# Part of e2yun. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.e2yun_quality_stock.models.qc_inspection import _filter_trigger_lines , _filter_trigger_lines_first

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.multi
    def first_inspection(self):
        inspection_model = self.env['qc.inspection']
        qc_trigger = self.env['qc.trigger'].search(
            [('picking_type_id', '=', self.picking_type_id.id)])

        trigger_lines = set()
        for model in ['qc.trigger.product_category_line',
                      'qc.trigger.product_template_line',
                      'qc.trigger.product_line']:
            partner = (self.partner_id
                       if qc_trigger.partner_selectable else False)

            trigger_lines = trigger_lines.union(
                self.env[model].get_trigger_line_for_product(
                    qc_trigger, self.product_id, partner=partner))
        for trigger_line in _filter_trigger_lines_first(trigger_lines):
            inspection_model._make_inspection(self, trigger_line)






class MrpProductProduceQC(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.multi
    def check_finished_move_lots(self):
        produce_move = self.production_id.move_finished_ids.filtered(
            lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel'))
        if produce_move:
            inspection_model = self.env['qc.inspection']
            qc_trigger = self.env['qc.trigger'].search(
                [('picking_type_id', '=', self.production_id.picking_type_id.id)])

            trigger_lines = set()
            for model in ['qc.trigger.product_category_line',
                          'qc.trigger.product_template_line',
                          'qc.trigger.product_line']:
                partner = (self.partner_id
                           if qc_trigger.partner_selectable else False)

                trigger_lines = trigger_lines.union(
                    self.env[model].get_trigger_line_for_product(
                        qc_trigger, self.product_id, partner=partner))
            for trigger_line in _filter_trigger_lines(trigger_lines):
                inspection_model._make_inspection(self, trigger_line)

            res = super(MrpProductProduceQC, self).check_finished_move_lots()

        return res

    @api.multi
    def first_inspection(self):
        inspection_model = self.env['qc.inspection']
        qc_trigger = self.env['qc.trigger'].search(
            [('picking_type_id', '=', self.production_id.picking_type_id.id)])

        trigger_lines = set()
        for model in ['qc.trigger.product_category_line',
                      'qc.trigger.product_template_line',
                      'qc.trigger.product_line']:
            partner = (self.partner_id
                       if qc_trigger.partner_selectable else False)

            trigger_lines = trigger_lines.union(
                self.env[model].get_trigger_line_for_product(
                    qc_trigger, self.product_id, partner=partner))
        for trigger_line in _filter_trigger_lines_first(trigger_lines):
            inspection_model._make_inspection(self, trigger_line)


