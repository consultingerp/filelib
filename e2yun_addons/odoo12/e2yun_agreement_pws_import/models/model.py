# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from odoo import api, fields, models, tools, _
import xlrd
import time

class AgreementPwsImport(models.TransientModel):
    _name = "agreement.pws.import"
    _description = "agreement pws Import"

    name = fields.Selection((('solution','EAS PWS Industry Solution'), ('odc','EAS PWS ODC')), default="solution", string="The import type", required=True)
    code = fields.Char('代码')
    data = fields.Binary('File', required=True)
    filename = fields.Char('File Name', required=True)

    @api.multi
    def import_excel(self):
        this = self[0]
        file =base64.decodestring(this.data)
        wb = xlrd.open_workbook(file_contents=file)
        print(wb.sheet_names())
        print(len(wb.sheets()))
        if self.name=='solution':
            vals=this.pws_solution(wb)
            agreement=self.env['agreement'].create(vals)
        elif self.name=='odc':
            vals = this.pws_odc(wb)
            agreement = self.env['agreement'].create(vals)
        else:
            return  False
        return {
            'name': 'agreement',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'agreement',
            'res_id': agreement.id,
            'type': 'ir.actions.act_window',
         }


    def pws_solution(self,wb):
        vals = {}
        vals['agreement_type_id'] = 2  # 合同类型
        for table in wb.sheets():
            print(table.nrows)
            print(table.ncols)
            for row in range(table.nrows):
                try:
                    if table.number == 4:
                        if row == 3:
                            cell_value = table.cell(3, 3).value  # 合作伙伴
                            if not (cell_value is None) and not (cell_value is ''):
                                parent = self.env['res.partner'].search(
                                    [('name', 'ilike', cell_value),
                                     ('company_id', '=', self.create_uid.company_id.id)], limit=1)
                                vals['partner_id'] = parent.id

                            cell_value = table.cell(3, 6).value  # 客户所属BU
                            if not (cell_value is None) and not (cell_value is ''):
                                vals['account_bu'] = cell_value
                        if row == 6:
                            cell_value = table.cell(6, 6).value  # 交付所属BU
                            if not (cell_value is None) and not (cell_value is ''):
                                vals['delivery_bu'] = cell_value

                    if table.number == 19:
                        if row == 15:
                            cell_value = table.cell(15, 5).value  # 订单类型
                            if not (cell_value is None) and not (cell_value is ''):
                                vals['order_type'] = cell_value

                        if row == 21:
                            cell_value = table.cell(21, 4).value  # 结算方式
                            if not (cell_value is None) and not (cell_value is ''):
                                vals['payment_term_id'] = cell_value

                    if table.number == 7:
                        # table.row_values(8)
                        if row == 8:
                            cell_value = table.cell(8, 5).value  # 合同名称
                            if not (cell_value is None) and not (cell_value is ''):
                                vals['name'] = cell_value

                        if row == 4:
                            cell_value = table.cell(4, 5).value  # 签约实体
                            if not (cell_value is None) and not (cell_value is ''):
                                vals['account_bu'] = cell_value

                        if row == 16:
                            cell_value = table.cell(16, 6).value  # 币种
                            if not (cell_value is None) and not (cell_value is ''):
                                vals['delivery_bu'] = cell_value

                            cell_value = table.cell(16, 8).value  # 金额
                            if not (cell_value is None) and not (cell_value is ''):
                                vals['delivery_bu'] = cell_value
                        if row == 2:
                            cell_value = table.cell(2, 2).value  # 销售
                            if not (cell_value is None) and not (cell_value is ''):
                                print(cell_value)
                                # vals['create_uid'] = cell_value

                            cell_value = table.cell(2, 5).value  # 项目经理

                            if not (cell_value is None) and not (cell_value is ''):
                                print(cell_value)
                        if row == 13:
                            cell_value = table.cell(13, 5).value  # 项目背景
                            if not (cell_value is None) and not (cell_value is ''):
                                vals['description'] = cell_value

                    if table.number == 8:
                        table.row_values(table.number)
                        if row == 2:
                            cell_value = table.cell(2, 3).value  # 合同起始日期
                            if not (cell_value is None) and not (cell_value is ''):
                                vals['start_date'] = xlrd.xldate.xldate_as_datetime(cell_value, 0)
                            cell_value = table.cell(2, 5).value  # 合同结束日期
                            if not (cell_value is None) and not (cell_value is ''):
                                vals['end_date'] = xlrd.xldate.xldate_as_datetime(cell_value, 0)
                except Exception as e:
                    print(e)
                    pass
        return vals

    def pws_odc(self,wb):
      try:
        vals = {}
        vals['agreement_type_id'] = 1  # 合同类型
        for table in wb.sheets():
            print(table.nrows)
            #print(table.ncols)
            print(table.number)
            if table.number == 5:
                cell_value = table.cell(5, 5).value  # 合作伙伴
                if not (cell_value is None) and not (cell_value is ''):
                    parent = self.env['res.partner'].search(
                        [('name', 'ilike', cell_value),
                     ('company_id', '=', self.create_uid.company_id.id)], limit=1)
                    vals['parent_id'] = parent.id

                cell_value = table.cell(10, 5).value  # 客户所属BU
                if not (cell_value is None) and not (cell_value is ''):
                    vals['account_bu'] = cell_value

                cell_value = table.cell(11, 5).value  # 交付所属BU
                if not (cell_value is None) and not (cell_value is ''):
                    vals['delivery_bu'] = cell_value

                cell_value = table.cell(8, 5).value  # 合同名称
                if not (cell_value is None) and not (cell_value is ''):
                    vals['name'] = cell_value

                cell_value = table.cell(4, 5).value  # 签约实体
                if not (cell_value is None) and not (cell_value is ''):
                    vals['account_bu'] = cell_value

                cell_value = table.cell(16, 6).value  # 币种
                if not (cell_value is None) and not (cell_value is ''):
                    vals['delivery_bu'] = cell_value

                cell_value = table.cell(16, 8).value  # 金额
                if not (cell_value is None) and not (cell_value is ''):
                    vals['delivery_bu'] = cell_value

                cell_value = table.cell(2, 2).value  # 销售
                if not (cell_value is None) and not (cell_value is ''):
                    print(cell_value)
                    # vals['create_uid'] = cell_value

                cell_value = table.cell(2, 5).value  # 项目经理
                if not (cell_value is None) and not (cell_value is ''):
                    print(cell_value)

                cell_value = table.cell(13, 5).value  # 项目背景
                if not (cell_value is None) and not (cell_value is ''):
                    vals['description'] = cell_value
            if table.number == 10:
               cell_value = table.cell(10, 2).value  # 订单类型
               if not (cell_value is None) and not (cell_value is ''):
                    vals['order_type'] = cell_value

               cell_value = table.cell(21, 4).value  # 结算方式
               if not (cell_value is None) and not (cell_value is ''):
                     vals['payment_term_id'] = cell_value

            if table.number == 6:
                cell_value = table.cell(2, 4).value  # 合同起始日期
                if not (cell_value is None) and not (cell_value is ''):
                  vals['start_date'] = xlrd.xldate.xldate_as_datetime(cell_value, 0)
                  cell_value = table.cell(2, 9).value  # 合同结束日期
                if not (cell_value is None) and not (cell_value is ''):
                   vals['end_date'] = xlrd.xldate.xldate_as_datetime(cell_value, 0)
      except Exception as e:
          print(e)
      return vals


# class Agreement(models.Model):
#     _inherit = 'agreement'
#
#     @api.model
#     def create(self, vals):
#         print(vals)
#         return super(Agreement,self).create(vals)


