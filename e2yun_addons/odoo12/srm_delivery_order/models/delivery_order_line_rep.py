from odoo import models, fields, tools,api,exceptions


class delivery_order_line_rep(models.Model):

    _name = "delivery.order.line.report"
    _table = "delivery_order_line_report"
    _description = "Read the Delivery Order Line."
    _auto = False
    _order = " dnnum "

    STATE_SELECTION = [
        ('supplier_create', 'Supplier Create'),
        ('print', 'Print'),
        ('supplier_cancel', 'Supplier Cancel'),
        ('purchase_cancel', 'Purchase Cancel'),
        ('purchase_lock', 'Purhase Lock'),
        ('Finished', 'Finished'),
    ]
    dnnum = fields.Char('Delivery Order', readonly=True)
    dline = fields.Char('Delivery Order Line', readonly=True)
    datoo = fields.Date('Demand Date', readonly=True)
    prefix_code = fields.Char('Matnr Code', readonly=True)
    matnrname = fields.Char('Matnr Name', readonly=True)
    meins =  fields.Char('Unit', readonly=True)
    dnmng = fields.Integer('Need Delivery Qty', required=True)
    sdmng = fields.Integer('Scheduling Qty', readonly=True)
    admng = fields.Integer('Already Delivery Qty', readonly=True)
    werks = fields.Char('Factory', required=True)
    lifnr = fields.Char( 'Supplier')
    supplier_code = fields.Char( 'Supplier Code')
    supplier_name = fields.Char( 'Supplier Name')
    ponum = fields.Char('Purchase Order', readonly=True)
    pline = fields.Char('Purchase Order Line ID', readonly=True)
    prnum = fields.Char('Product Order', readonly=True)
    menge = fields.Integer('PO Delivery Qty', readonly=True)
    state = fields.Selection(STATE_SELECTION, 'Status', track_visibility='onchange')
    senddate = fields.Char('Send Date', readonly=True)
    isinvalid = fields.Boolean('Is Invalid')

    def search(self,args, offset=0, limit=None, order=None, count=False):
        lifnr = self.env['res.users']._get_default_supplier()
        if lifnr > 0:
            args += [('lifnr', '=', lifnr)]

        return super(delivery_order_line_rep, self).search(args, offset=offset, limit=limit, order=order,count=count)


    def init(self):
        tools.drop_view_if_exists(self._cr, 'delivery_order_line_report')
        self._cr.execute("""
            create or replace view delivery_order_line_report as (
                 select concat(dpo.id,mo.id) as id, d.dnnum as dnnum,d.state as state,d.datoo as datoo,pt.default_code as prefix_code,pt.name as matnrname,pu.name as meins,
                    l.id as dline,l.dnmng,l.sdmng,dpo.done_menge as admng,w.name as werks,l.lifnr,rp.supplier_code as supplier_code ,rp.name as supplier_name,po.name as ponum,pol.item as pline,
                    dpo.menge as menge,mo.prnum as prnum,d."printSendDate" as senddate,l.isinvalid
                    from delivery_order d 
                    inner join delivery_order_line l on d.id = l.delivery_order_id
                    inner join delivery_purchase_orders dpo on dpo.delivery_order_line_id = l.id
                    inner join purchase_order po on dpo.ponum = po.id
                    inner join purchase_order_line pol on dpo.pline = pol.id
                    left join delivery_product_orders mo on mo.delivery_product_line_id = l.id 
                    left join product_product pr on pr.id = l.matnr
                    left join product_template pt on pt.id = pr.product_tmpl_id
                    left join uom_uom pu on pu.id = l.meins
                    left join stock_warehouse w on w.id = l.werks
                    left join res_partner rp on rp.id = l.lifnr
            )""")
