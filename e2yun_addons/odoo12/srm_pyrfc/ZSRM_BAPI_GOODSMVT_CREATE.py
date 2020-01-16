#!/usr/bin/python
# -*- coding: UTF-8 -*-
try:
    from odoo.addons.srm_pyrfc import get_pyrfc_conn
    import pyrfc
except:
    pass
from odoo import exceptions


class ZBAPI_GOODSMVT_CREATE():
    
  def BAPI_GOODSMVT_CREATE(self,cr,GOODSMVT_HEADER,GOODSMVT_ITEM,GM_CODE):
    rfc_result_map={};
    conn = None
    try:
      # reload(sys)
      # sys.setdefaultencoding('utf8')
      GOODSMVT_CODE = {'GM_CODE': GM_CODE}
      #db_user=openerp.tools.config['db_user']
      # NO_MORE_GR='X',
      getconn = get_pyrfc_conn.get_pyrfc_conntion()
      conn = getconn.get_conn(cr)
      zbapi_goodsmvt_create = ZBAPI_GOODSMVT_CREATE()
      GOODSMVT_ITEM_S=[]
      for item in GOODSMVT_ITEM:
          #GOODSMVT_ITEM_S.append(zbapi_goodsmvt_create.zerofill(item))
          GOODSMVT_ITEM_S.append(item)
      result = conn.call('ZSRM_BAPI_GOODSMVT_CREATE', GOODSMVT_HEADER=GOODSMVT_HEADER, GOODSMVT_CODE=GOODSMVT_CODE,
                         GOODSMVT_ITEM=GOODSMVT_ITEM_S)
      rfc_result_map['DOC_YEAR'] = result['GOODSMVT_HEADRET']['DOC_YEAR']
      rfc_result_map['MAT_DOC'] = result['GOODSMVT_HEADRET']['MAT_DOC']
      rfc_result_map['code'] = 0
      for res in result['RETURN']:
          rfc_result_map['message']=res['MESSAGE']
          rfc_result_map['code'] = 1
    except BaseException as b:
        rfc_result_map['message'] = b
        rfc_result_map['code'] = 1
        raise exceptions.ValidationError(b)
        pass
    finally:
        if conn:
            conn.close()
    return rfc_result_map


  def zerofill(self,map):
      zerosize = 0
      zero = "";
      length_temp = 0;
      if map['MATERIAL']:
          MATERIAL=map['MATERIAL']
          length_temp=len(MATERIAL)
          if length_temp<18:
              zero = ""
              i=0
              zerosize=18-length_temp
              while i<zerosize:
                  zero+="0"
                  i=i+1
              map["MATERIAL"]=zero+MATERIAL;

      if map['PO_NUMBER']:
          PO_NUMBER=map['PO_NUMBER']
          length_temp=len(PO_NUMBER)
          if length_temp<10:
              zero=""
              i=0
              zerosize=10-length_temp
              while i<zerosize:
                  zero+="0"
                  i=i+1
              map["PO_NUMBER"] = zero + PO_NUMBER;




      return  map



# srmpyrfc = ZBAPI_GOODSMVT_CREATE()
# GOODSMVT_ITEM=[]
# reload(sys)
# sys.setdefaultencoding('utf8')
# GOODSMVT_HEADER = {'PSTNG_DATE': '20180630',
#                    'DOC_DATE': '20180630', 'REF_DOC_NO': 'PO00012',
#                    'HEADER_TXT': str.encode('odoo收货')}
# #:str(datetime.date.today()).replace('-', '')
#
# GOODSMVT_ITEM_MAP={'MATERIAL': '402000483',
#                        'PLANT': '1000',
#                        'STGE_LOC': '1020',
#                        'MOVE_TYPE': '101',
#                        'ENTRY_UOM': 'PC',
#                        'ENTRY_QNT': 1,
#                        'QUANTITY': 10.000,
#                        'PO_NUMBER': '3000559',
#                        'PO_ITEM': '10',
#                       'MVT_IND': str.encode('B')
#                        }
# GOODSMVT_ITEM.append(GOODSMVT_ITEM_MAP)
#
# result_rfc=srmpyrfc.BAPI_GOODSMVT_CREATE(GOODSMVT_HEADER,GOODSMVT_ITEM)
# if result_rfc['code']==1:
#     print(result_rfc['message'])
# else:
#     print(result_rfc['MAT_DOC'])
