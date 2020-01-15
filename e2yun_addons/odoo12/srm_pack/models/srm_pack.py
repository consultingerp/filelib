# -*- coding: utf-8 -*-

from odoo import models, fields, api,exceptions
import datetime
import copy

class srm_pack(models.Model):
    _name = 'srm.pack'
    #_inherit = ['mail.thread']
    _description = "包裹"

    STATE_SELECTION = [
        ('create', 'Create'),
        ('print', 'Print')
    ]

    name = fields.Char('Packing Num')
    comco = fields.Many2one('res.company', 'Company', required=True,default=lambda self: self.env['res.company']._company_default_get('srm.pack').id)
    werks = fields.Many2one('stock.warehouse', 'Factory', required=False)
    lifnr = fields.Many2one('res.partner', 'Supplier', required=False, domain=[('supplier', '=', True)],default=lambda self: self.env['res.users']._get_default_supplier())
    state = fields.Selection(STATE_SELECTION, 'Status',default='create')
    prinu = fields.Integer("Print Count")
    matnr = fields.Many2one('product.product', 'Material', required=False, domain=[('purchase_ok', '=', True)])
    prnum = fields.Char('Produce Order')
    dnnum = fields.Char('Delivery Order')
    monum = fields.Char('Model')
    memo = fields.Text('Remark')
    srm_pack_line = fields.One2many('srm.pack.line', 'srm_pack_id', 'Packing Line')
    printSendDate = fields.Char('Print Send Date')
    serial_num = fields.Integer("Serial Num")

    _order = " create_date desc, serial_num "

    @api.model
    def create(self,vals):
        vals['werks'] = self._context['werks']
        srm_pack_line = vals['srm_pack_line']
        idvalues=0
        line_indexs=[]
        lingSumMengMap = {}
        lineUsmeg = {}
        linePacknum ={}
        lineMatnr = {}
        for line in srm_pack_line:
            if  'menge' in line[2].keys() and 'packnum' in line[2].keys() and line[2]['packnum'] and  line[2]['menge'] :
                vals['dnnum'] = line[2]['dnnum']
                packnum = line[2]['packnum']
                usmeg = line[2]['usmeg']
                menge = line[2]['menge']
                if packnum==0 or menge==0:
                    raise exceptions.ValidationError("包数或者包数量不能为零，无需打包的则不用输入！")

                dnnumLineId = line[2]['dnnum_line_id']
                if dnnumLineId in lingSumMengMap.keys():
                    mengeSum = menge + lingSumMengMap.get(dnnumLineId)

                    if mengeSum > usmeg:
                        raise exceptions.ValidationError("交货单行包数量不能大于需求数量！")
                    else:
                        lingSumMengMap[dnnumLineId] = mengeSum
                else:
                    lineMatnr[dnnumLineId] = line[2]['matnr']
                    lingSumMengMap[dnnumLineId] = menge
                    lineUsmeg[dnnumLineId] = usmeg
                    linePacknum[dnnumLineId] = packnum
                line_indexs.append(line)

        if  len(line_indexs) == 0:
            raise exceptions.ValidationError("请输入打包数量和包数量！")

        # if  len(line_index) > 1:
        #     raise exceptions.ValidationError("每次只允许进行单行打包！")

        for  dnnumLineId in  lingSumMengMap.keys() :
            usmeg = lineUsmeg[dnnumLineId]
            sumMenge = lingSumMengMap[dnnumLineId]
            packnum = linePacknum[dnnumLineId]
            if (usmeg%sumMenge> 0 and usmeg/sumMenge+1 < packnum) or (usmeg%sumMenge ==0 and usmeg/sumMenge < packnum):
                matnrcode = self.env['product.product'].browse(lineMatnr[dnnumLineId]).default_code
                raise exceptions.ValidationError("""%s物料的包数量x包数已超出交货可打包数量""" %(matnrcode));


        #计算小包数量
        for line_index in line_indexs:
            bigpack = copy.deepcopy(line_index);
            packnum = line_index[2]['packnum']
            packname = self.env['ir.sequence'].next_by_code('srm.pack')
            vals['matnr'] = line_index[2]['matnr']
            for i in range(packnum):
                vals['name'] = packname + '-' + str(i + 1) + '/' + str(packnum);
                vals['serial_num'] = i + 1
                if i==packnum-1: #最后一个包，需要计算行里面的包数量
                    dnnumLineId = line_index[2]['dnnum_line_id']
                    usmeng = lineUsmeg[dnnumLineId];
                    if  packnum*lingSumMengMap[dnnumLineId]<=usmeng:
                        vals['srm_pack_line'] = [line_index]
                        super(srm_pack, self).create(vals)
                    elif packnum*lingSumMengMap[dnnumLineId]>usmeng:
                        remainder = usmeng % lingSumMengMap[dnnumLineId]
                        remainderLine = []
                        if remainder <= line_index[2]['menge']:
                            line_index[2]['menge'] = remainder
                        elif remainder>line_index[2]['menge']:
                            remainder = remainder - line_index[2]['menge']

                        vals['srm_pack_line'] = [line_index]
                        super(srm_pack, self).create(vals)
                else:
                    vals['srm_pack_line'] = [line_index]
                    super(srm_pack, self).create(vals)



            # 计算大包数量
            sumLine =[];
            remainderMap={}
            for lineId in lingSumMengMap.keys():
                sumMenge = lingSumMengMap[dnnumLineId]
                usmeng = lineUsmeg[dnnumLineId];
                remainderMap[lineId] = usmeng%sumMenge;
            usmeg = bigpack[2]['usmeg']
            menge = bigpack[2]['menge']
            dnnumLineId = bigpack[2]['dnnum_line_id']
            sumMenge = lingSumMengMap[dnnumLineId]
            if sumMenge*packnum >= usmeg:
                if remainderMap[dnnumLineId] ==0:
                    bigpack[2]['menge'] = bigpack[2]['menge'] * packnum
                    sumLine.append(bigpack);
                elif remainderMap[dnnumLineId]<= menge:
                    bigpack[2]['menge'] = bigpack[2]['menge'] * (packnum-1)+remainderMap[dnnumLineId];
                    remainderMap[dnnumLineId] = 0;
                    sumLine.append(bigpack);
                else:
                    remainderMap[dnnumLineId] = remainderMap[dnnumLineId] - bigpack[2]['menge']
                    bigpack[2]['menge'] = bigpack[2]['menge'] * (packnum-1)+bigpack[2]['menge'];
                    sumLine.append(bigpack);
            elif sumMenge*packnum < usmeg:
                bigpack[2]['menge']= bigpack[2]['menge']*packnum;
                sumLine.append(bigpack);

            vals['name'] = packname
            vals['serial_num'] = 0
            vals['srm_pack_line'] = sumLine;
            id = super(srm_pack, self).create(vals)
            idvalues = id;
        return idvalues

    @api.multi
    def unlink(self):
        stock_pack_obj = self.pool.get('stock.quant.package')
        for order in self:
            #order = self.browse(cr,uid,id);
            delivery_order_obj = self.env['delivery.order'].search([('dnnum','=',order.dnnum)])
            if delivery_order_obj.state == 'Finished':
                raise exceptions.ValidationError("包裹关联的交货单已完成，不可以删除！")
            # if order.state == 'print':
            #     raise exceptions.ValidationError("打印状态不允许删除")
            pack_ids = stock_pack_obj.search([('name','=',order.name)])
            if pack_ids:
                pack_ids.unlink()

        super(srm_pack, self).unlink()

    @api.onchange('matnr','prnum')
    def onchange_head(self):
        matnr = self.matnr.id
        prnum = self.prnum
        result = {}
        sql = "";
        params = []
        sql = "SELECT ( T.pomeg - CASE WHEN T.usmeg IS NULL THEN 0 ELSE T.usmeg END ) AS us, T.* "\
              "FROM (  SELECT " \
              "l.matnr, " \
              "pr.prnum, " \
              "l.monum, " \
              "l.ID AS dnnum_line_id, "\
              " '' AS ponum, "\
              " '' AS pline, " \
              "h.dnnum, " \
              "h.datoo AS pdate, " \
              "current_date AS datec, "\
	          " '' AS order_line_id, "\
	          " '' AS btach_line_id, " \
              "l.dnmng AS pomeg, " \
              "( SELECT SUM ( menge )  FROM srm_pack_line " \
              " INNER JOIN srm_pack P ON P.ID = srm_pack_id  " \
              " WHERE dnnum_line_id = l.ID  AND P.NAME LIKE'%%-%%'  ) usmeg  "\
               " FROM " \
              " delivery_order h " \
              " INNER JOIN delivery_order_line l ON h.ID = l.delivery_order_id " \
              " left JOIN delivery_product_orders pr ON pr.delivery_product_line_id = l.id " \
              " WHERE 1 = 1 ";

        # "	h.comco = %s " \
        # "	AND h.lifnr = %s "
        # params = [comco,lifnr]
        params = []
        # if werks:
        #     params.append(werks)
        #     sql += "AND h.werks = %s"
        context = dict(self._context or {})
        if context['lifnr']:
            params.append(context['lifnr'])
            sql += "  AND h.lifnr = %s "
        if matnr:
            params.append(matnr)
            sql += " AND l.matnr = %s "
        if prnum:
            params.append(prnum)
            sql += " AND pr.prnum = %s "
        # if ponum:
        #     params.append(ponum)
        #     sql += " AND p.ponum = %s "

        if context['dnnum']:
            params.append(context['dnnum'])
            sql += " AND h.dnnum = %s "

        sql += "	) T "
        self._cr.execute(sql, params)
        mat_dicts = self._cr.dictfetchall()
        mat_line = []

        supplier_self = self.env['product.supplierinfo']
        resultlifnr = self.env['res.users']._get_default_supplier()

        for m in mat_dicts:
            packnum = 0
            min_pack = 0
            self._cr.execute("select min_pack from product_supplierinfo where product_tmpl_id=%s and name=%s ",(m['matnr'],resultlifnr))
            min_pack = self._cr.fetchone()
            if  min_pack == None:
                min_pack = 0
            else:
                min_pack = min_pack[0]

            if  min_pack>0 and m['us']>0:
                if m['us']%min_pack==0:
                    packnum = m['us']/min_pack
                else:
                    packnum = m['us']/min_pack +1

            mat_line.append({
                'matnr':m['matnr'],
                'prnum':m['prnum'],
                'monum':m['monum'],
                'ponum':m['ponum'],
                'pline':m['pline'],
                'dnnum':m['dnnum'],
                'pdate':m['pdate'],
                'datec':m['datec'],
                'dnnum_line_id':m['dnnum_line_id'],
                'order_line_id':m['order_line_id'],
                'btach_line_id':m['btach_line_id'],
                'packnum':packnum,
                'menge':min_pack,
                'usmeg':m['us']
            })

        return self.update({'srm_pack_line':mat_line})

    def get_printSendDate(self, data):
        today = datetime.datetime.today()
        weekday = datetime.datetime.isoweekday(today)
        printSendDate = today.strftime('%Y-%m-%d')
        # if weekday == 7:
        #     mondayDay = today + datetime.timedelta(days=1)
        #     printSendDate = mondayDay.strftime('%Y-%m-%d')
        # elif weekday == 6:
        #     mondayDay = today + datetime.timedelta(days=2)
        #     printSendDate = mondayDay.strftime('%Y-%m-%d')
        self.printSendDate = printSendDate
        self.state='print'
        self.prnum = int(self.prnum)+1
        return printSendDate

    @api.multi
    def print_order(self):
        self.ensure_one()
        today = datetime.datetime.today()
        printSendDate = today.strftime('%Y-%m-%d')
        packName = self.name
        if packName.find('-')> 0:
            self.write({'state': 'print', 'prinu': self.prinu + 1,'printSendDate':printSendDate})
            return self.env.ref('srm_pack.report_packing_tag_quotation').report_action(self)
        else:
            self._cr.execute("select id from srm_pack where name like '%s\-%%'" %(packName))
            sonPacks = self._cr.dictfetchall()
            sonpackId = []
            for sonPack in sonPacks:
                packOrder = self.browse(sonPack['id'])
                packOrder.write({'state': 'print', 'prinu': packOrder.prinu + 1,'printSendDate':printSendDate})
                sonpackId.append(sonPack['id'])
            return self.env.ref('srm_pack.report_packing_tag_quotation').report_action(sonpackId)

    def search(self,args, offset=0, limit=None, order=None, count=False):
        if self._context is None:
            context = {}
        comco = self.env['res.company']._company_default_get('srm.pack').id
        lifnr = self.env['res.users']._get_default_supplier()
        if lifnr > 0:
            args += [('lifnr', '=', lifnr)]
        args += [('comco', '=', comco)]

        return super(srm_pack, self).search(args, offset=offset, limit=limit, order=order,count=count)





