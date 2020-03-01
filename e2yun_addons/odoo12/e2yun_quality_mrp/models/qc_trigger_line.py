
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class QcTriggerLine(models.AbstractModel):
    _inherit = 'qc.trigger.line'

    operation_id = fields.Many2one('mrp.routing.workcenter', 'Step')
    routing_id = fields.Many2one(related='operation_id.routing_id', readonly=False)
    code = fields.Selection(related='trigger.code', readonly=False)
    first_inspection= fields.Boolean('First Inspection',default=False)



class QcTriggerProductCategoryLine(models.Model):
    _inherit = "qc.trigger.product_category_line"


    @api.onchange('product_category', 'trigger')
    def _onchange_product_category(self):
        product_ids = self.env['product.product'].search([('categ_id','child_of',self.product_category.id)])
        product_tmpl_ids = self.env['product.template'].search([('categ_id','child_of',self.product_category.id)])
        bom_ids = self.env['mrp.bom'].search(['|',('product_id', 'in', product_ids),
                                              ('product_tmpl_id', 'in', product_tmpl_ids)])
        routing_ids = bom_ids.mapped('routing_id.id')
        if self.trigger.code == 'mrp_operation':
            return {
                'domain': {
                    'operation_id': [('routing_id', 'in', routing_ids)],
                }
            }


class QcTriggerProductTemplateLine(models.Model):
    _inherit = "qc.trigger.product_template_line"


    @api.onchange('product_template', 'trigger')
    def _onchange_product_tmpl(self):
        bom_ids = self.env['mrp.bom'].search([('product_tmpl_id', '=', self.product_template.id)])
        routing_ids = bom_ids.mapped('routing_id.id')
        if self.trigger.code == 'mrp_operation':
            return {
                'domain': {
                    'operation_id': [('routing_id', 'in', routing_ids)],
                 }
            }

class QcTriggerProductLine(models.Model):
    _inherit = "qc.trigger.product_line"


    @api.onchange('product', 'trigger')
    def _onchange_product(self):
        bom_ids = self.env['mrp.bom'].search(['|',('product_id', '=', self.product.id),
                                              ('product_tmpl_id', '=', self.product.product_tmpl_id.id)])
        routing_ids = bom_ids.mapped('routing_id.id')
        if self.trigger.code == 'mrp_operation':
            return {
                'domain': {
                    'operation_id': [('routing_id', 'in', routing_ids)],
                }
            }
