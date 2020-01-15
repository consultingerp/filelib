from odoo import models, fields, tools,api,exceptions
class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    delivery_qty = fields.Float('收货数量',default=0)
    no_more_gr = fields.Char(string='no more gr')  # 交货已完成标识