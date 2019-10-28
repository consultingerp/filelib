# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()

        login = request.env.user.login
        supplier = request.env['e2yun.supplier.info'].sudo().search([('login_name','=',login)],limit=1)
        if supplier:
            state = supplier.state
            values.update({
                'supplier_state': state,
            })

        return values

