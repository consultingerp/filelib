# -*- coding: utf-8 -*-

from odoo import models, fields, api,exceptions
from odoo import tools, _
import odoo.addons.decimal_precision as dp
import datetime

class delivery_order_rep_batch(models.TransientModel):
    _name = 'srm.account.order.rep.batch'

    def create_account_order(self):
        ctx = self._context.copy()

        active_model = ctx.get('active_model')
        active_ids = ctx.get('active_ids', [])

        rep = self.env['srm.account.order.rep'].browse(active_ids)
        partner_id = rep[0].picking_partner.id
        head = {
            'partner_id' : partner_id,
            'state' : 'draft',
            'date' : datetime.date.today(),
            'currency' : rep[0]['currency']
        }
        line = []
        total_price = 0
        total_tax = 0
        for r in rep:
            # 验证供应商，同一张对账单，供应商必须相同
            if r.picking_partner.id != partner_id:
                raise exceptions.ValidationError('供应商必须一致')
                return False
            l = {
                'move_id': r.id,
                'product_id': r.product_id.id,
                'product_uom': r.product_uom.id,
                'price_unit': r.price_unit,
                'picking_id': r.picking_id.id,
                'tax_id': r.tax_id,
                'name': r.name,
                'product_uom_qty': r.product_uom_qty,
                'origin': r.origin,
                'purchase_order_no': r.purchase_order_no,
                'purchase_order_item': r.purchase_order_item,
                'purchase_qty': r.purchase_qty,
                'currency': r.currency,
                'tax_code': r.tax_code,
                'tax_rate': r.tax_rate,
                'date_done': r.date_done,
                'picking_type_code': r.picking_type_code,
                'voucher_code': r.voucher_code,
                'voucher_qty': r.voucher_qty,
                #'price_total_tax': r.price_total_tax,
                #'price_total': r.price_unit * r.product_uom_qty,
                'tax_price': r.tax_price,
                'lgort': r.lgort,
                'dnnum': r.dnnum,
                'kbetr': r.kbetr,
                'kpein': r.kpein
            }

            if r.picking_type_code == '161':
                l['price_total'] = r.price_unit * r.product_uom_qty * -1
            else:
                l['price_total'] = r.price_unit * r.product_uom_qty

            l['price_total_tax'] = round(l['price_total'], 2) + round(l['tax_price'], 2)

            line.append(l)

            total_tax += round(r.tax_price,2)
            total_price += round(l['price_total_tax'],2)

        head['total_price'] = total_price
        head['total_tax'] = total_tax

        account_id = self.env['srm.account.order'].create(head)
        for l in line:
            l['account_id'] = account_id.id
            self.env['srm.account.order.line'].create(l)

        id2 = self.env.ref('srm_account_order.srm_account_order_form')
        return {
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'srm.account.order',
            'views': [(id2.id, 'form')],
            'view_id': id2.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': self.env.context,
            'res_id': account_id.id,
        }




