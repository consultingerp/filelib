# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class RequestPayment(models.TransientModel):
    _name = 'request.payment'
    _description = 'Request Payment'

    partner_id = fields.Many2one('res.partner','Partner')
    credit = fields.Float('Credit')
    already_requested = fields.Boolean('Already Requested')
    request = fields.Float('Request Money')
    description = fields.Text('Payment Description')

    @api.model
    def default_get(self, fields):
        res = super(RequestPayment, self).default_get(fields)
        if self.env.user.partner_id:
            payment_obj = self.env['seller.payment']
            payment_id = payment_obj.search([('state','in',['draft','requested']),('seller_id','=',self.env.user.partner_id.id)])
            if payment_id:
                raise Warning(_('Your previous request is pending! you can not request right now!!!'))
            partner = self.env['res.partner'].browse(self.env.user.partner_id.id)
            if partner.seller == True:
                res.update({
                    'partner_id' : partner.id,
                    'credit' : partner.seller_credit
                    })
        return res


    def request_payment(self):
        for pay in self:
            if pay.request > pay.credit:
                raise Warning(_('You can not request more than credit amount.'))
            else:
                payment_obj = self.env['seller.payment']
                
                vals = {
                'seller_id' : pay.partner_id.id,
                'payment_mode' : 'seller_payment',
                'date' : fields.Date.context_today(self),
                'payment_type' : 'debit',
                'state' : 'draft',
                'payable_amount' : pay.request,
                'seller_commission' : pay.partner_id.seller_commission,
                'company_id' :  self.env.user.company_id.id,
                'currency_id' : self.env.user.company_id.currency_id.id,
                }
                
                payment_id = payment_obj.sudo().create(vals)
                payment_id.sudo().send_request()

                
                mananger_seller_id = self.env['ir.model.data'].sudo().get_object_reference('odoo_website_marketplace','group_market_place_manager')[1]

                group_manager = self.env['res.groups'].sudo().browse(mananger_seller_id)

                manager = None
                if group_manager.users:
                    manager = group_manager.users[0]

                template_id = self.env['ir.model.data'].sudo().get_object_reference('odoo_website_marketplace', 'email_template_payment_request_seller_email')[1]
                email_template_obj = self.env['mail.template'].sudo().browse(template_id)
                values = email_template_obj.sudo().generate_email(pay.partner_id.id)
                values['email_from'] = manager.sudo().partner_id.email
                values['email_to'] = pay.partner_id.email
                values['res_id'] = pay.partner_id.id
                values['body_html'] = """
                        <p>Dear %s</p>
                        <p> We Receive your payment request</p>
                        <p> Kindly wait for approval of your request.</p>
                        <br/>
                        <p>Your payment reference is <b> %s </b>. </p>
                        
                    """ % (str(pay.partner_id.name),str(payment_id.name))

                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.sudo().create(values)

                if msg_id:
                    mail_mail_obj.sudo().send([msg_id])

                action = self.env.ref('odoo_website_marketplace.action_payment_seller').read()[0]
                action['views'] = [(self.env.ref('odoo_website_marketplace.payment_seller_form_view').id, 'form')]
                action['res_id'] = payment_id.id

                return action


class RequestQty(models.TransientModel):
    _name = 'request.qty'
    _rec_name = 'product_tmpl_id'

    @api.model
    def default_get(self, fields):
        res = super(RequestQty, self).default_get(fields)
        product = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
        res.update({
            'product_tmpl_id' : product.id
        })
        return res

    update_qty = fields.Float(string='Update Qty', default=0.00)
    product_tmpl_id = fields.Many2one('product.template', string="product")

    def request_qty(self):
        company_id = self.env.user.company_id.id

        # stock_quant_id = self.env['stock.quant'].create(values)
        product_id = self.env['product.product'].search([('type','=','product'),('product_tmpl_id','=',self.product_tmpl_id.id)],limit=1)
        warehouse = self.env['stock.warehouse'].with_user(self.env.user).search([('company_id', '=', company_id)], limit=1)
        inventory_id = self.env['stock.inventory'].sudo().create({
            'name':product_id.name,
            'location_ids': [warehouse.lot_stock_id.id],
            'product_ids':[product_id.id],
            'company_id' : self.env.user.company_id.id
        })

        inventory_id.sudo().action_open_inventory_lines()
        lines = self.env['stock.inventory.line'].sudo().create({
            'product_id':product_id.id ,
            'inventory_id' : inventory_id.id ,
            'product_uom_id' : product_id.uom_id.id ,
            'product_qty': self.update_qty,
            'location_id' : warehouse.lot_stock_id.id})
       
        inventory_id.sudo().action_start()
        inventory_id.with_context(marketplace=True).action_validate()

        return {'type': 'ir.actions.act_window_close'}