# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions

class res_users(models.Model):
    _inherit = 'res.users'

    def _get_default_supplier(self):
        login_obj = self.browse(self._uid)
        supplier_id = 0
        sql = "select supplier_code,id from res_partner where supplier_code=%s and supplier=%s"
        self.env.cr.execute(sql,(login_obj.login,'t'))
        isf = self.env.cr.fetchone()
        if isf:
            supplier_id=isf[1]
        elif login_obj.partner_id.parent_id.supplier:
            supplier_id = login_obj.partner_id.parent_id.id
        return supplier_id