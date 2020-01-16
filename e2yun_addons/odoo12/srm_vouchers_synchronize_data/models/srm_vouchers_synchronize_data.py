#!/usr/bin/python
# -*- coding: UTF-8 -*-
from odoo import models, fields, tools, api, exceptions
try:
    from odoo.addons.srm_pyrfc import ZSRM_BAPI_MATERIAL_DOCUMENT
    from odoo.addons.srm_pyrfc import get_pyrfc_conn
except :
    pass
import datetime
import re
class Srm_vouchers_synchronize_data(models.Model):
    _name = "vouchers.synchronize.data"
    _table = 'vouchers_synchronize_data'
    mblnr = fields.Char('mblnr', )
    lfbnr = fields.Char('lfbnr')
    lfpos = fields.Char('lfpos')
    matnr = fields.Char('matnr')
    werks = fields.Char('werks')
    lgort = fields.Char('lgort')
    bwart = fields.Char('bwart')
    erfmg = fields.Float('erfmg')
    erfme = fields.Char('erfme')
    ebeln = fields.Char('ebeln')
    ebelp = fields.Char('ebelp')
    lifnr = fields.Char('lifnr')
    budat = fields.Char('budat')
    bukrs = fields.Char('bukrs')
    kbetr = fields.Char('kbetr')
    mwskz = fields.Char('mwskz')
    kpein = fields.Char('kpein')
    waers = fields.Char('waers')
    menge = fields.Float('menge')
    bedat = fields.Char('bedat')

    def zsrm_bapi_material_document_m_task(self,mblnr,bwart,mjahr,limit, context=None):
        cr=self._cr
        if mblnr == '0':
            # 取最大的凭证号增量同步
            sql = """select max(mblnr) from vouchers_synchronize_data where bwart = %s """
            cr.execute(sql, [bwart])
            sql_result = cr.fetchone()
            if sql_result and sql_result[0]:
                mblnr = sql_result[0]

        bapi=ZSRM_BAPI_MATERIAL_DOCUMENT.ZSRM_BAPI_MATERIAL_DOCUMENT()
        result=bapi.zsrm_bapi_material_document_m(cr,mblnr,bwart,mjahr,limit,context)
        results = []
        for val in result['ET_MSEG']:
            lfpos = re.sub(r"\b0*([1-9][0-9]*|0)", r"\1", val['LFPOS'])
            sql="select id from vouchers_synchronize_data where mblnr=%s and lfpos=%s and ebeln=%s and ebelp=%s   "
            cr.execute(sql,(val['MBLNR'],lfpos,val['EBELN'],val['EBELP']))
            sql_result = cr.fetchone()
            if sql_result:
                continue
            val_temp={}

            val_temp['mblnr'] = val['MBLNR']
            val_temp['lfbnr'] = val['LFBNR']
            val_temp['lfpos'] = lfpos
            val_temp['matnr'] = val['MATNR']
            val_temp['werks'] = val['WERKS']
            val_temp['lgort'] = val['LGORT']
            val_temp['bwart'] = val['BWART']
            val_temp['erfmg'] = val['ERFMG']
            val_temp['erfme'] = val['ERFME']
            val_temp['ebeln'] = val['EBELN']
            val_temp['ebelp'] = val['EBELP']
            val_temp['lifnr'] = val['LIFNR']
            val_temp['budat'] = val['BUDAT']
            val_temp['bukrs'] = val['BUKRS']
            val_temp['kbetr'] = val['KBETR']
            val_temp['mwskz'] = val['MWSKZ']
            val_temp['kpein'] = val['KPEIN']
            val_temp['waers'] = val['WAERS']
            val_temp['menge'] = val['MENGE']
            val_temp['bedat'] = val['BEDAT']

            new_id = super(Srm_vouchers_synchronize_data, self).create(val_temp)


            if bwart == '161' or bwart == '162':
                results.append(val_temp)
            else:
                #修改picking确认收货标识
                sql = """select picking_id from  sap_voucher where matdoc = %s and linemark = %s """
                cr.execute(sql,(val_temp['lfbnr'],val_temp['lfpos']))
                picking_ids = cr.dictfetchall()
                picking_model = self.env['stock.picking']
                for p in picking_ids:
                    picking_obj = picking_model.browse(p['picking_id'])
                    if not picking_obj.confirm_transfer:
                        picking_obj.confirm_transfer = True

        if results:
            dicts = {}
            for r in results:
                if r['mblnr'] in dicts:
                    dicts[r['mblnr']].append(r)
                else:
                    l = [r]
                    dicts[r['mblnr']] = l
            for d in dicts:
                list = dicts[d]
                partner_id = self.env['res.partner'].search([('supplier_code', '=', list[0]['lifnr'])], limit=1)
                picking_type_id = self.env['stock.picking.type'].search([('move_type', '=', '161')],limit=1)
                company_id = self.env['res.company'].search([('company_code', '=', list[0]['bukrs'])], limit=1)
                picking_location_id = self.env['stock.location'].search([('barcode', '=', list[0]['werks'] + '-' + list[0]['lgort'])], limit=1)
                supplier_location_id = self.env['stock.location'].search([('usage', '=', 'supplier')], limit=1)
                val = {
                    'picking_type_id': int(picking_type_id[0].id),
                    'move_type': 'direct',
                    'company_id': int(company_id[0].id),
                    'state': 'draft',
                    'partner_id': int(partner_id[0].id),
                    'name': list[0]['mblnr'],
                    'origin': list[0]['ebeln'],
                    'confirm_transfer': True if bwart == '161' else False,
                    'date_done': datetime.datetime.strptime(list[0]['budat'], "%Y%m%d"),
                    'location_id': picking_location_id[0].id if bwart == '161' else supplier_location_id[0].id,
                    'location_dest_id': supplier_location_id[0].id if bwart == '161' else picking_location_id[0].id
                }
                picking_id = self.env['stock.picking'].create(val)
                move_lins = []
                for l in list:
                    unit_id = self.env['product.uom'].search([('name','=',l['erfme'])],limit=1)
                    product_id = self.env['product.product'].search([('default_code','=',l['matnr'])],limit=1)
                    if not product_id:
                        continue
                    location_id = self.env['stock.location'].search([('barcode','=',l['werks']+'-'+l['lgort'])],limit=1)
                    warehouse_id = self.env['stock.warehouse'].search([('factory_code','=',l['werks'])],limit=1)
                    tax_id = self.env['account.tax'].search([('name','=',l['mwskz'])],limit=1)

                    move = {'origin': l['lfpos'],
                            'name': l['ebelp'],
                            'partner_id': partner_id[0].id,
                            'product_uom': unit_id[0].id,
                            'price_unit': float(l['kbetr']) / float(l['kpein']),
                            'product_uom_qty': l['erfmg'],
                            'date': datetime.datetime.now(),
                            'picking_type_id': picking_type_id[0].id,
                            'location_id': location_id[0].id if bwart == '161' else supplier_location_id[0].id,
                            'company_id': company_id[0].id,
                            'state': 'draft',
                            'date_expected': datetime.datetime.now(),
                            'warehouse_id': warehouse_id[0].id,
                            'product_id': product_id[0].id,
                            'location_dest_id': supplier_location_id[0].id if bwart == '161' else location_id[0].id,
                            'picking_id': picking_id.id,
                            'tax_id': int(tax_id[0].id),
                            'remark': 'ret_order'
                        }
                    self.env['stock.move'].create(move)
                sql = """ update stock_picking set state = 'done' where id =  %s """
                cr.execute(sql, ([picking_id.id]))
                sql = """ update stock_move set state = 'done' where picking_id =  %s """
                cr.execute(sql, ([picking_id.id]))