class delivery_order_rep(models.Model):
    _name = 'srm.account.order.rep'
    _description = 'Account Order Rep'
    _auto = False

    def _compute_tax_rate(self):
        for line in self:
            if line.purchase_line_id:
                if line.purchase_line_id.taxes_id:
                    tax = line.purchase_line_id.taxes_id[0].amount * 100
                    line.tax_rate = str(tax) + '%'
            elif line.tax_id:
                tax = self.env['account.tax'].browse(line.tax_id).amount* 100
                line.tax_rate = str(tax) + '%'

    @api.multi
    def _compute_tax_code(self):
        for line in self:
            if line.purchase_line_id:
                if line.purchase_line_id.taxes_id:
                    tax = line.purchase_line_id.taxes_id[0].name
                    line.tax_code = tax
            elif line.tax_id:
                tax = self.env['account.tax'].browse(line.tax_id).name
                line.tax_code = tax
            else:
                line.tax_code = ''

    @api.depends('picking_type_code','product_uom_qty')
    def _compute_price_total_tax(self):
        for line in self:
            amount = 0
            qty = line.product_uom_qty
            if line.purchase_line_id:
                if line.purchase_line_id.taxes_id:
                    amount = line.purchase_line_id.taxes_id[0].amount
                    # sql = """select erfmg from vouchers_synchronize_data v inner join  sap_voucher s on s.matdoc = v.lfbnr and v.lfpos = trim(to_char(s.linemark,'99999999999'))
                    #                                   where s.picking_id = %s and s.move_id = %s limit 1 """
                    # #sql = """select erfmg from vouchers_synchronize_data where lfbnr = (select matdoc from sap_voucher where picking_id = %s and move_id = %s )"""
                    # self._cr.execute(sql, (line.picking_id.id, line.id))
                    # erfmg = self._cr.fetchone()
                    # if erfmg and erfmg[0]:
                    #     qty = erfmg[0]
            elif line.tax_id:
                amount = self.env['account.tax'].browse(line.tax_id).amount
                # qty = line.product_uom_qty
            price_total = line.price_unit * (1+amount) * qty

            if line.picking_type_code == '161':
                price_total = price_total * -1

            line.price_total_tax = price_total

    @api.depends('picking_type_code','product_uom_qty')
    def _compute_tax_price(self):
        for line in self:
            amount = 0
            qty = line.product_uom_qty
            if line.purchase_line_id:
                if line.purchase_line_id.taxes_id:
                    amount = line.purchase_line_id.taxes_id[0].amount
                    # sql = """select erfmg from vouchers_synchronize_data v inner join  sap_voucher s on s.matdoc = v.lfbnr and v.lfpos = trim(to_char(s.linemark,'99999999999'))
                    #                                   where s.picking_id = %s and s.move_id = %s limit 1 """
                    # #sql = """select erfmg from vouchers_synchronize_data where lfbnr = (select matdoc from sap_voucher where picking_id = %s and move_id = %s )"""
                    # self._cr.execute(sql, (line.picking_id.id, line.id))
                    # erfmg = self._cr.fetchone()
                    # if erfmg and erfmg[0]:
                    #     qty = erfmg[0]
            elif line.tax_id:
                amount = self.env['account.tax'].browse(line.tax_id).amount
                # qty = line.product_uom_qty
            price_total = line.price_unit * amount * qty

            if line.picking_type_code == '161':
                price_total = price_total * -1
            line.tax_price = price_total

    def _compute_purchase_date(self):
        for line in self:
            if line.purchase_line_id:
                line.purchase_date = line.purchase_line_id.order_id.date_order
            else:
                voucher_id = self.env['vouchers.synchronize.data'].search(
                    [('mblnr', '=', line.picking_id.name), ('lfpos', '=', line.origin)])
                if voucher_id.bedat:
                    line.purchase_date = datetime.datetime.strptime(voucher_id.bedat, "%Y%m%d")
                else:
                    line.purchase_date = ''

    def _compute_purchase_order_no(self):
        for line in self:
            if line.purchase_line_id:
                line.purchase_order_no = line.purchase_line_id.order_id.name
            else:
                line.purchase_order_no = line.picking_id.origin

    def _compute_purchase_order_line_item(self):
        for line in self:
            if line.purchase_line_id:
                line.purchase_order_item = line.purchase_line_id.item
            else:
                line.purchase_order_item = line.name

    def _compute_purchase_qty(self):
        for line in self:
            if line.purchase_line_id:
                line.purchase_qty = line.purchase_line_id.product_qty
            else:
                voucher_id = self.env['vouchers.synchronize.data'].search([('mblnr', '=', line.picking_id.name),('lfpos','=',line.origin)])
                # bwart = self.env['vouchers.synchronize.data'].browse(voucher_id).bwart
                line.purchase_qty = float(voucher_id.menge)

    def _compute_currency(self):
        for line in self:
            if line.purchase_line_id:
                line.currency = line.purchase_line_id.order_id.currency_id.name
            else:
                voucher_id = self.env['vouchers.synchronize.data'].search(
                    [('mblnr', '=', line.picking_id.name), ('lfpos', '=', line.origin)])
                # bwart = self.env['vouchers.synchronize.data'].browse(voucher_id).bwart
                line.currency = voucher_id.waers

    def _compute_date_done(self):
        for line in self:
            line.date_done = line.picking_id.date_done

    def _compute_picking_type_code(self):
        for line in self:
            if line.purchase_line_id:
                sql = """select bwart from vouchers_synchronize_data v inner join  sap_voucher s on s.matdoc = v.lfbnr and v.lfpos = trim(to_char(s.linemark,'99999999999'))
                                                  where s.picking_id = %s and s.move_id = %s limit 1 """
                #sql = """select bwart from vouchers_synchronize_data where lfbnr = (select matdoc from sap_voucher where picking_id = %s and move_id = %s )"""
                self._cr.execute(sql,(line.picking_id.id,line.id))
                bwart = self._cr.fetchone()
                if not bwart or not bwart[0]:
                    bwart = ''
                else:
                    bwart = bwart[0]
                line.picking_type_code = bwart
            else:
                voucher_id = self.env['vouchers.synchronize.data'].search([('mblnr','=',line.picking_id.name),('lfpos','=',line.origin)])
                #bwart = self.env['vouchers.synchronize.data'].browse(voucher_id).bwart
                line.picking_type_code = voucher_id.bwart

    def _compute_voucher_qty(self):
        res = {}
        for line in self:
            if line.purchase_line_id:
                sql = """select erfmg from vouchers_synchronize_data v inner join  sap_voucher s on s.matdoc = v.lfbnr and v.lfpos = trim(to_char(s.linemark,'99999999999'))
                                                  where s.picking_id = %s and s.move_id = %s limit 1 """
                #sql = """select erfmg from vouchers_synchronize_data where lfbnr = (select matdoc from sap_voucher where picking_id = %s and move_id = %s )"""
                self._cr.execute(sql,(line.picking_id.id,line.id))
                erfmg = self._cr.fetchone()
                if not erfmg or not erfmg[0]:
                    erfmg = ''
                else:
                    erfmg = erfmg[0]
                line.voucher_qty = erfmg
            else:
                line.voucher_qty = line.product_uom_qty
        return res

    def _compute_voucher_code(self):
        for line in self:
            if line.purchase_line_id:
                sql = """select mblnr from vouchers_synchronize_data v inner join  sap_voucher s on s.matdoc = v.lfbnr and v.lfpos = trim(to_char(s.linemark,'99999999999'))
                                                  where s.picking_id = %s and s.move_id = %s limit 1 """
                #sql = """select mblnr from vouchers_synchronize_data where lfbnr = (select matdoc from sap_voucher where picking_id = %s and move_id = %s )"""
                self._cr.execute(sql,(line.picking_id.id,line.id))
                mblnr = self._cr.fetchone()
                if not mblnr or not mblnr[0]:
                    mblnr = ''
                else:
                    mblnr = mblnr[0]
                line.voucher_code = mblnr
            else:
                line.voucher_code = line.picking_id.name

    def _compute_lgort(self):
        for line in self:
            if line.purchase_line_id:
                sql = """select lgort from vouchers_synchronize_data v inner join  sap_voucher s on s.matdoc = v.lfbnr and v.lfpos = trim(to_char(s.linemark,'99999999999'))
                                                  where s.picking_id = %s and s.move_id = %s limit 1 """
                #sql = """select lgort from vouchers_synchronize_data where lfbnr = (select matdoc from sap_voucher where picking_id = %s and move_id = %s )"""
                self._cr.execute(sql,(line.picking_id.id,line.id))
                lgort = self._cr.fetchone()
                if not lgort or not lgort[0]:
                    lgort = ''
                else:
                    lgort = lgort[0]
                line.lgort = lgort
            else:
                voucher_id = self.env['vouchers.synchronize.data'].search([('mblnr','=',line.picking_id.name),('lfpos','=',line.origin)])
                #lgort = self.env['vouchers.synchronize.data'].browse(voucher_id).lgort
                line.lgort = voucher_id.lgort

    def _compute_dnnum(self):
        for line in self:
            if line.purchase_line_id:
                sql = """select dnnum from sap_voucher where picking_id = %s and move_id = %s"""
                self._cr.execute(sql,(line.picking_id.id,line.id))
                dnnum = self._cr.fetchone()
                if not dnnum or not dnnum[0]:
                    dnnum = ''
                else:
                    dnnum = dnnum[0]
                line.dnnum = str(dnnum)
            else:
                line.dnnum = ''

    def _compute_kbetr(self):
        for line in self:
            if line.purchase_line_id:
                sql = """select kbetr from vouchers_synchronize_data v inner join  sap_voucher s on s.matdoc = v.lfbnr and v.lfpos = trim(to_char(s.linemark,'99999999999'))
                  where s.picking_id = %s and s.move_id = %s limit 1 """
                self._cr.execute(sql,(line.picking_id.id,line.id))
                kbetr = self._cr.fetchone()
                if not kbetr or not kbetr[0]:
                    kbetr = 0
                else:
                    kbetr = kbetr[0]
                line.kbetr = kbetr
            else:
                voucher_id = self.env['vouchers.synchronize.data'].search([('mblnr','=',line.picking_id.name),('lfpos','=',line.origin)])
                line.kbetr = voucher_id.kbetr

    def _compute_kpein(self):
        res = {}
        for line in self:
            if line.purchase_line_id:
                sql = """select kpein from vouchers_synchronize_data v inner join  sap_voucher s on s.matdoc = v.lfbnr and v.lfpos = trim(to_char(s.linemark,'99999999999'))
                                  where s.picking_id = %s and s.move_id = %s limit 1 """
                #sql = """select kpein from vouchers_synchronize_data where lfbnr = (select matdoc from sap_voucher where picking_id = %s and move_id = %s )"""
                self._cr.execute(sql,(line.picking_id.id,line.id))
                kpein = self._cr.fetchone()
                if not kpein or not kpein[0]:
                    kpein = 0
                else:
                    kpein = kpein[0]
                line.kpein = kpein
            else:
                voucher_id = self.env['vouchers.synchronize.data'].search([('mblnr','=',line.picking_id.name),('lfpos','=',line.origin)])
                #kpein = self.env['vouchers.synchronize.data'].browse(voucher_id).kpein
                line.kpein = voucher_id.kpein
        return res

    def _compute_max_quantity(self):
        for line in self:
            qty = 0
            move = self.env['stock.move'].browse(line.id)
            if move.purchase_line_id.ret_item:
                qty = move.product_uom_qty
                move_ids = self.env['stock.move'].search([('state','=','done'),('origin_returned_move_id','=',move.id)])
                for m in move_ids:
                    qty = qty - m.product_uom_qty
            elif not move.purchase_line_id and move.remark == 'ret_order':
                qty = move.product_uom_qty
                sql = """ select sum(erfmg) qty from vouchers_synchronize_data where bwart = '162' and lfbnr = %s and lfpos = %s """
                self._cr.execute(sql, (move.picking_id.name, move.origin))
                max_qty = self._cr.fetchone()
                if max_qty and max_qty[0] and max_qty[0] > 0:
                    qty =  qty - max_qty[0]
            else:
                sql = """with voucher as(select matdoc,linemark from sap_voucher where picking_id = %s and move_id = %s and movetype='103')
                    select sum(erfmg) qty from vouchers_synchronize_data vs inner join voucher vo
                    on vs.lfbnr = vo.matdoc and vs.lfpos = trim(to_char(vo.linemark, '99999999999')) where vs.bwart = '105' """
                self._cr.execute(sql,(move.picking_id.id,move.id))
                max_qty = self._cr.fetchone()

                if max_qty and max_qty[0] and max_qty[0] > 0:
                    qty =  max_qty[0]

                sql = """with voucher as(select matdoc,linemark from stock_move sm
                        inner join sap_voucher sv on sv.picking_id = sm.picking_id and sv.move_id = sm.id
                        where sm.id =  %s)
                    select coalesce(sum(erfmg),0) qty from vouchers_synchronize_data vs inner join voucher vo
                    on vs.lfbnr = vo.matdoc and vs.lfpos = trim(to_char(vo.linemark, '99999999999')) where vs.bwart = '106' """
                self._cr.execute(sql, [move.id])
                max_qty = self._cr.fetchone()

                if max_qty and max_qty[0] and max_qty[0] > 0:
                    qty = qty - max_qty[0]
            line.product_uom_qty = qty - move.account_qty

    picking_partner = fields.Many2one('res.partner','供应商')
    product_id = fields.Many2one('product.product','物料')
    product_uom = fields.Many2one('product.uom','单位')
    price_unit = fields.Float('单价',digits=dp.get_precision('Product Price'))
    picking_id = fields.Many2one('stock.picking','作业')
    purchase_line_id = fields.Many2one('purchase.order.line','采购订单行')
    tax_id = fields.Integer('税')
    name = fields.Char('Name')
    product_uom_qty = fields.Float(compute='_compute_max_quantity',string='数量')
    origin = fields.Char('Origin')

    purchase_date = fields.Date(compute='_compute_purchase_date',string='采购日期')
    purchase_order_no = fields.Char(compute='_compute_purchase_order_no', string='采购单号')
    purchase_order_item = fields.Char(compute='_compute_purchase_order_line_item', string='采购单项次')
    purchase_qty = fields.Float(compute='_compute_purchase_qty', string='采购数量')
    currency =  fields.Char(compute='_compute_currency', string='币别')
    tax_code = fields.Char(compute='_compute_tax_code', string='税码')
    tax_rate = fields.Char(compute='_compute_tax_rate', string='税率')
    date_done = fields.Date(compute='_compute_date_done', string='过账日期')
    picking_type_code = fields.Char(compute='_compute_picking_type_code', string='作业类型')
    voucher_code = fields.Char(compute='_compute_voucher_code', string='合格入库凭证')
    voucher_qty = fields.Float(compute='_compute_voucher_qty', string='凭证数量')
    price_total_tax = fields.Float(compute='_compute_price_total_tax', string='应付本位币金额(含税)',digits=dp.get_precision('Discount'))
    tax_price = fields.Float(compute='_compute_tax_price', string='应付税额',digits=dp.get_precision('Discount'))
    lgort = fields.Char(compute='_compute_lgort', string='库位')
    dnnum = fields.Char(compute='_compute_dnnum', string='送货单号')
    kbetr = fields.Float(compute='_compute_kbetr', string='价格',digits=dp.get_precision('Product Price'))
    kpein = fields.Float(compute='_compute_kpein', string='价格单位')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'srm_account_order_rep')

        sql = """CREATE OR REPLACE VIEW srm_account_order_rep AS
            select m.id,p.partner_id as picking_partner,m.product_id,m.product_uom,
            (case when m.price_unit <=0 then (select price_unit from purchase_order_line where id= m.purchase_line_id) else m.price_unit end) price_unit,
            --(select price_unit from purchase_order_line where id= m.purchase_line_id) price_unit,
            m.picking_id,m.purchase_line_id,m.tax_id,m.name,m.product_uom_qty,m.origin
            from stock_move m inner join stock_picking p on m.picking_id = p.id
            where m.state = 'done' 
            and p.confirm_transfer = 't' 
            and p.state = 'done'
            and m.product_uom_qty - coalesce(m.account_qty,0) > 0
        
        """
        self._cr.execute(sql)