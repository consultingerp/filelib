# -*- coding: UTF-8 -*-
from odoo import models, fields
import odoo.addons.decimal_precision as dp



class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    delivery_qty = fields.Float('收货数量',digits=dp.get_precision('Product Unit of Measure'),default=0)