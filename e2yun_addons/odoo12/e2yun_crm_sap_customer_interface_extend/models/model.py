# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
try:
    from odoo.addons.e2yun_crm_sap_customer_interface_extend.rfc import ZCL_REST_CUSTOMER

except BaseException as b:
    print(b)
    pass
from odoo import exceptions

class e2yun_customer_info(models.Model):
    _inherit = 'e2yun.customer.info'

    sap_kunnr=fields.Char('sap kunnr' ,readonly=True) #SAP客户编号
    sap_remark = fields.Char('sap remark',required=True) #大客户号
    sap_ktokd = fields.Char('sap ktokd',default='C001',required=True)  #账户组
    sap_bu_sort1 = fields.Char('sap bu_sort1',required=True) #sap客户简称 汉字
    sap_bu_sort2 = fields.Char('sap bu_sort2',required=True) #sap客户简称 字母

    def customer_transfer_to_normal(self):

        partnerCheck = self.env['res.partner'].search([('name', '=', self.name)])
        if partnerCheck:
            raise exceptions.UserError(u'' + self.name + ',已经存在')
            return False

        if self.sap_ktokd and self.sap_ktokd=='C002':
            return super(e2yun_customer_info, self).customer_transfer_to_normal()
        try:
            partner=super(e2yun_customer_info, self).customer_transfer_to_normal()
        except BaseException as b:
            raise exceptions.ValidationError(b)
        if not partner:
            raise exceptions.ValidationError(u'生成正式客户失败')
        I_INPUT = {}
        I_INPUT['ZTYPE'] = '0'  # 事务类型  0 创建 1修改
        I_INPUT['KTOKD'] = self.sap_ktokd
        #I_INPUT['KUNNR'] = '200682'  # 客户号
        I_INPUT['NAME_ORG1'] = self.name
        I_INPUT['BU_SORT1'] = self.sap_bu_sort1
        I_INPUT['BU_SORT2'] = self.sap_bu_sort2
        I_INPUT['REMARK'] = self.sap_remark
        I_INPUT['LANGU'] = 'zh'  # 默认
        I_INPUT['COUNTRY'] = 'CN'  # 默认
        if self.zip:
            I_INPUT['POST_CODE1'] = self.zip  # 电话
            STREET = ""
            if self.street:
                STREET = str(self.street)
            if self.street2:
                STREET = STREET + str(self.street2)

            if STREET != "":
                I_INPUT['STREET'] = STREET
            if self.city:
                I_INPUT['CITY1'] = str(self.city)
            REGION = ""
            if self.state_id.name:
                REGION = str(self.state_id.name)
            if self.country_id.name:
                REGION = REGION + str(self.country_id.name)
            # if REGION!="":
            #     I_INPUT['REGION'] =REGION
            if self.mobile:
                I_INPUT['TEL_NUMBER'] = self.mobile  # 电话



        try:
            ZCL_REST_CUSTOMER_RFC=ZCL_REST_CUSTOMER.PYRFC_CRM_CUSTOMER()
            result = ZCL_REST_CUSTOMER_RFC.ZCL_REST_CUSTOMER(I_INPUT)
            if result:
                if result['I_OUTPUT']['ZTYPE']=='S':
                    #self.sap_kunnr=int(result['I_OUTPUT']['KUNNR'])
                    partner.sap_kunnr=int(result['I_OUTPUT']['KUNNR'])
                elif result['I_OUTPUT']['ZTYPE']=='E':
                    raise exceptions.ValidationError("SAP返回消息"+str(result['I_OUTPUT']['ZMESG']))
                else:
                    raise exceptions.ValidationError("SAP返回消息"+str(result['I_OUTPUT']['ZMESG']))
            else:
                raise exceptions.ValidationError("调用SAP接口失败")
        except BaseException as b:
            raise exceptions.ValidationError(b)

        return True




class res_partner(models.Model):
    _inherit = 'res.partner'

    sap_kunnr=fields.Char('sap kunnr') #SAP客户编号
    sap_remark = fields.Char('sap remark',required=True) #大客户号
    sap_ktokd = fields.Char('sap ktokd',required=True)  #账户组
    sap_bu_sort1 = fields.Char('sap bu_sort1',required=True) #sap客户简称 汉字
    sap_bu_sort2 = fields.Char('sap bu_sort2',required=True) #sap客户简称 字母


    def write(self, vals):
       if 'name' in vals.keys()\
               or 'sap_remark' in vals.keys() \
               or 'street' in vals.keys() \
               or 'city' in vals.keys() \
               or 'state_id' in vals.keys() \
               or 'sap_bu_sort1' in vals.keys() \
               or 'sap_bu_sort2' in vals.keys() \
               or 'sap_remark' in vals.keys() \
               or 'mobile' in vals.keys():
            I_INPUT = {}
            I_INPUT['ZTYPE'] = '1'  # 事务类型  0 创建 1修改
            if not self.sap_kunnr or  not self.sap_remark :
                return super(res_partner, self).write(vals)
            I_INPUT['KUNNR'] =self.sap_kunnr
            if 'name' in vals.keys() and vals['name']:
                I_INPUT['NAME_ORG1'] = vals['name']
            else:
                I_INPUT['NAME_ORG1'] = self.name

            if 'sap_ktokd' in vals.keys() and vals['sap_ktokd']:
                I_INPUT['KTOKD'] = vals['sap_ktokd']
            else:
                I_INPUT['KTOKD'] = self.sap_ktokd

            if 'sap_remark' in vals.keys() and vals['sap_remark']:
                I_INPUT['REMARK'] = vals['sap_remark']
            else:
                I_INPUT['REMARK'] = self.sap_remark

            if 'sap_bu_sort1' in vals.keys() and vals['sap_bu_sort1']:
                I_INPUT['BU_SORT1'] = vals['sap_bu_sort1']
            else:
                I_INPUT['BU_SORT1'] = self.sap_bu_sort1


            if 'sap_bu_sort2' in vals.keys() and vals['sap_bu_sort2']:
                I_INPUT['BU_SORT2'] = vals['sap_bu_sort2']
            else:
                I_INPUT['BU_SORT2'] = self.sap_bu_sort2


            I_INPUT['LANGU'] = 'zh'  # 默认
            I_INPUT['COUNTRY'] = 'CN'  # 默认

            if self.zip:
                I_INPUT['POST_CODE1'] = self.zip  # 电话
                STREET = ""
                if self.street:
                    STREET = str(self.street)
                if self.street2:
                    STREET = STREET + str(self.street2)

                if STREET != "":
                    I_INPUT['STREET'] = STREET
                if self.city:
                    I_INPUT['CITY1'] = str(self.city)
                REGION = ""
                if self.state_id.name:
                    REGION = str(self.state_id.name)
                if self.country_id.name:
                    REGION = REGION + str(self.country_id.name)
                # if REGION!="":
                #     I_INPUT['REGION'] =REGION
                if self.mobile:
                    I_INPUT['TEL_NUMBER'] = self.mobile  # 电话

            try:
                ZCL_REST_CUSTOMER_RFC = ZCL_REST_CUSTOMER.PYRFC_CRM_CUSTOMER()
                result = ZCL_REST_CUSTOMER_RFC.ZCL_REST_CUSTOMER(I_INPUT)
                if result:
                    if result['I_OUTPUT']['ZTYPE'] != 'S':
                        raise exceptions.ValidationError("SAP返回消息" + str(result['I_OUTPUT']['ZMESG']))
                else:
                    raise exceptions.ValidationError("调用SAP接口失败")
            except BaseException as b:
                raise exceptions.ValidationError(b)

       return super(res_partner,self).write(vals)
