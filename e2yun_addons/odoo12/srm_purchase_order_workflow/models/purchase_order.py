# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    STATE_SELECTION1 = [
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('bid', 'Bid Received'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('supply_confirm', 'Supplier Confirmed'),
        ('supply_refuse', 'Supplier Refuse'),
        ('supply_overdue', 'Supplier Overdue'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ]
    state = fields.Selection(STATE_SELECTION1, string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    email_supplier = fields.Boolean('Send Mail Supplier' ,readonly=True,default=False)

    # def wkf_approve_order(self):
    #     self.write({'state': 'approved','date_approve':fields.date.today()})
    #     if self.partner_id :
    #         partner = self.env['res.partner'].browse(self.partner_id.id)
    #
    #         if partner.order_confirm:
    #             config_set = self.pool.get('purchase.config.settings').search(self._cr,openerp.SUPERUSER_ID,[]);
    #             max_id = 0
    #             for pid in config_set:
    #                 if pid > max_id:
    #                     max_id = pid
    #             if max_id == 0:
    #                 return self.wkf_send_rfq()
    #             max_set = self.pool.get('purchase.config.settings').browse(self._cr,openerp.SUPERUSER_ID,max_id)
    #             if max_set and (not max_set.module_purchase_double_validation or max_set.limit_amount > self.amount_total):
    #                 return self.wkf_send_rfq()
    #         else:
    #             self.write({'state': 'supply_confirm'})


    #确认订单事件
    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.user.company_id.currency_id.compute(
                        order.company_id.po_double_validation_amount, order.currency_id)) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True


    #确认订单
    @api.multi
    def button_approve(self, force=False):
        state='purchase'
        for order in self:
             if order.partner_id.order_confirm and order.partner_id.order_confirm==True:
                 state='supply_confirm'

        self.write({'state':state, 'date_approve': fields.Date.context_today(self)})
        self._create_picking()
        self.filtered(
            lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
        return {}



    @api.multi
    def action_rfq_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            # if self.env.context.get('send_rfq', False):
            #     template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase')[1]
            # else:
            #     template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase_done')[1]
            template_id = ir_model_data.get_object_reference('srm_purchase_order_workflow', 'email_template_confim_purchase')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "purchase.mail_template_data_notification_email_purchase_order",
            'purchase_mark_rfq_sent': True,
            'force_email': True
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    # def wkf_send_rfq(self, cr, uid, ids, context=None):
    #     if not context:
    #         context= {}
    #     ir_model_data = self.pool.get('ir.model.data')
    #     try:
    #         if context.get('send_rfq', False):
    #             template_id = ir_model_data.get_object_reference(cr, openerp.SUPERUSER_ID, 'purchase', 'email_template_edi_purchase')[1]
    #         else:
    #             email_template = self.pool['email.template'].search(cr,openerp.SUPERUSER_ID,[('name', '=', 'Purchase Order - Send by Qweb Email')],context=context)
    #             for temp_id in email_template:
    #                 template_id = self.pool.get('email.template').browse(cr,openerp.SUPERUSER_ID,temp_id).id
    #             sql="update purchase_order set email_supplier='t' where id="+str(ids[0])+" "
    #             cr.execute(sql)
    #     except ValueError:
    #         template_id = False
    #     try:
    #         compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
    #     except ValueError:
    #         compose_form_id = False
    #     ctx = dict(context)
    #     ctx.update({
    #         'default_model': 'purchase.order',
    #         'default_res_id': ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #     })
    #     return {
    #         'name': _('Compose Email'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(compose_form_id, 'form')],
    #         'view_id': compose_form_id,
    #         'target': 'new',
    #         'context': ctx,
    #     }
    #
    # def action_cancel(self, cr, uid, ids, context=None):
    #     super(PurchaseOrder,self).action_cancel(cr,uid,ids,context=context)
    #     self.write(cr,uid,ids,{'email_supplier': False},context=context)
    #     order = self.browse(cr, uid, ids[0])
    #     if order.partner_id.purchae_order_cancel:
    #         ir_model_data = self.pool.get('ir.model.data')
    #         template_id = False
    #         try:
    #             email_template = self.pool['email.template'].search(cr, openerp.SUPERUSER_ID,[('name', '=', 'Purchase Order Cancel Send by Email')],context=context)
    #             for temp_id in email_template:
    #                 template_id = self.pool.get('email.template').browse(cr, openerp.SUPERUSER_ID, temp_id).id
    #         except ValueError:
    #             template_id = False
    #         try:
    #             compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
    #         except ValueError:
    #             compose_form_id = False
    #         ctx = dict(context)
    #         ctx.update({
    #             'default_model': 'purchase.order',
    #             'default_res_id': ids[0],
    #             'default_use_template': bool(template_id),
    #             'default_template_id': template_id,
    #             'default_composition_mode': 'comment',
    #         })
    #         return {
    #             'name': _('Compose Email'),
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'mail.compose.message',
    #             'views': [(compose_form_id, 'form')],
    #             'view_id': compose_form_id,
    #             'target': 'new',
    #             'context': ctx,
    #         }
    #
    # def picking_done(self, cr, uid, ids, context=None):
    #     self.write(cr, uid, ids, {'shipped':1,'state':'outgoing'}, context=context)
    #     # Do check on related procurements:
    #     proc_obj = self.pool.get("procurement.order")
    #     po_lines = []
    #     for po in self.browse(cr, uid, ids, context=context):
    #         po_lines += [x.id for x in po.order_line if x.state != 'cancel']
    #     if po_lines:
    #         procs = proc_obj.search(cr, uid, [('purchase_line_id', 'in', po_lines)], context=context)
    #         if procs:
    #             proc_obj.check(cr, uid, procs, context=context)
    #     self.message_post(cr, uid, ids, body=_("Products received"), context=context)
    #     return True




