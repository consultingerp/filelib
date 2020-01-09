#!/usr/bin/python
# -*- coding: UTF-8 -*-
try:
    from .import get_pyrfc_conn
    import pyrfc
except BaseException as b:
    print(b)
    pass
from odoo import exceptions


class PYRFC_CRM_CUSTOMER():
    
  def ZCL_REST_CUSTOMER(self,I_INPUT):

    conn = None
    getconn = get_pyrfc_conn.get_pyrfc_conntion()
    conn = getconn.get_conn()
    try:
      self.zerofill(I_INPUT)
      result = conn.call('ZCL_REST_CUSTOMER', I_INPUT=I_INPUT)
    except BaseException as b:
        raise exceptions.ValidationError(b)

    finally:
        if conn:
            conn.close()
    return result


  def zerofill(self,map):
      if 'KUNNR' in map.keys() and map['KUNNR']:
          KUNNR = ('%010d' % map['KUNNR'])
          map["KUNNR"] = KUNNR
          #
          # KUNNR=map['KUNNR']
          # length_temp=len(KUNNR)
          # if length_temp<10:
          #     zero = ""
          #     i=0
          #     zerosize=10-length_temp
          #     while i<zerosize:
          #         zero+="0"
          #         i=i+1
          #     map["KUNNR"]=zero+KUNNR;
      return  map
