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
      result = conn.call('ZCL_REST_CUSTOMER', I_INPUT=I_INPUT)
    except BaseException as b:
        raise exceptions.ValidationError(b)

    finally:
        if conn:
            conn.close()
    return result


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
