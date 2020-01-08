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
    sap_ktokd = fields.Char('sap ktokd',required=True)  #账户组
    sap_bu_sort1 = fields.Char('sap bu_sort1',required=True) #sap客户简称 汉字
    sap_bu_sort2 = fields.Char('sap bu_sort2',required=True) #sap客户简称 字母

    def customer_transfer_to_normal(self):
        I_INPUT = {}
        I_INPUT['ZTYPE'] = '0'  # 事务类型  0 创建 1修改
        I_INPUT['KTOKD'] = self.sap_ktokd
        #I_INPUT['KUNNR'] = '200682'  # 客户号
        I_INPUT['NAME_ORG1'] = self.name
        I_INPUT['BU_SORT1'] = self.sap_bu_sort1
        I_INPUT['BU_SORT2'] = self.sap_bu_sort1
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
                    self.sap_kunnr=int(result['I_OUTPUT']['KUNNR'])
                elif result['I_OUTPUT']['ZTYPE']=='E':
                    raise exceptions.ValidationError(result['I_OUTPUT']['ZMESG'])
                else:
                    raise exceptions.ValidationError(result['I_OUTPUT']['ZMESG'])
            else:
                raise exceptions.ValidationError("调用SAP接口失败")
        except BaseException as b:
            raise exceptions.ValidationError(b)

        return super(e2yun_customer_info,self).customer_transfer_to_normal()




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
               or 'mobile' in vals.keys():
            I_INPUT = {}
            I_INPUT['ZTYPE'] = '1'  # 事务类型  0 创建 1修改
            I_INPUT['KUNNR'] =self.sap_kunnr
            I_INPUT['NAME_ORG1'] = vals['name']
            I_INPUT['KTOKD'] = self.sap_ktokd
            I_INPUT['REMARK'] = self.sap_remark
            I_INPUT['BU_SORT1'] = self.sap_bu_sort1
            I_INPUT['BU_SORT2'] = self.sap_bu_sort1
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
                        raise exceptions.ValidationError(result['I_OUTPUT']['ZMESG'])
                else:
                    raise exceptions.ValidationError("调用SAP接口失败")
            except BaseException as b:
                raise exceptions.ValidationError(b)

       return super(res_partner,self).write(vals)
