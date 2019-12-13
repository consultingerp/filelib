# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError

class product_template(models.Model):
    _inherit = 'product.template'

        
    seller_id= fields.Many2one('res.partner', "Seller",domain=[('seller','=',True)])
    state = fields.Selection([
            ('draft', 'Draft'),
            ('waiting', 'Waiting'),
            ('approve', 'Approved'),
            ('cancel', 'Cancelled'),
            ], 'Status', readonly=True, copy=False, default="draft",  index=True)
    # product_categ_ids = fields.Many2many('product.public.category')

    @api.model
    def default_get(self, fields):
        res = super(product_template, self).default_get(fields)
        if self.env.user.has_group('odoo_website_marketplace.group_market_place_seller'):
            if self.env.user.partner_id.seller == True:
                res.update({
                    'seller_id' : self.env.user.partner_id.id
                    })
        return res

    @api.model
    def create(self,val):
        val.update({'sale_ok' : True,})
        result = super(product_template, self).create(val)
        return result

    @api.multi
    def write(self, val):
        res = super(product_template, self).write(val)
        if self.type != 'service':
            if self.env.user.id != 1:
                if self.env.user.has_group('odoo_website_marketplace.group_market_place_seller'):
                    if 'is_published' in val:
                        if val['is_published'] == True:
                            if self.state != 'approve':
                                raise UserError(_('Your product is not Approved!! You can not publish it'))
                    if 'website_published' in val:
                        if val['website_published'] == True:
                            if self.state != 'approve':
                                raise UserError(_('Your product is not Approved!! You can not publish it'))
        return res

    @api.multi
    def set_to_draft(self):
        for record in self:
            record.state = 'draft'
        return True

    @api.multi
    def request_approve(self):
        for record in self:            
            template_id = self.env.ref('odoo_website_marketplace.email_template_marketplace_approve_product')
            template_id.sudo().send_mail(record.id, force_send=True) 
            record.state = 'waiting'
            if record.seller_id:
                if record.seller_id.seller_shop_id:
                    record.seller_id.seller_shop_id.seller_products()
        return True

    @api.multi
    def approve_product(self):
        for record in self:
            template_id = self.env.ref('odoo_website_marketplace.email_template_marketplace_approved_product')
            template_id.sudo().send_mail(record.id, force_send=True) 
            record.state = 'approve'
            if record.seller_id:
                if record.seller_id.seller_shop_id:
                    record.seller_id.seller_shop_id.seller_products()
            record.website_published = True
            record.active = True
        return True

    @api.multi
    def reject_product(self):
        for record in self:
            template_id = self.env.ref('odoo_website_marketplace.email_template_marketplace_reject_product')
            template_id.sudo().send_mail(record.id, force_send=True) 
            if record.seller_id:
                if record.seller_id.seller_shop_id:
                    record.seller_id.seller_shop_id.seller_products()
            record.state = 'cancel'
            record.website_published = False
        return True


class website(models.Model):
    _inherit = 'website'

    @api.multi
    def get_seller_products(self, seller):
        user_ids=self.env['res.users'].search([('partner_id','=',seller.id)])
        prod_ids=self.env['product.template'].search([('seller_id','=',user_ids.partner_id.id)])
        return prod_ids


class Inventory(models.Model):
    _inherit = "stock.inventory"

    @api.multi
    def action_validate(self):
        if not self.exists():
            return
        self.ensure_one()

        if not self._context.get('marketplace'):
            if not self.user_has_groups('stock.group_stock_manager'):
                raise UserError(_("Only a stock manager can validate an inventory adjustment."))
        if self.state != 'confirm':
            raise UserError(_(
                "You can't validate the inventory '%s', maybe this inventory " +
                "has been already validated or isn't ready.") % (self.name))
        inventory_lines = self.line_ids.filtered(lambda l: l.product_id.tracking in ['lot', 'serial'] and not l.prod_lot_id and l.theoretical_qty != l.product_qty)
        lines = self.line_ids.filtered(lambda l: float_compare(l.product_qty, 1, precision_rounding=l.product_uom_id.rounding) > 0 and l.product_id.tracking == 'serial' and l.prod_lot_id)
        if inventory_lines and not lines:
            wiz_lines = [(0, 0, {'product_id': product.id, 'tracking': product.tracking}) for product in inventory_lines.mapped('product_id')]
            wiz = self.env['stock.track.confirmation'].create({'inventory_id': self.id, 'tracking_line_ids': wiz_lines})
            return {
                'name': _('Tracked Products in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.track.confirmation',
                'target': 'new',
                'res_id': wiz.id,
            }
        self._action_done()
        self.line_ids._check_company()
        self._check_company()
        return True