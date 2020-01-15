#!/usr/bin/python
# -*- coding: UTF-8 -*-
try:
    from odoo.addons.srm_pyrfc import get_pyrfc_conn
    import pyrfc
except:
    pass
from odoo import exceptions

class ZSRM_INCOMINGINVOICE_CREATE():
    
  def BAPI_INCOMINGINVOICE_CREATE(self,cr,H_IS_HEADERDATA,L_IT_ITEMDATA):
    rfc_result_map={};
    conn = None
    try:
      getconn = get_pyrfc_conn.get_pyrfc_conntion()
      conn = getconn.get_conn(cr)
      # user = 'ddic_kf'
      # passwd = '123456'
      # conn = pyrfc.Connection(user=user,
      #                         passwd=passwd,
      #                         ashost='192.168.1.186',
      #                         sysnr='00',
      #                         client='800',
      #                         saprouter='/H/116.6.193.100/H/',
      #                         lang='zh')
      result = conn.call('ZSRM_INCOMINGINVOICE_CREATE',IS_HEADERDATA=H_IS_HEADERDATA,IT_ITEMDATA=L_IT_ITEMDATA)
      rfc_result_map['EV_INVOICEDOCNUMBER'] = result['EV_INVOICEDOCNUMBER']
      rfc_result_map['EV_FISCALYEAR'] = result['EV_FISCALYEAR']
      rfc_result_map['code'] = 0
      for res in result['IT_RETURN']:
          rfc_result_map['message']=res['MESSAGE'];
          rfc_result_map['code'] = 1
    except BaseException as b:
        rfc_result_map['message'] = b;
        rfc_result_map['code'] = 1
        raise exceptions.ValidationError(b)
        pass
    finally:
        if conn:
            conn.close()
    return rfc_result_map

#
#
# srmpyrfc = ZSRM_INCOMINGINVOICE_CREATE()
# GOODSMVT_ITEM=[]
# reload(sys)
# sys.setdefaultencoding('utf8')
# GOODSMVT_HEADER = {'INVOICE_IND': 'X',
#                    'DOC_TYPE':'RE',
#                    'REF_DOC_NO':'11',
#                    'DOC_DATE': '20181214', 'PSTNG_DATE': '20181214',
#                    'COMP_CODE':'1000','CURRENCY':'USD','GROSS_AMOUNT':11.6,'CALC_TAX_IND':'X'}
# #:str(datetime.date.today()).replace('-', '')
# GOODSMVT_ITEM_MAP={'INVOICE_DOC_ITEM': '000001',
#                        'PO_NUMBER': '4500000152',
#                         'PO_ITEM': '00010',
#                         'REF_DOC':'5000064503',
#                         'REF_DOC_IT':'0001',
#                        'REF_DOC_YEAR': '2018',
#                        'TAX_CODE': 'J5',
#                        'ITEM_AMOUNT': 10,
#                        'QUANTITY': 1,
#                        'PO_UNIT': 'PC',
#                        }
# GOODSMVT_ITEM.append(GOODSMVT_ITEM_MAP)
#
# result_rfc=srmpyrfc.BAPI_INCOMINGINVOICE_CREATE('',GOODSMVT_HEADER,GOODSMVT_ITEM)
# if result_rfc['code']==1:
#     print(result_rfc['message'])
# else:
#     print(result_rfc['EV_INVOICEDOCNUMBER'])
