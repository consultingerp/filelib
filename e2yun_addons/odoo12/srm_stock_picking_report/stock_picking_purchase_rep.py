# -*- coding: utf-8 -*-
from odoo import models, fields, tools, api, exceptions


class matnr_demand_exec(models.Model):
    _name = "stock.picking.purchase.report"
    _table = "stock_picking_purchase_report"
    _description = ""
    _auto = False

    STATE_SELECTION = [
        ('draft', 'New'),
        ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('assigned', 'Available'),
        ('done', 'Done'),
    ]
    purchase_line_id = fields.Many2one('purchase.order.line','po line')
    pickingname = fields.Char('Picking Name', readonly=True)
    matnr = fields.Many2one('product.product','Matnr', readonly=True)
    matnrname = fields.Char('Matnr', readonly=True)
    ponum = fields.Char('Purchase Order', required=True)
    product_qty = fields.Integer('Product Qty', required=True)
    complete_name = fields.Many2one('stock.location','Location Dest', required=True)
    bussinesfriend = fields.Many2one('res.partner','Bussines Friend')
    picking_type_id = fields.Many2one('stock.picking.type','作业类型')
    state = fields.Selection(STATE_SELECTION, 'Status')
    item = fields.Char('Purchase Order Item', related="purchase_line_id.item")

    def search(self, args, offset=0, limit=None, order=None, count=False):
        lifnr = self.env['res.users']._get_default_supplier()
        if lifnr > 0:
            args += [('lifnr', '=', lifnr)]

        return super(matnr_demand_exec, self).search(args, offset=offset, limit=limit, order=order,count=count)


    def init(self):
        tools.drop_view_if_exists(self._cr, 'stock_picking_purchase_report')
        self._cr.execute("""
                create or replace view stock_picking_purchase_report as (
                    select concat(m.id,p.id) as id, 
                        p.name as pickingname,
                        p.partner_id bussinesfriend,
                        m.product_qty,
                        m.product_id matnr,
                        '' matnrname,
                        m.location_dest_id complete_name,
                        m.purchase_line_id,
                        p.picking_type_id,
                        (select name from purchase_order po where po.id = (select order_id from purchase_order_line pol where pol.id = m.purchase_line_id)) ponum,
                        m.state 
                    from stock_picking p 
                    inner join stock_move m on p.id = m.picking_id
                    
                    order by p.write_date desc,p.name
                )
            """)
