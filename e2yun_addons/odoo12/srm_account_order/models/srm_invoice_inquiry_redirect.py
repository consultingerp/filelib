
from odoo import models, fields


class srm_account_redirect(models.Model):
    _name = 'srm.redirect.account'

    def srm_account_inquiry_redirect(self):
        params = self._context.get('params')
        if params:
            account_id = params.get('account_id')
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/srm_inquiry_account/%d' % account_id + '/'
        }