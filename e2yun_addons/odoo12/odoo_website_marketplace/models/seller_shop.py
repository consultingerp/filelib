# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class sellers_shop(models.Model):
    _name = 'seller.shop'
    _inherit = ['mail.thread']
    
    @api.depends('name','seller_id')
    def seller_products(self):
        for product in self:
            product_ids = self.env['product.template'].search([('seller_id','=',product.seller_id.sudo().partner_id.id)])
            product.seller_product_ids = [(6,0,product_ids.ids)]
        return True

    @api.depends('seller_product_ids','seller_id')
    def count_product(self):
        for count in self:
            count.total_product = len(count.seller_product_ids)
        return True

    name = fields.Char('Shop Name',required=True)

    seller_id= fields.Many2one('res.users', "seller" ,required="True")
    seller_product_ids = fields.Many2many('product.template',store=True, compute='seller_products')
    
    active = fields.Boolean(string='Active',default=True)
    
    city = fields.Char('city')
    color = fields.Integer('Color')
    country_id = fields.Many2one('res.country','Country')
    description = fields.Text('Description')
    state_id =fields.Many2one('res.country.state','State')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip')

    email = fields.Char('Email')
    phone = fields.Char('Phone')
    
    # pro_count = fields.Boolean('Product Count')
    total_product = fields.Integer('Total Product',default=0,store=True,compute='count_product')
    
    shop_url = fields.Char('URL',readonly=True)
    header_url = fields.Char('Header URL')
    url_handler = fields.Char('URL Handler',required=True,copy=False)
    
    published_website = fields.Boolean('Website Published')
    # pro_sale_count = fields.Boolean('Product Sale Count')
    
    fax = fields.Char('Fax')
    terms_con_seller = fields.Html('Terms & Conditions')

    # terms_con_shop = fields.Html('Terms & Conditions')
    # ship_address = fields.Boolean('Seller Shipping Address')
    
    banner = fields.Binary('Banner')
    shop_logo = fields.Binary('Shop Logo')
    
    tag_line = fields.Char('Shop Tag Line',required=True)

    return_polocy = fields.Html('Return Policy')
    shipping_policy = fields.Html('Shipping Policy')

    _sql_constraints = [
        ('name_url_handler_shop_uniq', 'UNIQUE(url_handler)', 'URL Name Must Be unique! \n URL you\'re trying to use is already has been taken!!'),
        ('name_seller_shop_unique', 'UNIQUE(seller_id)', 'Seller Name Must Be unique! \n Seller you\'re trying to use is already has been taken!!'),
    ]


    def toggle_active(self):
        for record in self:
            record.active = True
        return True
    
class seller_review( models.Model):
    _name = 'seller.review'   
    
    name = fields.Char('Review Title',required=True)
    seller_id= fields.Many2one('res.users', "Seller" ,required=True)
    email =fields.Char('Email Address')
    rating_num = fields.Integer('Rating',required=True)
    rating_msg = fields.Text('Rating Message',required=True)
    
