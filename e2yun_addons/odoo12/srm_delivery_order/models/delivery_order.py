# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo import tools, _
import datetime


class delivery_order(models.Model):
    _name = 'delivery.order'
    _inherit = ['mail.thread']
    _description = "交货订单"

    STATE_SELECTION = [
        ('supplier_create', 'Supplier Create'),
        ('print', 'Print'),
        ('supplier_cancel', 'Supplier Cancel'),
        ('purchase_cancel', 'Purchase Cancel'),
        ('purchase_lock', 'Purhase Lock'),
        ('Finished', 'Finished'),
    ]

    HSTAT_SELECTION = [
        ('passage', 'Passage'),
        ('check', 'Check'),
        ('out_stock', 'Out Stock'),
        ('in_stock', 'In Stock'),
        ('allot', 'Allot Goods')
    ]

    def _default_werks(self):
        return int(self._context.get('werks'))

    def _default_datoo(self):
        return self._context.get('datoo')

    def _default_comco(self):
        return self.env['res.company']._company_default_get('delivery.order').id

    def _default_lifnr(self):
        return self.env['res.users']._get_default_supplier()

    @api.multi
    def _compute_supplier(self):

        for id in self.ids:
            obj = self.browse(id)
            supplier_code = self.env['res.users'].browse(self._uid).login
            partner_obj = self.env['res.partner'].search([('supplier_code', '=', supplier_code),
                                                          ('supplier', '=', True)])
            if partner_obj:
                obj.is_supplier = partner_obj.supplier

    dnnum = fields.Char("Delivery Order", copy=False, readonly=True)
    name = fields.Char("Name")
    comco = fields.Many2one('res.company', 'Company', required=True, readonly=True,default=_default_comco)
    werks = fields.Many2one('stock.warehouse', 'Factory', required=True, readonly=True,default=_default_werks)
    lifnr = fields.Many2one('res.partner', 'Supplier', required=False, readonly=True, domain=[('supplier', '=', True)],default=_default_lifnr)
    datoo = fields.Char('Demand Date', required=True, readonly=True,default=_default_datoo)
    state = fields.Selection(STATE_SELECTION, 'Status', track_visibility='onchange',default='supplier_create')
    hstat = fields.Selection(HSTAT_SELECTION, 'Goods Status', track_visibility='onchange', readonly="True",default='allot')
    prinu = fields.Integer("Print Count", readonly="True")
    boxnu = fields.Integer("Total Box Qty")
    delivery_order_line = fields.One2many('delivery.order.line', 'delivery_order_id', 'Delivery Order Line')
    is_supplier = fields.Boolean(compute=_compute_supplier)
    state_begin_lock = fields.Char('Pre-lock state')
    printSendDate = fields.Char('Print Send Date', readonly=True)
    prnum = fields.Char('Produce Order')

    pocondition = fields.Char('Purchase Order')
    pocondhideorshow = fields.Boolean('Pocondition field Show or Hide',default=True)



    # _defaults = {
    #     'comco': _default_comco,
    #     'lifnr': _default_lifnr,
    #     'state': 'supplier_create',
    #     'hstat': 'allot',
    #     'datoo': _default_datoo,
    #     'werks': _default_werks,
    #     'is_supplier':True,
    #     'pocondhideorshow':True
    # }
    _order = "dnnum desc"

    @api.model
    def create(self,vals):
        # vals['dnnum'] = self.pool.get('ir.sequence').next_by_code(cr, uid, 'delivery.order')
        # vals['name'] = vals['dnnum']
        dnnum = self.env['ir.sequence'].next_by_code('delivery.order')
        seqnum = int(dnnum[6:len(dnnum)]) - 1
        if seqnum-1000>=0:
            vals['dnnum'] = dnnum[0:6] + str(seqnum)
        elif seqnum-100>=0:
            vals['dnnum'] = dnnum[0:6] +'0'+str(seqnum)
        elif seqnum - 10>=0:
            vals['dnnum'] = dnnum[0:6] + '00' + str(seqnum)
        elif 10-seqnum>0:
            vals['dnnum'] = dnnum[0:6] + '000' + str(seqnum)
        vals['name'] = vals['dnnum']

        prnumArray = []
        allPrnum = []
        details_ids=[]
        if 'delivery_order_line' in vals.keys():
            orderLines = vals['delivery_order_line']
            for orderLine in orderLines:
                if len(orderLine)==3:
                    orderLine2 = orderLine[2]
                    if 'delivery_purchase_orders' in orderLine2.keys() and len(orderLine2['delivery_purchase_orders']) > 0 and len(orderLine2['delivery_purchase_orders'][0])>0 \
                            and orderLine2['delivery_purchase_orders'][0][0] != 0:
                        del (orderLine2['delivery_purchase_orders'][0])
                    if 'delivery_product_orders' in orderLine2.keys() and len(orderLine2['delivery_product_orders']) > 0 and len(orderLine2['delivery_product_orders'][0])>0\
                            and orderLine2['delivery_product_orders'][0][0] != 0:
                        del (orderLine2['delivery_product_orders'][0])
                    if 'delivery_product_orders'in orderLine2.keys():
                        productOrders = orderLine2['delivery_product_orders']
                        if len(productOrders)>0:
                            for productOrder in productOrders:
                                if  productOrder[2]['details_id'] not in details_ids:
                                    details_ids.append(productOrder[2]['details_id'])
                                if len(allPrnum)==0:
                                    allPrnum.append(productOrder[2]['prnum'])
                                elif productOrder[2]['prnum'] not in allPrnum:
                                    if 'source' in self._context.keys() and 'import' == self._context['source']:
                                        raise exceptions.ValidationError("The delivery order associated with the delivery order must be the same. "
                                                                         "Only all delivery lines are allowed to be associated with the same production order, "
                                                                         "or all delivery lines are not associated with the production order.")
                                    else:
                                        raise exceptions.ValidationError(
                                            "交货单中关联的生产订单必须相同。只允许所有的交货单行都关联同一个生产订单，或者所有的交货单行都不关联生产订单")
                                if len(productOrder)>=3 and  'prnum' in productOrder[2].keys():
                                    prnum = productOrder[2]['prnum']
                                    if prnum not in prnumArray and len(prnumArray)>0:
                                        if 'source' in self._context.keys() and 'import' == self._context['source']:
                                            raise exceptions.ValidationError("No more production orders are allowed in the delivery order.")
                                        else:
                                            raise exceptions.ValidationError(
                                                "交货单中不允许关联多个生产订单.")
                                    else:
                                        prnumArray.append(prnum)
                        else:
                            if  len(allPrnum)==0:
                                allPrnum.append(" ")
                            elif " " not in allPrnum :
                                if 'source' in self._context.keys() and 'import' == self._context['source']:
                                    raise exceptions.ValidationError("The delivery order associated with the delivery order must be the same. "
                                                                         "Only all delivery lines are allowed to be associated with the same production order, "
                                                                         "or all delivery lines are not associated with the production order.")
                                else:
                                    raise exceptions.ValidationError(
                                        "交货单中关联的生产订单必须相同。只允许所有的交货单行都关联同一个生产订单，或者所有的交货单行都不关联生产订单")

            if 'delivery_purchase_orders' not in orderLines[0][2]:
                raise exceptions.ValidationError("交货采购订单不能为空")

            orderLine_purchaseOrderLine=[]
            surplus_poLines = self.select_surplus_po(orderLines[0][2]['delivery_purchase_orders'][0][2]['lifnr'], orderLines[0][2]['delivery_purchase_orders'][0][2]['comco'],
                                                     orderLines[0][2]['werks'])

            demandQtyValues = []
            if len(details_ids)>0:
                demandQtyValues = self.get_demand_residual_qty(details_ids)

            if len(allPrnum)>0:
                if allPrnum[0]== " ":
                    vals['prnum'] =''
                else:
                    vals['prnum'] = allPrnum[0]

            if len(orderLines)>0:
                for i,orderLineindex in enumerate(orderLines):
                    orderLine = orderLineindex[2]
                    purchaseLines = orderLine['delivery_purchase_orders']
                    for purchaseLine in purchaseLines:
                        orderLine_purchaseOrderLine.append(purchaseLine)
                        for surplus_poLine in surplus_poLines:
                            if purchaseLine[2]['ponum'] == surplus_poLine['ponum'] and purchaseLine[2]['pline'] == surplus_poLine['pline'] and purchaseLine[2]['matnr'] == surplus_poLine['matnr']  :
                                num = int(surplus_poLine['menge']) - int(purchaseLine[2]['menge'])
                                if num>=0:
                                    surplus_poLine['menge']= num
                                elif num < 0:
                                    poname = self.env["purchase.order"].browse(purchaseLine[2]['ponum']).name
                                    item = self.env["purchase.order.line"].browse(purchaseLine[2]['pline']).item
                                    if 'source' in self._context.keys() and 'import' == self._context['source']:
                                        raise exceptions.ValidationError("""Line %s of the delivery order, associated purchase order %s, the number of line items %s is greater than the number of outstanding %s."""%(str(i+1),poname,item,str(abs(num))))
                                    else:
                                        raise exceptions.ValidationError(_(
                                            """交货单第%s行,关联的采购订单%s,行项目%s数量已经大于未清数量%s个.""" % (str(i + 1), poname, item, str(abs(num)))))

                    if 'delivery_product_orders' in orderLine.keys():
                        productLines = orderLine['delivery_product_orders']
                        for productLine in productLines:
                            for demandQty in demandQtyValues:
                                if productLine[2]['details_id'] == demandQty['details_id']:
                                    num = demandQty['penge'] - productLine[2]['penge']
                                    if num >= 0:
                                        demandQty['penge'] = num
                                    elif num < 0:
                                        prefix_code = self.env["product.product"].browse(demandQty['matnr']).default_code
                                        if 'source' in self._context.keys() and 'import' == self._context['source']:
                                            raise exceptions.ValidationError("""No%s, Product Order: %s matnr: %s qty  is larger than the remaining qty"""%(str(i+1),demandQty['prnum'],str(prefix_code)) )
                                        else:
                                            raise exceptions.ValidationError("""第%s行,生产订单:%s 的物料:%s匹配数量已经大于需求剩余数量."""%(str(i+1),demandQty['prnum'],str(prefix_code)))




            if len(orderLine_purchaseOrderLine)>333:
                if 'source' in self._context.keys() and 'import' == self._context['source']:
                    raise exceptions.ValidationError('The maximum number of purchase order items associated with a single delivery item is 333 rows.')
                else:
                    raise exceptions.ValidationError('交货单行项目关联的采购订单行项目最大数为333行.')
        else:
            raise exceptions.ValidationError('交货单行项目不能为空')

        id = super(delivery_order, self).create(vals)
        return id

    def write(self,vals):
        if 'delivery_order_line' in vals.keys():
            deliveryPos=[]
            delivery_order_line_ids =[]
            for delivery_order_line in vals['delivery_order_line']:
                if delivery_order_line[0]==0:
                    sql = " select count(1) from delivery_order d "\
                        " inner join delivery_order_line dl on d.id = dl.delivery_order_id "\
                        " inner JOIN delivery_product_orders dpl on dl.id = dpl.delivery_product_line_id "\
                        " where d.id =%s"
                    self._cr.execute(sql,self.ids)
                    count = self._cr.fetchone()
                    if count[0] > 0:
                        raise exceptions.ValidationError("交货单行已经关联生产订单，不允许再创建不关联生产订单的行！")

                if isinstance(delivery_order_line[2], (dict)) and 'dnmng' in delivery_order_line[2].keys() and vals['delivery_order_line'][0][0]==1:
                    if 'delivery_purchase_orders' in delivery_order_line[2].keys():
                        dnmng = delivery_order_line[2]['dnmng']
                        sumPoNum = 0
                        deliveryPo={}
                        delivery_order_line_ids.append(delivery_order_line[1])
                        for delivery_po_order in delivery_order_line[2]['delivery_purchase_orders']:
                            dpo = self.env['delivery.purchase.orders'].browse(delivery_po_order[1])
                            menge=0
                            if isinstance(delivery_po_order[2], (dict)) and 'menge' in delivery_po_order[2].keys():
                                sumPoNum += delivery_po_order[2]['menge']
                                menge = delivery_po_order[2]['menge']
                            else:
                                if delivery_po_order[0]!=2:#2表示删除，删除的不需要累加
                                    sumPoNum+=dpo['menge']
                                    menge=dpo['menge']
                        if sumPoNum!=dnmng:
                            raise exceptions.ValidationError("交货数量必须与关联的采购订单数量相等")
                    else:
                        raise exceptions.ValidationError("修改交货数量时请同时修改关联的采购订单数量！")

        return super(delivery_order, self).write(vals)

    def select_surplus_po(self,lifnr, comco,werks):
        line =[]
        if not werks:
            werks = self._context['werks']
        werks = int(werks)
        order_sql = "select h.id as order_id,l.id as line_id,coalesce(l.product_qty,0) - coalesce(l.delivery_qty,0) as product_qty,l.date_planned,l.product_id,h.picking_type_id " \
                    ",case when l.item is not null then l.item else ''||l.id end as item from purchase_order h " \
                    " inner join purchase_order_line l on h.id = l.order_id " \
                    " where l.NO_MORE_GR is null AND h.partner_id = %s and h.company_id = %s  " \
                    " and h.state = 'supply_confirm' and h.location_id = (select lot_stock_id from stock_warehouse where id = %s ) " \
                    " order by h.id "
        self._cr.execute(order_sql, (lifnr, comco, werks))
        order_dicts = self._cr.dictfetchall()

        for od in order_dicts:
            # 查询PO已创建交货单数量
            po_sql = "select sum(menge) from delivery_purchase_orders o " \
                     "inner join delivery_order_line l on l.id = o.delivery_order_line_id " \
                     "inner join delivery_order h on h.id = l.delivery_order_id " \
                     "where h.state in ('supplier_create','print') " \
                     "and o.ponum = %s and o.pline = %s "
            self._cr.execute(po_sql, (od['order_id'], od['line_id']))
            pomenge = self._cr.fetchone()
            if not pomenge[0]:
                pomenge = 0
            else:
                pomenge = pomenge[0]

            if  od['product_qty'] - pomenge > 0:
                line.append({
                    'ponum': od['order_id'],
                    'pline': od['line_id'],
                    'menge': od['product_qty'] - pomenge,
                    'old_menge': od['product_qty'] - pomenge,
                    'matnr': od['product_id'],
                    'werks': werks,
                    'ddate': od['date_planned'],
                    'comco': comco,
                    'lifnr': lifnr,
                    'item': od['item']
                })
        return line

    def get_demand_residual_qty(self,details_ids):
        details_strs = ""
        for i, details_id in enumerate(details_ids):
            if i == len(details_ids) - 1:
                details_strs += str(details_id)
            else:
                details_strs += str(details_id) + ","
        demandsql = "select details_id, prnum, menge, ddate, lifnr, matnr, aprng, menge - COALESCE(aprng,0) AS penge  " \
                    "from (SELECT md.ID AS details_id,prnum, menge,ddate, lifnr,matnr, " \
                    "(SELECT SUM(case when d.state in ('supplier_create','print') then penge else done_menge end) FROM delivery_product_orders dp " \
                    " INNER JOIN delivery_order_line dl on dp.delivery_product_line_id = dl.id " \
                    " INNER JOIN delivery_order d on d.id=dl.delivery_order_id  " \
                    " INNER JOIN delivery_purchase_orders on delivery_order_line_id = dl.id 	" \
                    " where dp.details_id = md.ID and d.state in ('supplier_create','print','Finished')) AS aprng " \
                    " FROM mat_demand_line_details md inner join mat_demand_head h on md.mat_demand_id =h.id where h.state='publish' and  md.state in ('create','supplier_confirm','supplier_edit','purchase_edit','purchase_confirm', 'not_confirm') and " \
                    " md.id in ("+details_strs+")  )t where menge - COALESCE ( aprng, 0 )>0  "
        self._cr.execute(demandsql)
        productLine = self._cr.dictfetchall()
        return productLine

    def dnnum_sequence_reset(self):
        self._cr.execute("select id from ir_sequence  where code='delivery.order'")
        id = self._cr.fetchone()
        if id:
            sql = ("select setval('ir_sequence_%03d',1)" %id)
            self._cr.execute(sql)


    def unlink(self):
        for id in self.ids:
            order = self.browse(id)
            if order.state == 'print' or order.state == 'Finished':
                raise exceptions.ValidationError("打印或完成状态下的单据不允许删除")

        super(delivery_order, self).unlink()

    @api.onchange('werks')
    def onchange_werks(self):
        result = {}
        context = dict(self._context or {})
        werks = int(context.get('werks'))
        comco = self.env['res.company']._company_default_get('delivery.order').id
        lifnr = self.env['res.users']._get_default_supplier()
        datoo = context.get('datoo')


        versi = context['versi']
        prnum = context['prnum'] if 'prnum' in context else False

        if context['isscheduledate'] == False :
            result['delivery_order_line'] = []
            result['is_edit_mantr'] = True
            result['pocondhideorshow'] =False
            return {'value': result}
        if werks and comco and lifnr and datoo:
            sql = "select matnr,(select product_tmpl_id from product_product where id = l.matnr) as tmpl_id,ekgrp,meins,prnum,monum,bmeng as bmeng,h.id as version_id,l.id as line_version_id" \
                  " from mat_demand_head h inner join mat_demand_line_details l " \
                  " on h.id = l.mat_demand_id " \
                  " where h.comco = %s and h.werks = %s and l.lifnr = %s and versi=%s and l.ddate = %s " \
                  " and h.state = 'publish' and (l.state = 'not_confirm' or l.delivery = True) "
            if prnum:
                sql += """ and l.prnum = '"""+prnum+"""'"""

            #" and h.history_data = False "
            # and l.state in ('supplier_confirm','not_confirm')
            self._cr.execute(sql, (comco, werks, lifnr,versi,datoo))
            dicts = self._cr.dictfetchall()
            order_line = []
            for d in dicts:
                # 查询物料已交货数
                sql = "select done_menge,menge,h.state  from delivery_order h inner join delivery_order_line l " \
                      " on h.id = l.delivery_order_id" \
                      " inner join delivery_purchase_orders p on p.delivery_order_line_id = l.id  " \
                      " where h.comco = %s and h.werks = %s and h.lifnr = %s and l.matnr = %s" \
                      " and h.datoo = %s and l.version_id = %s and l.line_version_id = %s and h.state in ('supplier_create','print','Finished')"
                self._cr.execute(sql, (comco, werks, lifnr, d['matnr'], datoo,d['version_id'],d['line_version_id']))
                haveDeliverys  = self._cr.dictfetchall()
                admng=0
                for haveDelivery in haveDeliverys:
                    if haveDelivery['state']=='supplier_create' or haveDelivery['state']=='print' :
                        admng +=haveDelivery['menge']
                    elif haveDelivery['state']=='Finished':
                        admng +=haveDelivery['done_menge']



                dnmng = d['bmeng']
                if admng:
                    dnmng = dnmng - admng

                if dnmng > 0:
                    line = []
                    productLine = []
                    supplier_self = self.env['product.supplierinfo']
                    supplierinfo = supplier_self.search(
                                                        [('product_tmpl_id', '=', d['tmpl_id']), ('name', '=', lifnr)])
                    auto_sel = supplierinfo.automatic_selection
                    if supplierinfo and len(supplierinfo) == 1:
                        # 查询物料对应的采购订单
                        order_sql = "select h.id as order_id,l.id as line_id,coalesce(l.product_qty,0) - coalesce(l.delivery_qty,0) as product_qty,l.date_planned,l.product_id,h.picking_type_id " \
                                    ",case when l.item is not null then l.item else ''||l.id end as item from purchase_order h " \
                                    " inner join purchase_order_line l on h.id = l.order_id " \
                                    " left JOIN stock_move sm ON sm.purchase_line_id = l.id and sm.location_dest_id in (select id from stock_location where usage='internal')  " \
                                    " left JOIN stock_picking sp ON sp.ID = sm.picking_id " \
                                    " where l.NO_MORE_GR is null AND h.partner_id = %s and h.company_id = %s  " \
                                    " and h.state = 'supply_confirm'and sp.state='assigned' and l.product_id = %s and h.location_id = (select lot_stock_id from stock_warehouse where id = %s ) "

                        if context['isscheduledate']:
                            order_sql += " and h.name not like '5%%'  and h.name not like '92%%'"
                        order_sql+=" order by h.id "
                        self._cr.execute(order_sql, (lifnr, comco, d['matnr'], werks))
                        order_dicts = self._cr.dictfetchall()
                        calculate_dnmng = dnmng

                        for od in order_dicts:
                            # 查询PO已创建交货单数量
                            po_sql = "select sum(menge) from delivery_purchase_orders o " \
                                     "inner join delivery_order_line l on l.id = o.delivery_order_line_id " \
                                     "inner join delivery_order h on h.id = l.delivery_order_id " \
                                     "where h.state in ('supplier_create','print') " \
                                     "and o.ponum = %s and o.pline = %s "
                            self._cr.execute(po_sql, (od['order_id'], od['line_id']))
                            pomenge = self._cr.fetchone()
                            if not pomenge[0]:
                                pomenge = 0
                            else:
                                pomenge = pomenge[0]

                            if calculate_dnmng > 0 and od['product_qty'] - pomenge > 0:
                                if auto_sel == True:
                                    if od['product_qty'] - pomenge > calculate_dnmng:
                                        line.append({
                                            'ponum': od['order_id'],
                                            'pline': od['line_id'],
                                            'menge': calculate_dnmng,
                                            'old_menge': calculate_dnmng,
                                            'matnr': od['product_id'],
                                            'werks': werks,
                                            'ddate': od['date_planned'],
                                            'comco': comco,
                                            'lifnr': lifnr,
                                            'item':od['item']
                                        })
                                        calculate_dnmng = 0
                                    else:
                                        line.append({
                                            'ponum': od['order_id'],
                                            'pline': od['line_id'],
                                            'menge': od['product_qty'] - pomenge,
                                            'old_menge': od['product_qty'] - pomenge,
                                            'matnr': od['product_id'],
                                            'werks': werks,
                                            'ddate': od['date_planned'],
                                            'comco': comco,
                                            'lifnr': lifnr,
                                            'item': od['item']
                                        })
                                        calculate_dnmng = calculate_dnmng - od['product_qty'] - pomenge
                                else:
                                    line.append({
                                        'ponum': od['order_id'],
                                        'pline': od['line_id'],
                                        'menge': od['product_qty']- pomenge,
                                        'old_menge':od['product_qty'] - pomenge,
                                        'matnr': od['product_id'],
                                        'werks': werks,
                                        'ddate': od['date_planned'],
                                        'comco': comco,
                                        'lifnr': lifnr,
                                        'item': od['item']
                                    })
                        demandsql = "select details_id, prnum, menge, ddate, lifnr, matnr, aprng, menge - COALESCE(aprng,0) AS penge ,menge - COALESCE(aprng,0) as max_menge "\
                                "from (SELECT md.ID AS details_id,prnum, menge,ddate, lifnr,matnr, "\
                                "(SELECT SUM(case when d.state in ('supplier_create','print') then penge else done_menge end) FROM delivery_product_orders dp "\
                                " INNER JOIN delivery_order_line dl on dp.delivery_product_line_id = dl.id "\
                                " INNER JOIN delivery_order d on d.id=dl.delivery_order_id  "\
                                " INNER JOIN delivery_purchase_orders on delivery_order_line_id = dl.id 	"\
                                " where dp.details_id = md.ID and d.state in ('supplier_create','print','Finished')) AS aprng "\
                                " FROM mat_demand_line_details md inner join mat_demand_head h on md.mat_demand_id =h.id where h.state='publish' and  md.state in ('create','supplier_confirm','supplier_edit','purchase_edit','purchase_confirm', 'not_confirm') and " \
                                " ddate = %s and matnr = %s and lifnr=%s and versi=%s  )t where menge - COALESCE ( aprng, 0 )>0  "

                        if prnum:
                            demandsql +=  """ and prnum = '"""+prnum+"""'"""

                        self._cr.execute(demandsql, (datoo,d['matnr'] ,lifnr,versi))
                        productLine = self._cr.dictfetchall()
                    ol = {
                        'matnr': d['matnr'],
                        'ekgrp': d['ekgrp'],
                        'meins': d['meins'],
                        'prnum': d['prnum'],
                        'monum': d['monum'],
                        'version_id': d['version_id'],
                        'line_version_id': d['line_version_id'],
                        'comco': comco,
                        'lifnr': lifnr,
                        'dnmng': dnmng,
                        'max_dnmng': dnmng,
                        'sdmng': d['bmeng'],
                        'admng': admng,
                        'werks': werks
                    }
                    if len(line) > 0:
                        ol['delivery_purchase_orders'] = line
                    if len(productLine)> 0:
                        ol['delivery_product_orders'] = productLine
                    if auto_sel:
                        ol['atsel'] = True
                    order_line.append(ol)

            result['delivery_order_line'] = order_line
            result['is_edit_mantr'] = True
            result['pocondhideorshow'] = True

            return {'value': result}

        return {}

    def onchange_pocondition(self, werks, comco, lifnr, datoo,pocondition):
        result = {}
        if werks and comco and lifnr and datoo and pocondition:
            pocondition = pocondition.replace(' ','').replace('，',',')
            poconditionArray = pocondition.split(',')
            poonditionStr = ''
            for i,poconditionindex in enumerate(poconditionArray):
                if len(poconditionArray) == i+1:
                    poonditionStr +="'"+poconditionArray[i]+"'"
                else:
                    poonditionStr +="'"+poconditionArray[i]+"',"

            sql = "select h.id as order_id,l.id as line_id,coalesce(l.product_qty,0) - coalesce(l.delivery_qty,0) as product_qty,l.date_planned,l.product_id,h.picking_type_id ,case when l.item is not null then l.item else ''||l.id end as item from purchase_order h  "\
                " inner join purchase_order_line l on h.id = l.order_id  " \
                " left JOIN stock_move sm ON sm.purchase_line_id = l.id " \
                " left JOIN stock_picking sp ON sp.ID = sm.picking_id " \
                "where h.name in ("+poonditionStr+") "\
                "and h.state = 'supply_confirm' and sp.state='assigned' "\
                "and h.location_id = (select lot_stock_id from stock_warehouse where id = %s ) "\
                "and l.NO_MORE_GR is null  "\
                "AND h.partner_id =%s "
            self._cr.execute(sql, (werks, lifnr))
            podicts = self._cr.dictfetchall()
            if len(podicts)==0:
                result['pocondhideorshow'] = False
                return {'value': result}
            order_line = []
            new_podicts = []
            matnrs = []
            for poline in podicts:
                if poline['product_id'] not in matnrs:
                    matnrs.append(poline['product_id'])
                    new_podicts.append(poline)


            for poline in new_podicts:
                line = []
                self._cr.execute("select product_tmpl_id from  product_product where id=%(matnr)s ",
                           {'matnr': poline["product_id"]})
                tmpl_id = self._cr.fetchone()
                self._cr.execute("select uom_id from  product_template where id=%(tmpl_id)s ", {'tmpl_id': tmpl_id})
                menin = self._cr.fetchone()
                order_sql = "select h.id as order_id,l.id as line_id,coalesce(l.product_qty,0) - coalesce(l.delivery_qty,0) as product_qty,l.date_planned,l.product_id,h.picking_type_id, " \
                            " case when l.item is not null then l.item else ''||l.id end as item from purchase_order h " \
                            " inner join purchase_order_line l on h.id = l.order_id " \
                            " left JOIN stock_move sm ON sm.purchase_line_id = l.id and sm.location_dest_id in (select id from stock_location where usage='internal') " \
                            " left JOIN stock_picking sp ON sp.ID = sm.picking_id " \
                            " where l.NO_MORE_GR is null AND h.partner_id = %s and h.company_id = %s  " \
                            " and h.state = 'supply_confirm' and sp.state='assigned' and l.product_id = %s and h.location_id = (select lot_stock_id from stock_warehouse where id = %s ) " \
                            " order by h.id "
                self._cr.execute(order_sql, (lifnr, comco, poline["product_id"], werks))
                order_dicts = self._cr.dictfetchall()

                for od in order_dicts:
                    po_sql = "select sum(menge) from delivery_purchase_orders o " \
                             "inner join delivery_order_line l on l.id = o.delivery_order_line_id " \
                             "inner join delivery_order h on h.id = l.delivery_order_id " \
                             "where h.state in ('supplier_create','print') " \
                             "and o.ponum = %s and o.pline = %s "
                    self._cr.execute(po_sql, (od['order_id'], od['line_id']))
                    pomenge = self._cr.fetchone()
                    if not pomenge[0]:
                        pomenge = 0
                    else:
                        pomenge = pomenge[0]

                    if od['product_qty'] - pomenge > 0:
                        line.append({
                            'ponum': od['order_id'],
                            'pline': od['line_id'],
                            'menge': od['product_qty'] - pomenge,
                            'old_menge': od['product_qty'] - pomenge,
                            'matnr': od['product_id'],
                            'werks': werks,
                            'ddate': od['date_planned'],
                            'comco': comco,
                            'lifnr': lifnr,
                            'item': od['item']
                        })
                ol = {
                    'matnr': poline["product_id"],
                    'ekgrp': '',
                    'meins': menin[0],
                    'prnum': '',
                    'monum': 0,
                    'version_id': '',
                    'line_version_id': '',
                    'comco': comco,
                    'lifnr': lifnr,
                    'dnmng': 0,
                    'sdmng': 0,
                    'admng': 0,
                    'werks': werks
                }
                if len(line) > 0:
                    ol['delivery_purchase_orders'] = line
                order_line.append(ol)

            result['delivery_order_line'] = order_line
            result['is_edit_mantr'] = True
            result['pocondhideorshow'] = False
            return {'value': result}
        return {}


    def search(self,args, offset=0, limit=None, order=None, count=False):
        comco = self.env['res.company']._company_default_get('delivery.order')
        lifnr = self.env['res.users']._get_default_supplier()
        if lifnr > 0:
            args += [('lifnr', '=', lifnr)]
        args += [('comco', '=', comco.id)]

        return super(delivery_order, self).search(
            args, offset=offset, limit=limit, order=order,
            count=count)

    # @api.multi
    def order_lock(self):

        iswarehouse = self.valid_user_iswarehouser()
        if iswarehouse:
            raise exceptions.ValidationError("仓库用户无操作权限")
        self.write({'state': 'purchase_lock','state_begin_lock':self.state})

    # @api.multi
    def order_cancel_lock(self):
        self.write({'state': self.state_begin_lock,'state_begin_lock':''})

    def order_cancel(self,):
        iswarehouse = self.valid_user_iswarehouser()
        if iswarehouse:
            raise exceptions.ValidationError("仓库用户无操作权限。")
        supplier_id = self.env['res.users']._get_default_supplier()

        if supplier_id > 0:
            self.state = 'supplier_cancel'
        else:
            self.state = 'purchase_cancel'

    @api.multi
    def order_print(self):
        today = datetime.datetime.today()
        weekday = datetime.datetime.isoweekday(today)
        printSendDate = today.strftime('%Y-%m-%d')
        # if weekday == 7:
        #     mondayDay = today + datetime.timedelta(days=1)
        #     printSendDate = mondayDay.strftime('%Y-%m-%d')
        # elif weekday == 6:
        #     mondayDay = today + datetime.timedelta(days=2)
        #     printSendDate = mondayDay.strftime('%Y-%m-%d')
        sql = "SELECT dp.prnum FROM delivery_product_orders dp "\
                    "INNER JOIN delivery_order_line dl on dp.delivery_product_line_id = dl.id  "\
                    "INNER JOIN  delivery_order d on d.id=dl.delivery_order_id  "\
                    "where d.id= %(order_id)s" 
        self._cr.execute(sql, {'order_id':self.ids[0]})
        prnum =''
        dataPrnum= self._cr.fetchone()
        if dataPrnum:
            prnum = str(dataPrnum[0])

        sql = "select count(1) from srm_pack where dnnum=%(dnnum)s and name like '%%-%%'"
        self._cr.execute(sql, {'dnnum': str(self.name)})
        boxnum = 0
        dataBoxnum = self._cr.fetchone()
        if dataBoxnum:
            boxnum = str(dataBoxnum[0])

        self.write({'state': 'print', 'hstat': 'passage', 'prinu': self.prinu + 1,'printSendDate':printSendDate,'boxnu':boxnum})

        return self.env.ref('srm_delivery_order.report_srm_delivery_quotation').report_action(self)
        #return self.env['report'].get_action('srm_delivery_order.report_delivery')

    def order_recovery(self):
        surplus_poLines = self.select_surplus_po(self.lifnr.id,self.comco.id,self.werks.id)
        orderLines = self.delivery_order_line
        orderLine_purchaseOrderLine = []
        errorNum =0
        errormsg = {}
        if len(orderLines) > 0:
            for i, orderLineindex in enumerate(orderLines):
                purchaseLines = orderLineindex.delivery_purchase_orders
                for purchaseLine in purchaseLines:
                    orderLine_purchaseOrderLine.append(purchaseLine)
                    matchingNum = 0
                    for surplus_poLine in surplus_poLines:
                        if purchaseLine.ponum.id == surplus_poLine['ponum'] and purchaseLine.pline.id == \
                                surplus_poLine['pline'] and purchaseLine.matnr.id == surplus_poLine['matnr']:
                            matchingNum+=1
                            num = int(surplus_poLine['menge']) - int(purchaseLine.menge)
                            if num >= 0:
                                surplus_poLine['menge'] = num
                            elif num < 0:
                                errorNum +=1
                                key = purchaseLine.ponum.name+purchaseLine.pline.item
                                if key not in errormsg.keys():
                                    errormsg[key]= "采购订单："+str(purchaseLine.ponum.name)+"，行项目"+str(purchaseLine.pline.item)+"，"
                    if matchingNum==0:
                            errorNum += 1
                            key = purchaseLine.ponum.name + purchaseLine.pline.item
                            if key not in errormsg.keys():
                                errormsg[key] = "采购订单：" + str(purchaseLine.ponum.name) + "，行项目" + str(
                                    purchaseLine.pline.item)+"，"

        if len(orderLine_purchaseOrderLine) > 333:
            raise exceptions.ValidationError('交货单行项目关联的采购订单行项目最大数为333行！')

        if(errorNum>0):
            sumerrormsg = ""
            for value in errormsg.values():
                sumerrormsg += value
            raise exceptions.ValidationError('当前交货单关联的'+sumerrormsg+'已经超过最大数量，不允许恢复！')
        else:
            self.write({'state': 'supplier_create'})




    def valid_user_iswarehouser(self):
        sql = (" select count(1) from res_groups_users_rel "
               "where uid=%(uid)s and gid in (select id from res_groups where "
               "category_id in (select id from ir_module_category where  name ='Warehouse'))")
        param ={
            'uid':self._uid
        }
        self._cr.execute(sql,param)
        value = self._cr.fetchone()
        if value[0]> 0:
            return True
        return False

    @api.multi
    def delivery_pack(self):
        id2 = self.env.ref('srm_pack.srm_pack_form')
        return {
            'name': _('Packing'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'srm.pack',
            'views': [(id2.id, 'form')],
            'context':{'dnnum':self.dnnum,'lifnr':self.lifnr.id,'werks':self.werks.id},
            'view_id': id2.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }


class delivery_order_line(models.Model):
    _name = 'delivery.order.line'
    _description = u"交货订单行"

    @api.multi
    @api.depends('delivery_purchase_orders')
    def _compute_aomng(self):
        for s in self:
            total_qty = 0
            for order in s.delivery_purchase_orders:
                total_qty += order.done_menge
            if total_qty > 0:
                s.aomng = total_qty

    delivery_order_id = fields.Many2one('delivery.order', 'Delivery Order', required=True, readonly=True,
                                        ondelete='cascade')
    matnr = fields.Many2one('product.product', 'Material', required=True, domain=[('purchase_ok', '=', True)],
                            readonly=True)
    ekgrp = fields.Many2one('product.category', 'Purchase Group', domain="[('type','=','view')]")
    dnmng = fields.Integer('Need Delivery Qty', required=True)
    max_dnmng = fields.Integer('Max Delivery Qty', readonly=True)
    sdmng = fields.Integer('Scheduling Qty', readonly=True)
    admng = fields.Integer('Already Delivery Qty', readonly=True)
    aomng = fields.Integer('Already Out Qty', readonly=True,compute=_compute_aomng,store=True)
    meins = fields.Many2one('uom.uom', 'Unit', required=False, readonly=True)
    memo = fields.Text('Remark')
    prnum = fields.Text('Produce Order')
    monum = fields.Text('Model')
    werks = fields.Many2one('stock.warehouse', 'Factory', required=True)
    comco = fields.Many2one('res.company', 'Company', required=True, readonly=True,default=lambda self: self.env['res.company']._company_default_get('delivery.order.line').id)
    lifnr = fields.Many2one('res.partner', 'Supplier', required=False, readonly=True, domain=[('supplier', '=', True)],default=lambda self: self.env['res.users']._get_default_supplier())
    delivery_purchase_orders = fields.One2many('delivery.purchase.orders', 'delivery_order_line_id',
                                               'Delivery Purchase Orders', required=True)
    delivery_product_orders = fields.One2many('delivery.product.orders', 'delivery_product_line_id',
                                              'Delivery Product Orders')
    atsel = fields.Boolean('Auto Selection PO', readonly=True)
    version_id = fields.Integer('Version')
    line_version_id = fields.Integer('Line Version mat')
    isinvalid = fields.Boolean('Is Invalid',required=True, readonly=True,default=False)
    is_edit_mantr = fields.Boolean('IS Edit Mantr',default=True)

    _sql_constraints = [
        ('dnmng_check', "CHECK (dnmng > 0 )", "The amount of demand must be greater than 0 ."),
    ]

    # _defaults = {
    #     'comco': lambda self: self.env['res.company']._company_default_get('delivery.order.line'),
    #     'lifnr': lambda self: self.env['res.users']._get_default_supplier(),
    #     'isinvalid': False,
    #     'is_edit_mantr':True
    # }



    def search(self,args, offset=0, limit=None, order=None,count=False):
        comco = self.env['res.company']._company_default_get('delivery.order')
        lifnr = self.env['res.users']._get_default_supplier()
        if lifnr > 0:
            args += [('lifnr', '=', lifnr)]
        args += [('comco', '=', comco.id)]

        return super(delivery_order_line, self).search(args, offset=offset, limit=limit, order=order,count=count)

    def create(self,values):
        for vals in values:
            if not vals.get('delivery_purchase_orders',False) or len(vals.get('delivery_purchase_orders')) <= 0:
                if 'source' in self._context.keys() and 'import' == self._context['source']:
                    raise exceptions.ValidationError("No purchase order.No delivery order is allowed.")
                else:
                    raise exceptions.ValidationError("没有采购订单不允许创建交货单")
            if 'delivery_purchase_orders' in  vals:
                for d in vals['delivery_purchase_orders']:
                    for k in d:
                        if type(k) == dict and 'matnr' in  k and k['matnr'] != vals['matnr']:
                            raise exceptions.ValidationError("采购订单行和交货单行不匹配")

            # if not vals.get('delivery_product_orders') and context.get('isscheduledate')==True:
            #     raise exceptions.ValidationError("没有生产订单不允许创建交货单")
            if 'delivery_product_orders' in vals.keys() and  len(vals.get('delivery_product_orders'))>1:
                if 'source' in self._context.keys() and 'import' == self._context['source']:
                    raise exceptions.ValidationError("Only one production order is allowed to create the delivery order.")
                else:
                    raise exceptions.ValidationError("只允许选择一个生产订单创建交货单")

            #交货数不能超过最大交货数
            if 'max_dnmng' in vals and vals['dnmng'] > vals['max_dnmng']:
                raise exceptions.ValidationError("交货数量不能超过最大交货数"+str(vals['max_dnmng']))

            # 判断采购订单合计数量是否超过需交货数
            po_pty = 0
            for po in vals['delivery_purchase_orders']:
                for p in po:
                    if p and isinstance(p, dict) and p.get('menge'):
                        po_pty += p['menge']

            if po_pty > vals['dnmng']:
                if 'source' in self._context.keys() and 'import' == self._context['source']:
                    raise exceptions.ValidationError("Purchase orders can not exceed the quantity required.")
                else:
                    raise exceptions.ValidationError("采购订单数量不能大于需交货数.")
            elif po_pty < vals['dnmng']:
                if 'source' in self._context.keys() and 'import' == self._context['source']:
                    raise exceptions.ValidationError("Purchase order quantity should not be less than required delivery quantity.")
                else:
                    raise exceptions.ValidationError("采购订单数量不能小于需交货数")

            pr_pty = 0
            if 'delivery_product_orders' in vals.keys():
                for pr in vals['delivery_product_orders']:
                    for p in pr:
                        if p and isinstance(p, dict) and p.get('penge'):
                            pr_pty += p['penge']

                    if pr_pty > vals['dnmng']:
                        if 'source' in self._context.keys() and 'import' == self._context['source']:
                            raise exceptions.ValidationError("The number of production orders can not exceed the required delivery.")
                        else:
                            raise exceptions.ValidationError("生产订单数量不能大于需交货数.")
                    elif pr_pty < vals['dnmng']:
                        if 'source' in self._context.keys() and 'import' == self._context['source']:
                            raise exceptions.ValidationError("The quantity of production orders should not be less than the required deliveries.")
                        else:
                            raise exceptions.ValidationError("生产订单数量不能小于需交货数.")


            if 'admng' in vals.keys():
                vals['admng'] = vals['admng'] + vals['dnmng']
            if 'meins' not in  vals.keys():
                self._cr.execute("select product_tmpl_id from  product_product where id=%(matnr)s ", {'matnr': vals['matnr']})
                tmpl_id = self._cr.fetchone()
                self._cr.execute("select uom_id from  product_template where id=%(tmpl_id)s ", {'tmpl_id': tmpl_id})
                menin = self._cr.fetchone()
                vals['meins'] = menin[0]


        return super(delivery_order_line, self).create(values)


    @api.onchange('matnr')
    def onchange_matnr(self):
        result = {}
        context = dict(self._context or {})
        werks = context['werks']
        werks = int(werks)
        lifnr = context['lifnr']
        comco = context['comco']
        matnr = self.matnr
        partner = self.env['res.partner'].browse(lifnr)
        isallownoschedulecreate = partner.allow_no_schedule_create
        if isallownoschedulecreate == False:
            result['delivery_order_line'] = []
            result['is_edit_mantr'] = False
            return {'value': result}
        if werks and comco and lifnr and matnr:

            line = []
            productLine = []
            tmpl_id = matnr.product_tmpl_id.id

            self._cr.execute("select count(1) from product_product p inner join product_supplierinfo s on p.product_tmpl_id = s.product_tmpl_id"
                       " and s.name=%(lifnr)s and s.product_tmpl_id=%(tmpl_id)s ",{'lifnr': lifnr,'tmpl_id':tmpl_id})
            count = self._cr.fetchone()
            if int(count[0])==0:
                raise exceptions.ValidationError("当前物料不是当前供应商提供，请重新选择物料！")

            self._cr.execute("select uom_id from  product_template where id=%(tmpl_id)s ", {'tmpl_id': tmpl_id})
            menin = self._cr.fetchone()
            supplier_self = self.env['product.supplierinfo']
            supplierinfo = supplier_self.search([('product_tmpl_id', '=', tmpl_id), ('name', '=', lifnr)])
            auto_sel = supplierinfo.automatic_selection
            if supplierinfo and len(supplierinfo) == 1:
                # 查询物料对应的采购订单
                order_sql = "select h.id as order_id,l.id as line_id,coalesce(l.product_qty,0) - coalesce(l.delivery_qty,0) as product_qty,l.date_planned,l.product_id,h.picking_type_id, " \
                            " case when l.item is not null then l.item else ''||l.id end as item from purchase_order h " \
                            " inner join purchase_order_line l on h.id = l.order_id " \
                            " left JOIN stock_move sm ON sm.purchase_line_id = l.id and sm.location_dest_id in (select id from stock_location where usage='internal') "\
							" left JOIN stock_picking sp ON sp.ID = sm.picking_id " \
                            " where l.NO_MORE_GR is null AND h.partner_id = %s and h.company_id = %s  " \
                            " and h.state = 'supply_confirm' and sp.state='assigned' and l.product_id = %s and h.location_id = (select lot_stock_id from stock_warehouse where id = %s ) " \
                            " order by h.id "
                self._cr.execute(order_sql, (lifnr, comco, matnr.id, werks))
                order_dicts = self._cr.dictfetchall()

                for od in order_dicts:
                    # 查询PO已创建交货单数量
                    po_sql = "select sum(menge) from delivery_purchase_orders o " \
                             "inner join delivery_order_line l on l.id = o.delivery_order_line_id " \
                             "inner join delivery_order h on h.id = l.delivery_order_id " \
                             "where h.state in ('supplier_create','print') " \
                             "and o.ponum = %s and o.pline = %s "
                    self._cr.execute(po_sql, (od['order_id'], od['line_id']))
                    pomenge = self._cr.fetchone()
                    if not pomenge[0]:
                        pomenge = 0
                    else:
                        pomenge = pomenge[0]

                    if od['product_qty'] - pomenge > 0:
                        line.append({
                            'ponum': od['order_id'],
                            'pline': od['line_id'],
                            'menge': od['product_qty'] - pomenge,
                            'old_menge':od['product_qty'] - pomenge,
                            'matnr': od['product_id'],
                            'werks': werks,
                            'ddate': od['date_planned'].strftime('%Y-%m-%d'),
                            'comco': comco,
                            'lifnr': lifnr,
                            'item':od['item']
                        })

            ol = {
                'matnr':  matnr.id,
                'ekgrp': '',
                'meins': menin[0],
                'prnum': '',
                'monum': 0,
                'version_id': '',
                'line_version_id': '',
                'comco': comco,
                'lifnr': lifnr,
                'dnmng': 0,
                'sdmng': 0,
                'admng': 0,
                'werks': werks
            }
            if len(line) > 0:
                ol['delivery_purchase_orders'] = line
            if auto_sel:
                ol['atsel'] = True
            # order_line.append(ol)

            if 'delivery_purchase_orders' not in ol:
                ol['delivery_purchase_orders'] = []
            result = ol
            result['is_edit_mantr'] = True
            return {'value': result}
        result['delivery_order_line'] = []
        result['is_edit_mantr'] = True
        return {'value': result}

    def write(self,vals):
        if vals.get('dnmng'):
            old_obj = self.env['delivery.order.line'].browse(self.ids[0])
            if old_obj['admng']>0:
                vals['admng'] = old_obj['admng'] - old_obj['dnmng'] + vals['dnmng']
        return super(delivery_order_line, self).write(vals)

    @api.multi
    def select_po(self):
        id2 = self.env.ref('delivery_order.select_po_view')
        purchase_lines = self.env['purchase.order.line'].search(
            [('product_id', '=', self.matnr.id),
             ('date_planned', '>=', self.delivery_order_id.datoo),
             ('state', '=', 'supply_confirm')],
            order='date_planned DESC')
        # 'domain': "[('id','in',[" + ','.join(map(str,purchase_lines.ids)) + "])]",
        # orders = []
        # for line in purchase_lines:
        #     orders.append({'ponum':line['order_id'].id,'pline':line['id'],'menge':line['product_qty']})
        return {
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'delivery.purchase.orders',
            'views': [(id2.id, 'tree')],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


class delivery_purchase_orders(models.Model):
    _name = 'delivery.purchase.orders'
    _description = "采购订单"

    def _default_matnr(self):
        return self._context.get('matnr')

    def _default_werks(self):
        return self._context.get('werks')

    def _default_comco(self):
        return self._context.get('comco')

    def _default_lifnr(self):
        return self._context.get('lifnr')

    delivery_order_line_id = fields.Many2one('delivery.order.line', 'Delivery Order Line', readonly=True,
                                             ondelete='cascade')
    comco = fields.Many2one('res.company', 'Company', required=True,default=_default_comco)
    lifnr = fields.Many2one('res.partner', 'Supplier', required=False, domain=[('supplier', '=', True)],default=_default_lifnr)
    ponum = fields.Many2one("purchase.order", "Purchase Order", required=True)
    old_menge = fields.Integer("Old Delivery Qty", required=True)
    menge = fields.Integer("Delivery Qty", required=True)
    done_menge = fields.Integer("Done Qty",default=0)
    matnr = fields.Many2one('product.product', 'Material', required=True, domain=[('purchase_ok', '=', True)],default=_default_matnr)
    werks = fields.Many2one('stock.warehouse', 'Factory', required=True,default=_default_werks)
    pline = fields.Many2one("purchase.order.line", "Purchase Order Line", required=True)
    item = fields.Char("Purchase Order Line ID")
    ddate = fields.Date("Demand Date", required=True)
    delivery_order_batch = fields.One2many('delivery.order.batch', 'delivery_purchase_orders_id',
                                           'Delivery Order Batch')
    @api.onchange('menge')
    def onchange_menge(self):
        if self.menge > self.old_menge:
            result = {}
            result['menge'] = self.old_menge
            return {'value': result}

class delivery_order_batch(models.Model):
    _name = 'delivery.order.batch'
    _description = "批次信息"

    def _default_matnr(self):
        return self._context.get('matnr')

    def _default_werks(self):
        return self._context.get('werks')

    def _default_ponum(self):
        return self._context.get('ponum')

    def _default_pline(self):
        return self._context.get('pline')

    def _default_pomen(self):
        return self._context.get('pomen')

    delivery_purchase_orders_id = fields.Many2one('delivery.purchase.orders', 'Delivery Purchase Order', readonly=True,
                                                  ondelete='cascade')
    ponum = fields.Many2one("purchase.order", "Purchase Order", readonly=True,default=_default_ponum)
    pline = fields.Many2one("purchase.order.line", "Purchase Order Line", readonly=True,default=_default_pline)
    matnr = fields.Many2one('product.product', 'Material', readonly=True, required=True,
                            domain=[('purchase_ok', '=', True)],default=_default_matnr)
    menge = fields.Integer("Delivery Qty")
    pomen = fields.Integer("PO Qty", readonly=True,default=_default_pomen)
    werks = fields.Many2one('stock.warehouse', 'Factory', required=True, readonly=True,default=_default_werks)
    pdate = fields.Date("Product Date")
    datec = fields.Char("Date Code")



    # _defaults = {
    #     'matnr': _default_matnr,
    #     'werks': _default_werks,
    #     'ponum': _default_ponum,
    #     'pline': _default_pline,
    #     'pomen': _default_pomen,
    # }

    def create(self,vals):
        vals['matnr'] = self.env['delivery.purchase.orders'].browse(vals['delivery_purchase_orders_id']).matnr.id
        vals['werks'] = self.env['delivery.purchase.orders'].browse(vals['delivery_purchase_orders_id']).werks.id
        id = super(delivery_order_batch, self).create(vals)
        return id

class delivery_product_orders(models.Model):
    _name = 'delivery.product.orders'
    _description = "生产订单"

    delivery_product_line_id = fields.Many2one('delivery.order.line', 'Delivery Order Line', readonly=True,
                                             ondelete='cascade')
    lifnr = fields.Many2one('res.partner', 'Supplier', required=True, domain=[('supplier', '=', True)])
    details_id = fields.Many2one("mat.demand.line.details", "Details Line", required=True)
    prnum = fields.Char('Product Order')
    penge = fields.Integer("Product Qty", required=True,readonly=False)
    menge = fields.Integer("Demand Qty", required=True)
    matnr = fields.Many2one('product.product', 'Material', readonly=True, domain=[('purchase_ok', '=', True)])
    ddate = fields.Date("Demand Date", required=True,readonly=False)
    aprng = fields.Integer('Already Product Qty', readonly=True)
    max_menge = fields.Integer("Max Delivery Qty")

    @api.onchange('penge')
    def onchange_penge(self):
        if self.penge > self.max_menge:
            result = {}
            result['penge'] = self.max_menge
            return {'value': result}
