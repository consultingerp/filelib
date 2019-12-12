# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import Warning

class payment_seller(models.Model):
    _name = 'seller.payment'
    _inherit = 'mail.thread'

    name = fields.Char('Reference', copy=False, readonly=True, default=lambda x: _('New'))
    seller_id= fields.Many2one('res.partner', "seller" ,required=True,domain=[('seller','=',True)])
    payment_mode = fields.Selection([
            ('paid', 'Paid'),
            ('refund', 'Refund'),
            ('seller_payment', 'Seller Payment'),
            ('cancel', 'Cancelled'),
            ], 'Payment Mode',required=True)
    payment_description = fields.Text('Payment Description') 
    payable_amount = fields.Float('Payable Amount',required=True)
    date = fields.Date('Date')
    payment_method_id = fields.Many2one('seller.payment.method','Payment Method')
    payment_type = fields.Selection([('debit','Debit'),('credit','Credit')],'Payment Type',required=True)
    invoice_id = fields.Many2one('account.invoice','Invoice')
    state = fields.Selection([
        ('draft','Draft'),
        ('requested','Requested'),
        ('confirm','Confirm'),
        ('cancel','Cancelled')],'State',default='draft',copy=False)
    invoice_line_ids = fields.Many2many('account.invoice.line', string='Invoice Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    seller_commission = fields.Float('Seller Commission',default=0.0)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.user.company_id,
        help="Company related to this journal")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Account Currency', store=True, help="The related account currency if not equal to the company one.", readonly=True)


    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            sequence_credit = self.env['ir.sequence'].next_by_code('seller_credit') 
            sequence_debit = self.env['ir.sequence'].next_by_code('seller_debit')
            if vals.get('payment_type') == 'debit':
                vals['name'] = sequence_debit or _('New')
            else:
                vals['name'] = sequence_credit or _('New')
            
        return super(payment_seller, self).create(vals)

    def send_request(self):
        for payment in self:
            payment.state = 'requested'
        return True

    def validate_request(self):
        for payment in self:
            inv_obj = self.env['account.invoice']
            product = self.env['product.product'].search([('name','=','Marketplace Seller Payment')], limit=1)
            partner_obj = self.env['res.partner']
            account_id = False
            if product:
                if not product.property_account_income_id:
                    account_id = product.categ_id.property_account_income_categ_id.id
                    #raise ValidationError(_('Please Configure Income and Expense Account for the Product'))
                else:
                    account_id = product.property_account_income_id.id

            vals = {
                # 'origin': payment.name,
                'type': 'in_invoice',
                # 'reference': False,
                'user_id' : self.env.user.id,
                # 'account_id': payment.seller_id.property_account_receivable_id.id,
                'partner_id': payment.seller_id.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id' : product.id,
                    'name': product.name,
                    # 'origin': payment.name,
                    'account_id': account_id,
                    'price_unit': payment.payable_amount, 
                    })],
                }
            
            invoice_id = inv_obj.sudo().create(vals)  

            
            invoice_id.sudo().action_post()

            
            payment_obj = self.env['account.payment']
            payment_method = self.env['account.payment.method'].sudo().search([],limit=1)
            journal_id = self.env['account.journal'].search([('type','=','purchase')],limit=1)
            
            if not journal_id:
                raise ValidationError(_('Please Define Type Purchase Journal !!'))

            res = payment_obj.sudo().create({
                        'partner_id':invoice_id.partner_id.id,
                        'amount': payment.payable_amount,
                        'payment_type':'outbound',
                        'partner_type':'supplier',
                        'payment_method_id' : payment_method.id,
                        'journal_id':journal_id.id,
                        'payment_date':fields.date.today(),
                        'communication':invoice_id.name,
                        'invoice_ids':[(6,0,[invoice_id.id])]
                        })
            
            invlist = invoice_id.invoice_line_ids.ids
            payment.write({
                'invoice_line_ids':[(6,0,invlist)],
                'state' : 'confirm',
                'invoice_id' : invoice_id.id,
                })


            
            sequence_code = 'account.payment.supplier.invoice'
            res.sudo().write({'name': self.env['ir.sequence'].sudo().with_context(ir_sequence_date=res.payment_date).next_by_code(sequence_code),})
            
            invoice_id.reconciled = True
            invoice_id.sudo().action_invoice_paid()
            
            pay_confirm = payment_obj.sudo().search([("communication","=",invoice_id.name)])
            for pay in pay_confirm:
                if not pay.state == 'posted':
                    pay.sudo().post()

            partner = partner_obj.sudo().browse(payment.seller_id.id)
            updated_amount = partner.seller_credit - payment.payable_amount
            partner.write({'seller_credit' : updated_amount,'last_payment_date':fields.Date.context_today(self)})

    def view_invoice(self):
        
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]

        res = self.env.ref('account.view_move_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = self.invoice_id.id
        result['domain'] = [
            ('type', 'in', ('in_invoice', 'in_refund')),
            ('id','=',self.invoice_id.id)
        ]
        result['context'] = {
            'default_type':'in_invoice', 'type':'in_invoice',
        }
        return result

    def unlink(self):
        for partner in self:
            if partner.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete an payment which is not draft or cancelled.'))
        return super(payment_seller, self).unlink()

class SellerPaymentMethod(models.Model):
    _name = 'seller.payment.method'
    _description = 'Seller Payment Method'

    name = fields.Char(string='Payment Ref Name',)


class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    seller_id = fields.Many2one('res.partner', "seller")


class StockMove(models.Model):
    _inherit = "stock.move"

    seller_id = fields.Many2one('res.partner', "seller",related="sale_line_id.product_id.product_tmpl_id.seller_id", store=True)

class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'


    def action_invoice_paid(self):
        # lots of duplicate calls to action_invoice_paid, so we remove those already paid
        res = super(AccountInvoiceInherit, self).action_invoice_paid()
        
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if not active_id or active_model != 'account.invoice':
            return res
        invoices = self.env['account.invoice'].browse(active_id)
        config_id = self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        partner_obj = self.env['res.partner']
        for invoice in invoices:
            if invoice.state == 'posted':
                for line in invoice.invoice_line_ids:
                    if line.product_id.product_tmpl_id.seller_id:
                        if line.pay_done == False:
                            total = credit = commission = 0.0
                            partner = partner_obj.browse(line.product_id.product_tmpl_id.seller_id.id)
                            credit = partner.seller_credit  

                            if partner.overwrite_setting == True:
                                commission = partner.seller_commission
                                total = (line.price_total - ((line.price_total * partner.seller_commission)/100))
                                partner.write({'seller_credit' : ( credit + abs(total) )})
                                line.write({'pay_done':True})
                            elif config_id.is_commission == True:  
                                commission = config_id.commission_value                              
                                total = (line.price_total - ((line.price_total * config_id.commission_value)/100))
                                partner.write({'seller_credit' : ( credit + abs(total) )})
                                line.write({'pay_done':True})
                            else:
                                total = line.price_total
                                partner.write({'seller_credit' : ( credit + abs(line.price_total) )})
                                line.write({'pay_done':True})
      
                            payment_obj = self.env['seller.payment']
                        
                            vals = {
                                'seller_id' : partner.id,
                                'payment_mode' : 'seller_payment',
                                'date' : fields.Date.context_today(self),
                                'payment_type' : 'credit',
                                'state' : 'confirm',
                                'payable_amount' : total,
                                'seller_commission' : commission,
                                'company_id' :  self.env.user.company_id.id,
                                'currency_id' : self.env.user.company_id.currency_id.id,
                            }
                            
                            payment_id = payment_obj.sudo().create(vals)
                            payment_id.write({
                                'invoice_line_ids':[(6,0,[line.id])],
                                })

        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    pay_done = fields.Boolean('Done Payment',default=False)