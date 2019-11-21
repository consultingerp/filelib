from odoo import fields, models, api


class ModelName (models.Model):
    _inherit = 'res.partner'


    def go_to_customer_payment(self):
        ctx = self._context.copy()
        ctx['partner_id'] = self.id
        ctx['default_payment_type'] = 'inbound'
        ctx['default_partner_type'] = 'customer'
        # print('success')
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'context': ctx,
            # 'default': partner_id
        }
