# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError, Warning


class order_line_seller(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('order_id.picking_ids')
    @api.multi
    def _compute_picking_ids(self):
        for line in self:

            delivery_list = []

            if self.env.user.has_group('odoo_website_marketplace.group_market_place_seller'):
                for pick in line.order_id.picking_ids:
                    if pick.move_line_ids:
                        if pick.move_line_ids[0].product_id.product_tmpl_id.seller_id == self.env.user.partner_id:
                            delivery_list.append(pick.move_line_ids[0].product_id.id)
                delivery_count = len(delivery_list)
            else:
                delivery_count = len(line.order_id.picking_ids)

            line.update({
                'delivery_count' : delivery_count
                })


    @api.onchange('product_id')
    @api.multi
    def product_id_change(self):
        result = super(order_line_seller, self).product_id_change()
        for line in self:
            if line.product_id:
                line.seller_id = line.product_id.product_tmpl_id.seller_id.id
        return result

    order_state = fields.Selection([
        ('draft','Draft'),
        ('approved','Approved'),
        ('shipped','Shipped'),
        ],'States',default='draft',copy=False)
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')
    seller_id = fields.Many2one('res.partner',string='Marketplace Seller',store=True,readonly=True,related='product_id.seller_id')
    seller_amount = fields.Float('Seller Amount',default=0.0,copy=False)
    commission_amount = fields.Float('Commission Amount',default=0.0,copy=False)
    create_date = fields.Datetime(string='Creation Date',related='order_id.create_date',store=True, readonly=True, index=True, help="Date on which sales order is created.")
    # payment_tx_id = fields.Many2one('payment.transaction', string='Last Transaction', copy=False,related='order_id.payment_tx_id',store=True, readonly=True, index=True,)
    payment_acquirer_id = fields.Many2one('payment.acquirer', string='Payment Acquirer', store=True)
    pay_done = fields.Boolean('Done Payment',default=False)

    @api.multi
    def approve_order(self):
        for line in self:
            if line.product_id.type == 'product':
                if line.product_id.virtual_available < 0:
                    raise Warning(_('You plan to sell %s but you only have %s available \n \
                        You can not approve order right now. Please make sure you had enough qty available') % (line.product_uom_qty,line.product_id.virtual_available))
            line.sudo()._action_launch_stock_rule()
            line.order_state = 'approved'
        return True

    @api.multi
    def ship_order_view(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.sudo().mapped('order_id.picking_ids')
        picking_ids = []
        for picking in pickings:
            if picking.group_id.sale_id == self.order_id:
                for move in picking.move_ids_without_package:                    
                    if move.product_id.product_tmpl_id.seller_id == self.env.user.partner_id:
                        picking_ids.append(picking.id)
        
        picking_ids = list(set(picking_ids))
        
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        # pickings = self.mapped('picking_ids')
        if len(picking_ids) > 1:
            action['domain'] = [('id', 'in', picking_ids)]
        elif picking_ids:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = picking_ids[0]

        action['context'] = dict(self._context, default_partner_id=self.order_id.partner_id.id, default_picking_id=picking_ids[0], default_origin=self.order_id.name)
        return action


    @api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom')
    @api.multi
    def _compute_qty_delivered(self):
        super(order_line_seller, self)._compute_qty_delivered()

        for line in self:  # TODO: maybe one day, this should be done in SQL for performance sake
            if line.qty_delivered_method == 'stock_move':
                qty = 0.0
                for move in line.move_ids.filtered(lambda r: r.state == 'done' and not r.scrapped and line.product_id == r.product_id):
                    if move.location_dest_id.usage == "customer":
                        if not move.origin_returned_move_id or (move.origin_returned_move_id and move.to_refund):
                            qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
                    elif move.location_dest_id.usage != "customer" and move.to_refund:
                        qty -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
                line.qty_delivered = qty
                if line.qty_delivered == line.product_uom_qty:
                    line.write({'order_state' :'shipped' })



    # @api.multi
    # def _action_launch_stock_rule(self):
    #     """
    #     Launch procurement group run method with required/custom fields genrated by a
    #     sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
    #     depending on the sale order line product rule.
    #     """
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #
    #     errors = []
    #     for line in self:
    #         if line.state != 'sale' or not line.product_id.type in ('consu','product'):
    #             continue
    #         #qty = line._get_qty_procurement(previous_product_uom_qty)
    #         qty = line._get_qty_procurement()
    #         if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
    #             continue
    #         #group_id = None
    #         #group_id = line._get_procurement_group()
    #
    #         group_id = self.env['procurement.group'].create({
    #             'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
    #             'sale_id': line.order_id.id,
    #             'partner_id': line.order_id.partner_shipping_id.id,
    #         })
    #
    #         line.order_id.procurement_group_id = group_id
    #
    #         # In case the procurement group is already created and the order was
    #         # cancelled, we need to update certain values of the group.
    #
    #         updated_vals = {}
    #
    #         if group_id.partner_id != line.order_id.partner_shipping_id:
    #             updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
    #         if group_id.move_type != line.order_id.picking_policy:
    #             updated_vals.update({'move_type': line.order_id.picking_policy})
    #         if updated_vals:
    #             group_id.write(updated_vals)
    #
    #         values = line._prepare_procurement_values(group_id=group_id)
    #         product_qty = line.product_uom_qty - qty
    #
    #         #line_uom = line.product_uom
    #
    #         procurement_uom = line.product_uom
    #         quant_uom = line.product_id.uom_id
    #         get_param = self.env['ir.config_parameter'].sudo().get_param
    #         if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
    #             product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
    #             procurement_uom = quant_uom
    #         #product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
    #             try:
    #                 self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom,
    #                                                   line.order_id.partner_shipping_id.property_stock_customer,
    #                                                   line.name, line.order_id.name, values)
    #             except UserError as error:
    #                 errors.append(error.name)
    #     if errors:
    #         raise UserError('\n'.join(errors))
    #
    #     return True

# class order_seller(models.Model):
#     _inherit = 'sale.order'
#
#     @api.multi
#     def _action_confirm(self):
#         super(order_seller, self)._action_confirm()
#         for line in self.order_line:
#             line._action_launch_stock_rule()

