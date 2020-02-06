# -*- coding: utf-8 -*-

from __future__ import division
from odoo import models, fields, api, exceptions
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _
import datetime
import time
try:
    from odoo.addons.srm_pyrfc import ZSRM_INCOMINGINVOICE_CREATE
except:
    pass

class srm_account_order(models.Model):
    _name = 'srm.account.order'
    _inherit = ['mail.thread', ]
    _description = "Account Order"

    STATE_SELECTION = [
        ('draft', '草稿'),
        ('send', '待供应商确认'),
        ('supplier_confirm', '供应商确认'),
        ('supply_refuse', '供应商拒绝'),
        ('done', '完成'),
        ('cancel', '取消'),
    ]

    name = fields.Char('对账单')
    date = fields.Date('对账日期')
    done_date = fields.Date('完成日期')
    total_price = fields.Float('合计金额',digits=dp.get_precision('Discount'))
    total_tax = fields.Float('合计税额',digits=dp.get_precision('Discount'))
    company_id = fields.Many2one('res.company','公司',default=lambda self: self.env['res.company']._company_default_get('srm.account.order').id)
    partner_id = fields.Many2one('res.partner','供应商')
    state = fields.Selection(STATE_SELECTION,'状态')
    currency = fields.Char('币别')
    voucher = fields.Char('凭证')
    account_lines = fields.One2many('srm.account.order.line','account_id','Account Line')

    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].get('srm.account.order')
        id =  super(srm_account_order, self).create(vals)
        return id

    def unlink(self):
        for v in  self:
            if v.state != 'draft':
                raise exceptions.ValidationError('只能删除草稿状态对账单')
                return False
            for l in v.account_lines:
                m = l.move_id
                m.account_qty = m.account_qty - l.product_uom_qty
        return super(srm_account_order, self).unlink()

    def wkf_send_email(self):
        ir_model_data = self.env['ir.model.data']
        self.write({'state':'send'})
        try:
             emil_name='SRM - Account check for email'
             #invoice check for email
             email_template = self.env['mail.template'].search([('name', '=', emil_name)])
             for temp_id in email_template:
                 template_id = temp_id.id
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self._context)
        ctx.update({
            'default_model': 'srm.account.order',
            'default_res_id': self._ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'active_id':self.id,
            'active_ids':[self.id,],
            'active_model':'srm.account.order',
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def order_confirm(self):
        IT_ITEMDATA = []
        IS_HEADERDATA = {}

        current_date = datetime.datetime.now()
        for inv in self:
            IS_HEADERDATA['INVOICE_IND'] = 'X'
            IS_HEADERDATA['DOC_TYPE'] = 'RE'
            IS_HEADERDATA['REF_DOC_NO'] = inv.name or ''
            if inv.date:
                IS_HEADERDATA['DOC_DATE'] = str(inv.date).replace('-', '')
                IS_HEADERDATA['PSTNG_DATE'] = str(inv.date).replace('-', '')
            else:
                IS_HEADERDATA['DOC_DATE'] = datetime.datetime.strftime(current_date, '%Y-%m-%d').replace('-', '')
                IS_HEADERDATA['PSTNG_DATE'] = datetime.datetime.strftime(current_date, '%Y-%m-%d').replace('-', '')
            IS_HEADERDATA['COMP_CODE'] = str(inv.company_id.company_code)  # 公司代码
            IS_HEADERDATA['CURRENCY'] = inv.currency  # 币别
            IS_HEADERDATA['GROSS_AMOUNT'] = inv.total_price
            IS_HEADERDATA['CALC_TAX_IND'] = 'X'

            i = 0
            for iline in inv.account_lines:
                i = i + 1
                IT_ITEMDATA_ITEM_MAP = {}
                IT_ITEMDATA_ITEM_MAP['INVOICE_DOC_ITEM'] = str(i)
                IT_ITEMDATA_ITEM_MAP['PO_NUMBER'] = str(iline.purchase_order_no).zfill(10)
                IT_ITEMDATA_ITEM_MAP['PO_ITEM'] = str(iline.purchase_order_item)

                if iline.move_id and iline.move_id.purchase_line_id:
                    sql = "select matdoc,linemark from sap_voucher where move_id=" + str(
                        iline.move_id.id) + " and pline='" + str(iline.move_id.purchase_line_id.item) + "'"
                    self._cr.execute(sql)
                    result = self._cr.fetchone()
                    if result:
                        IT_ITEMDATA_ITEM_MAP['REF_DOC'] = str(result[0])  # 凭证
                        IT_ITEMDATA_ITEM_MAP['REF_DOC_IT'] = str(result[1])  # 凭证行号
                else:
                    IT_ITEMDATA_ITEM_MAP['REF_DOC'] = str(iline.move_id.picking_id.name)  # 凭证
                    IT_ITEMDATA_ITEM_MAP['REF_DOC_IT'] = str(iline.move_id.origin)  # 凭证行号

                IT_ITEMDATA_ITEM_MAP['REF_DOC_YEAR'] = str(current_date.year)  # 会记年度

                IT_ITEMDATA_ITEM_MAP['TAX_CODE'] = iline.tax_code or ''
                IT_ITEMDATA_ITEM_MAP['PO_UNIT'] = iline.product_uom.name
                IT_ITEMDATA_ITEM_MAP['ITEM_AMOUNT'] = iline.price_total
                IT_ITEMDATA_ITEM_MAP['QUANTITY'] = iline.product_uom_qty
                IT_ITEMDATA.append(IT_ITEMDATA_ITEM_MAP)

            #判断总额为负数，特殊处理
            if IS_HEADERDATA['GROSS_AMOUNT'] < 0:
                del IS_HEADERDATA['INVOICE_IND']
                #IS_HEADERDATA['INVOICE_IND'] = ''
                IS_HEADERDATA['GROSS_AMOUNT'] = abs(IS_HEADERDATA['GROSS_AMOUNT'])
                for item in IT_ITEMDATA:
                    item['ITEM_AMOUNT'] = abs(item['ITEM_AMOUNT'])

            # srmpyrfc = ZSRM_INCOMINGINVOICE_CREATE.ZSRM_INCOMINGINVOICE_CREATE()
            # result_rfc = srmpyrfc.BAPI_INCOMINGINVOICE_CREATE(self._cr, IS_HEADERDATA, IT_ITEMDATA)
            #
            # if result_rfc['code'] == 1:
            #     raise exceptions.ValidationError('SAP' + result_rfc['message'])
            # else:
            #     self.write({'state': 'done','voucher':result_rfc['EV_INVOICEDOCNUMBER'],'done_date':datetime.date.today()})
            self.write(
                {'state': 'done', 'voucher': int(time.time()), 'done_date': datetime.date.today()})
        return True


class srm_account_order_line(models.Model):
    _name = 'srm.account.order.line'
    _inherit = ['mail.thread']
    _description = "Account Order Line"

    move_id = fields.Many2one('stock.move','Move')
    account_id = fields.Many2one('srm.account.order','Account')
    product_id = fields.Many2one('product.product', '物料')
    product_uom = fields.Many2one('uom.uom', '单位')
    price_unit = fields.Float('单价',digits=dp.get_precision('Product Price'))
    picking_id = fields.Many2one('stock.picking', '作业')
    tax_id = fields.Integer('税')
    name = fields.Char('Name')
    product_uom_qty = fields.Float('数量')
    origin = fields.Char('Origin')

    purchase_order_no = fields.Char('采购单号')
    purchase_order_item = fields.Char('采购单项次')
    purchase_qty = fields.Float('采购数量')
    currency = fields.Char('币别')
    tax_code = fields.Char('税码')
    tax_rate = fields.Char('税率')
    date_done = fields.Date('过账日期')
    picking_type_code = fields.Char('作业类型')
    voucher_code = fields.Char('合格入库凭证')
    voucher_qty = fields.Float('凭证数量')
    price_total_tax = fields.Float('金额(含税)',digits=dp.get_precision('Discount'))
    price_total = fields.Float('金额',digits=dp.get_precision('Discount'))
    tax_price = fields.Float('应付税额',digits=dp.get_precision('Discount'))
    lgort = fields.Char('库位')
    dnnum = fields.Char('送货单号')
    kbetr = fields.Float('价格',digits=dp.get_precision('Product Price'))
    kpein = fields.Float('价格单位')

    def create(self,vals):
        move = self.env['stock.move']
        m = move.browse(vals['move_id'])
        m.account_qty = m.account_qty + vals['product_uom_qty']
        id =  super(srm_account_order_line, self).create(vals)
        return id

