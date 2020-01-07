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
        I_INPUT['ZTYPE'] = '1'  # 事务类型  0 创建 1修改
        I_INPUT['KTOKD'] = 'C001'  # 账户组
        I_INPUT['KUNNR'] = '200682'  # 客户号
        I_INPUT['NAME_ORG1'] = '接口测试名称修改'  # 客户名称
        I_INPUT['BU_SORT1'] = '789'  # sap客户简称
        I_INPUT['BU_SORT2'] = '55566'  # sap客户简称字母
        I_INPUT['REMARK'] = '接口测试修改'  # 大客户号
        I_INPUT['LANGU'] = 'zh'  # 默认
        I_INPUT['COUNTRY'] = 'CN'  # 默认
        try:
            ZCL_REST_CUSTOMER_RFC=ZCL_REST_CUSTOMER.PYRFC_CRM_CUSTOMER()
            result = ZCL_REST_CUSTOMER_RFC.ZCL_REST_CUSTOMER(I_INPUT)
            if result:
                if result['ZTYPE']=='S':
                    print(result['KUNNR'])
                elif result['ZTYPE']=='E':
                    raise exceptions.ValidationError(result['ZMESG'])
            else:
                raise exceptions.ValidationError("调用SAP接口失败")
        except BaseException as b:
            raise exceptions.ValidationError(b)

        return super(e2yun_customer_info,self).customer_transfer_to_normal()





