from odoo import models, fields, api
from datetime import datetime

class marketplace_inventory(models.Model):
    _name = 'seller.dashboard'

    # @api.depends('name','state')
    def _count(self):
        for count in self:
            product_obj = self.env['product.template']
            partner_obj = self.env['res.partner']
            orderline_obj = self.env['sale.order.line']
            payment_obj = self.env['seller.payment']
            if count.state == 'product':
                if self.env.user.has_group('odoo_website_marketplace.group_market_place_manager'):
                    waiting = product_obj.sudo().search([('state','=','waiting')])
                    approved = product_obj.sudo().search([('state','=','approve')])
                    rejected = product_obj.sudo().search([('state','=','cancel')])

                    count.waiting_product = len(waiting)
                    count.approved_product = len(approved)
                    count.rejected_product = len(rejected)
                elif self.env.user.has_group('odoo_website_marketplace.group_market_place_seller'): 
                    waiting = product_obj.sudo().search([('seller_id','=',self.env.user.partner_id.id),('state','=','waiting')])
                    approved = product_obj.sudo().search([('seller_id','=',self.env.user.partner_id.id),('state','=','approve')])
                    rejected = product_obj.sudo().search([('seller_id','=',self.env.user.partner_id.id),('state','=','cancel')])

                    count.waiting_product = len(waiting)
                    count.approved_product = len(approved)
                    count.rejected_product = len(rejected)
                else:
                    count.waiting_product = 0
                    count.approved_product = 0
                    count.rejected_product = 0

            elif count.state == 'seller':
                if self.env.user.has_group('odoo_website_marketplace.group_market_place_manager'):
                    waiting = partner_obj.sudo().search([('state','=','waiting')])
                    approved = partner_obj.sudo().search([('state','=','approve')])
                    rejected = partner_obj.sudo().search([('state','=','denied')])

                    count.waiting_product = len(waiting)
                    count.approved_product = len(approved)
                    count.rejected_product = len(rejected)
            elif count.state == 'order':
                if self.env.user.has_group('odoo_website_marketplace.group_market_place_manager'):
                    waiting = orderline_obj.sudo().search([('order_state','=','approved')])
                    approved = orderline_obj.sudo().search([('order_state','=','shipped')])
                    rejected = orderline_obj.sudo().search([('order_state','=','draft')])

                    count.waiting_product = len(waiting)
                    count.approved_product = len(approved)
                    count.rejected_product = len(rejected)
                elif self.env.user.has_group('odoo_website_marketplace.group_market_place_seller'):
                    rejected = orderline_obj.sudo().search([('product_id.product_tmpl_id.seller_id','=',self.env.user.partner_id.id),('order_state','=','draft')])
                    waiting = orderline_obj.sudo().search([('product_id.product_tmpl_id.seller_id','=',self.env.user.partner_id.id),('order_state','=','approved')])
                    approved = orderline_obj.sudo().search([('product_id.product_tmpl_id.seller_id','=',self.env.user.partner_id.id),('order_state','=','shipped')])

                    count.waiting_product = len(waiting)
                    count.approved_product = len(approved)
                    count.rejected_product = len(rejected)
                else:
                    count.waiting_product = 0
                    count.approved_product = 0
                    count.rejected_product = 0 

            elif count.state == 'payment':
                if self.env.user.has_group('odoo_website_marketplace.group_market_place_manager'):
                    waiting = payment_obj.sudo().search([('state','=','requested')])
                    approved = payment_obj.sudo().search([('state','=','confirm')])
                    rejected = payment_obj.sudo().search([('state','=','cancel')])

                    count.waiting_product = len(waiting)
                    count.approved_product = len(approved)
                    count.rejected_product = len(rejected)
                elif self.env.user.has_group('odoo_website_marketplace.group_market_place_seller'): 
                    waiting = payment_obj.sudo().search([('seller_id','=',self.env.user.partner_id.id),('state','=','requested')])
                    approved = payment_obj.sudo().search([('seller_id','=',self.env.user.partner_id.id),('state','=','confirm')])
                    rejected = payment_obj.sudo().search([('seller_id','=',self.env.user.partner_id.id),('state','=','cancel')])

                    count.waiting_product = len(waiting)
                    count.approved_product = len(approved)
                    count.rejected_product = len(rejected)
                else:
                    count.waiting_product = 0
                    count.approved_product = 0
                    count.rejected_product = 0
            else:
                count.waiting_product = 0
                count.approved_product = 0
                count.rejected_product = 0
        return True

    name = fields.Char('Market Place Dashboard')
    color = fields.Integer('Color')
    state = fields.Selection([
        ('product', 'Products'), 
        ('order', 'Orders'),
        ('payment', 'Payments'),
        ('seller', 'Sellers'),
        ])
    waiting_product = fields.Integer('Pending Count',default=0,compute="_count")
    approved_product = fields.Integer('Approved Count',default=0,compute="_count")
    rejected_product = fields.Integer('Rejected Count',default=0,compute="_count")
    group_id = fields.Many2one('res.groups', string='Group', ondelete='cascade', index=True)