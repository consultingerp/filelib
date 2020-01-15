#!/usr/bin/python
# -*- coding: UTF-8 -*-
try:
    from odoo.addons.srm_pyrfc import  get_pyrfc_conn
    import pyrfc
except BaseException as b:
    print(b)

from odoo import exceptions
import importlib,sys

class ZSRM_BAPI_MATERIAL_DOCUMENT():

    def zsrm_bapi_material_document_m(self,cr,mblnr,bwart,mjahr,limit,context=None):
        try:
            importlib.reload(sys)
            conn=""
            getconn = get_pyrfc_conn.get_pyrfc_conntion()
            conn = getconn.get_conn(cr)
            result=""
            if mblnr and bwart:
                result = conn.call('ZSRM_BAPI_MATERIAL_DOCUMENT',MBLNR=mblnr, BWART=bwart,MJAHR=mjahr, LIMIT=limit)
            return result
        except BaseException as b:
            raise  exceptions.ValidationError(b)
            pass
        finally:
            if conn:
                conn.close()




