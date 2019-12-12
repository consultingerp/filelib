# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round as round

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _message_count(self):
        self.message_count = self.website_message_ids and len( self.website_message_ids ) or 0

    def _get_partner_rate(self):
        for obj in self:
            partner_rate = 0.0
            total_messages = len( [x.id for x in obj.website_message_ids if x.message_rate > 0] )
            if total_messages > 0:
                total_rate = sum( [x.message_rate for x in obj.website_message_ids] )
                # getcontext().prec = 3
                partner_rate = float(float(total_rate) / float(total_messages))
                # partner_rate = Decimal( total_rate ) / Decimal( total_messages )
            obj.partner_rate = round(partner_rate, 2)


    seller = fields.Boolean('Is A Seller?? ')
    profile_detail = fields.Text(string='Profile Details')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('approve', 'Approved'),
        ('denied', 'Denied'),
        ], 'Status', readonly=True, copy=False, default="draft",index=True)
    seller_shop_id = fields.Many2one('seller.shop','Seller')
    url_handler = fields.Char('URL Handler')
    shop_name = fields.Char('Shop Name')
    tag_line = fields.Char('Shop Tag Line')
    seller_id = fields.Many2one('res.users','Shop User',copy=False)
    website_true = fields.Boolean('Website True',default=False,copy=False)
    password = fields.Char('Password')
    partner_rate = fields.Float(compute=_get_partner_rate, store=False, string='Partner Rate' )
    message_count = fields.Integer(string="Messages", compute="_message_count" )
    website_message_ids = fields.One2many('mail.message', 'res_id', domain=lambda self: [( 'model', '=', self._name ),('website_message','=',True)], string='Website Comments' ) #( 'type', '=', 'comment' ),
    seller_credit = fields.Float(string="Credit",default=0.0)
    seller_commission = fields.Float(string="Commission",default=0.0)
    max_withdraw_amount = fields.Float(string="Maximum Withdraw Amount",default=0.0)
    payment_method_ids = fields.Many2many('seller.payment.method',string="Payment Methods",)
    last_payment_date = fields.Date('Last Payment Date',)
    overwrite_setting = fields.Boolean('Overwrite Default Commission Setting',default=False,copy=False)


    def action_view_product_rating(self):
        tree_view = self.env.ref('mail.view_message_tree', False)
        form_view = self.env.ref('mail.view_message_form', False)
        
        return {
            'name': _( 'Product Rating' ),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'mail.message',
            'views': [(tree_view.id, 'tree' ), (form_view.id, 'form' )],
            'view_id': tree_view.id,
            'domain': "[('id','in',[" + str( self.website_message_ids.ids ).strip( "[]" ) + "]),('website_message','=',True)]",
        }


    def ask_to_approve(self):
        for record in self:

            if not record.shop_name:
                raise UserError(_('Error! Please Enter Valid Shop Name!'))

            if not record.tag_line:
                raise UserError(_('Error! Please Enter Valid Tag Line!'))

            if not record.password:
                raise UserError(_('Error! Please Enter Valid Password!'))

            if not record.seller:
                raise UserError(_('Error! Please Enter Make Partner a Seller for Approval!'))

            if record == self.env.user.partner_id:
                record.seller_id = self.env.user.id
            template_id = self.env.ref('odoo_website_marketplace.email_template_marketplace_approve')
            
            template_id.send_mail(record.id) 
            record.state = 'waiting'
        return True

    def approve_partner(self):
        for record in self:
            context = None
            pattern = re.compile('(\w+[.|\w])*@(\w+[.])*(com$|in$)')
            if self.email:
                if not re.match(pattern, self.email):
                    raise UserError(_('Error! Email value is incorrect. Enter valid email to process!'))

            res_users = self.env['res.users']
            sellers_shop = self.env['seller.shop']

            pending_seller_id = self.env.ref('odoo_website_marketplace.group_market_place_seller')
            stock_user_id = self.env.ref('stock.group_stock_user')
                
            print(stock_user_id,'-0-0000000000000000000000 stock')

            seller_id = False
            group_list = []
            group_list.append(pending_seller_id.id)
            group_list.append(stock_user_id.id)
            
            if self.website_true == True:
                if self.seller_id:
                    self.seller_id.write({
                        'groups_id' : [(6, 0, group_list)],
                        })
                    seller_id = self.seller_id.id
            else:
                if not self.seller_id:
                    valuess = {
                    'email': record.email,
                    'login': record.email,
                    'password' : str(record.password),
                    'partner_id': record.id,
                    'groups_id': [(6, 0, group_list)],
                    }
                    create_id = res_users.create(valuess)
                    seller_id = create_id.id
                else:
                    if self.seller_id:
                        self.seller_id.write({
                            'groups_id' : [(6, 0, group_list)],
                        })
                        seller_id = self.seller_id.id
            
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url').rstrip('/')
            
            url = base_url + str('/sellers/') + str(record.id)
            

            shop = {
                'seller_id' : seller_id,
                'name' : record.shop_name,
                'tag_line' : record.tag_line,
                'url_handler' : url,
            }

            shop_id = sellers_shop.create(shop)

            template_id = self.env.ref('odoo_website_marketplace.email_template_marketplace_approved')
            
            template_id.send_mail(record.id) 
            record.url_handler = url
            record.seller_id = seller_id
            record.seller_shop_id = shop_id
            record.seller = True
            record.state = 'approve'

        return True

    def deny_partner(self):
        for record in self:
            template_id = self.env.ref('odoo_website_marketplace.email_template_marketplace_rejected')
            template_id.send_mail(record.id) 
            record.state = 'denied'
            record.seller_id = False
            record.seller_shop_id = False
        return True

    def set_to_draft(self):
        for record in self:
            record.state = 'draft'
        return True

    def partner_credit(self):
        '''
        This function returns an action that display payment history of customer.
        '''
        action = self.env.ref('odoo_website_marketplace.action_partner_seller_payment_').sudo().read()[0]
        action['domain'] = [('seller_id', '=', self.id)]
        return action


    def unlink(self):
        for partner in self:
            if partner.state not in ('draft', 'denied'):
                raise UserError(_('You cannot delete an partner which is not draft or cancelled.'))
        return super(ResPartner, self).unlink()


class mailmessage(models.Model):
    _inherit = 'mail.message'

    message_rate = fields.Integer('Message Rating')
    short_description = fields.Char('Short Description')
    website_message = fields.Boolean('Is Website Message', default=False)