class srm_pack_line(models.Model):
    _name = 'srm.pack.line'
    #_inherit = ['mail.thread']
    _description = "包裹行"

    srm_pack_id = fields.Many2one('srm.pack', 'Packing Num', required=True, ondelete='cascade')
    dnnum = fields.Char('Delivery Order')
    dnnum_line_id = fields.Integer('Delivery Order Line')
    matnr = fields.Many2one('product.product', 'Material', required=True, domain=[('purchase_ok', '=', True)])
    prnum = fields.Char('Produce Order')
    monum = fields.Char('Model')
    ponum = fields.Many2one("purchase.order", "Purchase Order")
    pline = fields.Many2one("purchase.order.line", "Purchase Order Line")
    menge = fields.Integer("Packing Qty")
    usmeg = fields.Integer("Used Qty")
    pdate = fields.Date("Product Date")
    datec = fields.Char("Date Code")
    order_line_id = fields.Integer('Order Line ID')
    batch_line_id = fields.Integer('Batch Line ID')
    packnum = fields.Integer("Package Num")

    @api.onchange('menge')
    def changmenge(self):
        if self.menge == 0:
            return
        if self.menge > self.usmeg:
            raise exceptions.ValidationError("包数量不能大于总数量")
        if self.usmeg == 0:
            return
        packnum = 0
        if self.usmeg % self.menge > 0:
            packnum = self.usmeg / self.menge + 1
        else:
            packnum = self.usmeg / self.menge
        return self.update({'packnum':packnum})
