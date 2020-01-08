from odoo import fields, models, api,_
from odoo.exceptions import Warning
import suds.client



class ModelName (models.Model):
    _inherit = 'res.partner'


    def go_to_customer_payment(self):
        ctx = self._context.copy()
        ctx['partner_id'] = self.id
        ctx['default_payment_type'] = 'inbound'
        ctx['default_partner_type'] = 'customer'

        result = 'S'
        if not self.shop_customer:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncMember?wsdl'  # webservice调用地址
            client = suds.client.Client(url)
            result = client.service.getSAPState(self.app_code or '')
        if result == 'S':
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'type': 'ir.actions.act_window',
                'context': ctx,
                # 'default': partner_id
            }
        else:
            raise Warning(_('客户状态不正确，请检查pos状态-%s') % result)
