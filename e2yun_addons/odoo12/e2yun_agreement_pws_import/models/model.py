# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from odoo import api, fields, models, tools, _
import xlrd
import time
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
class AgreementPwsImport(models.TransientModel):
    _name = "agreement.pws.import"
    _description = "agreement pws Import"

    agreement_id = fields.Many2one(
        "agreement",
        string="agreement")

    new = fields.Boolean(default=False)
    name = fields.Selection((('solution','EAS PWS Industry Solution'), ('odc','EAS PWS ODC')), default="", string="The import type", required=True)
    #code = fields.Char('代码')
    #data = fields.Binary('File', required=True)
    #filename = fields.Char('File Name', required=True)
    import_pws_attachment_ids = fields.Many2many(
        'ir.attachment', 'agreement_import_pws_ir_attachments_rel',
        'id', 'attachment_id', 'Pws 文件')


    @api.multi
    def import_excel(self):
        # if self.new==False and not self.agreement_id:
        #     raise UserError("如果不是新建，请选择需要添加PWS的合同")
        if not self.import_pws_attachment_ids:
            return

        status, headers, content=self.env['ir.http'].binary_content(xmlid=None, model='ir.attachment', id=self.import_pws_attachment_ids[0].id, field='datas', unique=False,
                           filename=None, filename_field='datas_fname', download=False, mimetype=None,
                           default_mimetype='application/octet-stream', related_id=None, access_mode=None,
                           access_token=None,
                           env=None)

        this = self[0]
        #content_base64 = base64.b64decode(content)
        file =base64.decodestring(content)
        wb = xlrd.open_workbook(file_contents=file)
        #print(wb.sheet_names())
        #print(len(wb.sheets()))
        if self.name=='solution':
            vals=this.pws_solution(wb)
            if not self.agreement_id and self.new==True:
                agreement=self.env['agreement'].create(vals)
            else:
                agreement=self.agreement_id
        elif self.name=='odc':
            vals = this.pws_odc(wb)
            if not self.agreement_id and self.new == True:
                agreement = self.env['agreement'].create(vals)
            else:
                agreement = self.agreement_id
        else:
            return  False

        #写行项目
        if agreement and vals:
            # Model = self.env['ir.attachment']
            # attachment = Model.create({
            #     'name': self.filename,
            #     'datas': file,
            #     'datas_fname': self.filename,
            #     'res_model': 'agreement',
            #     'res_id': 0
            # })
            #创建行项目
            agreement_pws_lineObj=self.env['agreement.pws.line']
            agreement_pws_lineObj.create({
                'agreement_id':agreement.id,
                'pid': '',
                'cgm': vals['x_studio_cgmpd'] if 'x_studio_cgmpd' in vals.keys() else '',
                'x_studio_htje': vals['x_studio_htje'] if 'x_studio_htje' in vals.keys() else '',
                'x_studio_jfssbu': vals['x_studio_jfssbu'] if 'x_studio_jfssbu' in vals.keys() else '',
                'x_studio_htbz': vals['x_studio_htbz'] if 'x_studio_htbz' in vals.keys() else '',
                'x_studio_mjhtje':vals['x_studio_mjhtje']if 'x_studio_mjhtje' in vals.keys() else '',
                'pws_line_attachment_ids':[[6, False, [self.import_pws_attachment_ids[0].id]]],
            })

            #写行项目附件
            #sql = "INSERT into agreement_line_pws_ir_attachments_rel(id,attachment_id)VALUES (%s,%s)"
            #self._cr.execute(sql, (agreement_pws_lineData.id, attachment.id))

            #读取行项目数据汇总  计算CGM
            sum_cgm=0
            sum_amount=0
            if agreement.pws_line_ids:
                for pwsObj in agreement.pws_line_ids:
                    #x_studio_cgmpd
                    if pwsObj.cgm and pwsObj.x_studio_htje:
                        cgm=pwsObj.cgm.strip('%')
                        sum_cgm=sum_cgm+(pwsObj.x_studio_htje*(float(cgm)/100))
                        sum_amount=sum_amount+pwsObj.x_studio_htje
                if sum_cgm!=0 and sum_amount!=0:
                    x_studio_cgmpd=  str(round((sum_cgm/sum_amount) * 100)) + "%"
                    sql = "update agreement set x_studio_cgmpd=%s where id=%s"
                    self._cr.execute(sql, (x_studio_cgmpd, agreement.id))



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
      vals['agreement_type_id'] = 1  # 合同类型
      vals['name'] = "/"
      for table in wb.sheets():
        if table.number == 7:
            cell_value = table.cell(5, 5).value  # 客户名称与合作伙伴
            if not (cell_value is None) and not (cell_value is ''):
                parent = self.env['res.partner'].search(
                    [('name', 'ilike', cell_value),
                     ('company_id', '=', self.create_uid.company_id.id)], limit=1)
                if parent:
                    vals['x_studio_partner_id'] = parent.id
                    #vals['x_studio_customer_name'] = cell_value
                else:
                    raise UserError(("客户没有维护: %s")%(cell_value) )


            cell_value = table.cell(10, 5).value  # 客户所属BU
            if not (cell_value is None) and not (cell_value is ''):
                print(cell_value)
                crm_teamObj = self.env['crm.team'].search(
                    [('name', 'ilike', cell_value)], limit=1)
                if crm_teamObj:
                    vals['x_studio_customer_bu'] = crm_teamObj.id

            cell_value = table.cell(11, 5).value  # 交付所属BU
            if not (cell_value is None) and not (cell_value is ''):
                vals['x_studio_jfssbu'] = cell_value

            cell_value = table.cell(6, 5).value  # 机会编号
            if not (cell_value is None) and not (cell_value is ''):
                import math
                vals['x_studio_jhhm_id'] = math.floor(cell_value)

            cell_value = table.cell(8, 5).value  # 项目名称
            if not (cell_value is None) and not (cell_value is ''):
                vals['x_studio_xmmc'] = cell_value

            cell_value = table.cell(4, 5).value  # 签约实体
            if not (cell_value is None) and not (cell_value is ''):
                vals['x_studio_signing_entity'] = cell_value

            cell_value = table.cell(16, 6).value  # 币种
            if not (cell_value is None) and not (cell_value is ''):
                if cell_value=='USD':
                    vals['x_studio_usd'] = cell_value
                    x_studio_htje='x_studio_mjhtje'
                else:
                    vals['x_studio_htbz'] = cell_value
                    x_studio_htje = 'x_studio_htje'

            cell_value = table.cell(16, 8).value  # 金额
            if not (cell_value is None) and not (cell_value is ''):
                vals[x_studio_htje] = ("%.2f" % float(cell_value))



            cell_value = table.cell(2, 2).value  # 销售
            if not (cell_value is None) and not (cell_value is ''):
                parent = self.env['res.partner'].search(
                    [('name', 'ilike', cell_value),
                     ('company_id', '=', self.create_uid.company_id.id)], limit=1)
                if parent:
                    user = self.env['res.users'].search(
                        [('partner_id', '=', parent.id)], limit=1)
                    if user:
                        vals['x_studio_xsdb1'] = user.id

            cell_value = table.cell(2, 6).value  # 项目经理
            if not (cell_value is None) and not (cell_value is ''):
                parent = self.env['res.partner'].search(
                    [('name', 'ilike', cell_value),
                     ('company_id', '=', self.create_uid.company_id.id)], limit=1)
                if parent:
                    user = self.env['res.users'].search(
                        [('partner_id', '=', parent.id)], limit=1)
                    if user:
                        vals['x_studio_xmjl1'] = user.id

            cell_value = table.cell(13, 5).value  # 项目背景
            if not (cell_value is None) and not (cell_value is ''):
                vals['x_studio_xmbj'] = cell_value

        if table.number == 8:
           cell_value = table.cell(2, 3).value  # 合同起始日期
           if not (cell_value is None) and not (cell_value is ''):
                    vals['start_date'] = xlrd.xldate.xldate_as_datetime(cell_value, 0)
           cell_value = table.cell(2, 5).value  # 合同结束日期
           if not (cell_value is None) and not (cell_value is ''):
                    vals['end_date'] = xlrd.xldate.xldate_as_datetime(cell_value, 0)

      table = wb.sheets()[16]
      cell_value = table.cell(10, 4).value  # 收入确认类型
      if not (cell_value is None) and not (cell_value is ''):
          vals['x_studio_srqrlx'] = cell_value

      cell_value = table.cell(10, 6).value  # 产品线
      if not (cell_value is None) and not (cell_value is ''):
          vals['x_studio_cpx'] = cell_value

      cell_value = table.cell(10, 2).value  # 订单类型
      if not (cell_value is None) and not (cell_value is ''):
         # print(cell_value)
          vals['x_studio_order_type1'] = cell_value
      cell_value = table.cell(21, 4).value  # 付款方式
      if not (cell_value is None) and not (cell_value is ''):
          vals['x_studio_payment_method'] = cell_value

      cell_value = table.cell(21, 2).value  # 回款账龄
      if not (cell_value is None) and not (cell_value is ''):
          vals['x_studio_hkzl'] = cell_value

      return vals

    def pws_odc(self,wb):
      try:
        vals = {}
        vals['agreement_type_id'] = 1  # 合同类型
        vals['name']='/'
        for table in wb.sheets():
            if table.number == 5:
                cell_value = table.cell(5, 5).value  # 客户名称
                if not (cell_value is None) and not (cell_value is ''):
                    parent = self.env['res.partner'].search(
                        [('name', 'ilike', cell_value),
                     ('company_id', '=', self.create_uid.company_id.id)], limit=1)
                    if parent:
                        vals['x_studio_partner_id'] = parent.id
                        # vals['x_studio_customer_name'] = cell_value
                    else:
                        raise UserError(("客户没有维护: %s") % (cell_value))

                cell_value = table.cell(6, 5).value  #机会编号
                if not (cell_value is None) and not (cell_value is ''):
                    import math
                    vals['x_studio_jhhm_id'] = math.floor(cell_value)

                cell_value = table.cell(10, 5).value  # 客户所属BU
                if not (cell_value is None) and not (cell_value is ''):
                    print(cell_value)
                    crm_teamObj = self.env['crm.team'].search(
                        [('name', 'ilike', cell_value)], limit=1)
                    if crm_teamObj:
                        vals['x_studio_customer_bu'] = crm_teamObj.id

                cell_value = table.cell(11, 5).value  # 交付所属BU
                if not (cell_value is None) and not (cell_value is ''):
                    vals['x_studio_jfssbu'] = cell_value

                cell_value = table.cell(8, 5).value  # 项目名称
                if not (cell_value is None) and not (cell_value is ''):
                    vals['x_studio_xmmc'] = cell_value

                cell_value = table.cell(4, 5).value  # 签约实体
                if not (cell_value is None) and not (cell_value is ''):
                    vals['x_studio_signing_entity'] = cell_value

                cell_value = table.cell(16, 6).value  # 币种
                if not (cell_value is None) and not (cell_value is ''):
                    vals['x_studio_htbz'] = cell_value.strip()

                cell_value = table.cell(16, 8).value  # 金额
                if not (cell_value is None) and not (cell_value is ''):
                    vals['x_studio_htje'] = cell_value

                cell_value = table.cell(2, 2).value  # 销售
                if not (cell_value is None) and not (cell_value is ''):
                    parent = self.env['res.partner'].search(
                        [('name', 'ilike', cell_value),
                         ('company_id', '=', self.create_uid.company_id.id)], limit=1)
                    if parent:
                       user=self.env['res.users'].search(
                            [('partner_id', '=', parent.id)], limit=1)
                       if user:
                          vals['x_studio_xsdb1'] = user.id


                cell_value = table.cell(2, 6).value  # 项目经理
                if not (cell_value is None) and not (cell_value is ''):
                    parent = self.env['res.partner'].search(
                        [('name', 'ilike', cell_value),
                         ('company_id', '=', self.create_uid.company_id.id)], limit=1)
                    if parent:
                        user = self.env['res.users'].search(
                            [('partner_id', '=', parent.id)], limit=1)
                        if user:
                            vals['x_studio_xmjl1'] = user.id

                cell_value = table.cell(13, 5).value  # 项目背景
                if not (cell_value is None) and not (cell_value is ''):
                    vals['x_studio_xmbj'] = cell_value

            if table.number == 10:
               cell_value = table.cell(10, 2).value  # 订单类型
               if not (cell_value is None) and not (cell_value is ''):
                    #print(cell_value)
                    vals['x_studio_order_type1'] = cell_value

               cell_value = table.cell(21, 4).value  # 付款方式
               if not (cell_value is None) and not (cell_value is ''):
                      #x_studio_fkfs
                     vals['x_studio_payment_method'] = cell_value

               cell_value = table.cell(10, 4).value  # 收入确认类型
               if not (cell_value is None) and not (cell_value is ''):
                   vals['x_studio_srqrlx'] = cell_value

               cell_value = table.cell(10, 6).value  # 产品线
               if not (cell_value is None) and not (cell_value is ''):
                   vals['x_studio_cpx'] = cell_value

               cell_value = table.cell(21, 2).value  # 回款账龄
               if not (cell_value is None) and not (cell_value is ''):
                   vals['x_studio_hkzl'] = cell_value

            if table.number == 6:
                cell_value = table.cell(2, 4).value  # 合同起始日期
                if not (cell_value is None) and not (cell_value is ''):
                  vals['start_date'] = xlrd.xldate.xldate_as_datetime(cell_value, 0)
                  cell_value = table.cell(2, 9).value  # 合同结束日期
                if not (cell_value is None) and not (cell_value is ''):
                   vals['end_date'] = xlrd.xldate.xldate_as_datetime(cell_value, 0)

            if table.number == 2:
                cell_value = table.cell(9, 5).value  # 税后未计息前合同利润率
                if not (cell_value is None) and not (cell_value is ''):
                    #vals['x_studio_shwjxq'] = str(round(cell_value*100))+"%"
                    vals['x_studio_cgmpd'] = str(round(cell_value*100))+"%"

      except Exception as e:
          raise UserError(e)
      return vals



