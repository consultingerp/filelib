try:
    from odoo.addons.srm_pyrfc import  get_pyrfc_conn
    import pyrfc
except:
    pass
import importlib,sys
from odoo import exceptions

class ZSRM_BAPI_MATERIAL_GET_DETAIL():

    def BAPI_ZSRM_BAPI_MATERIAL_GET_DETAIL(self,cr,IV_BEGIN,IV_END,MATNR,IV_QC):
        conn=""
        try:
            getconn = get_pyrfc_conn.get_pyrfc_conntion()
            conn = getconn.get_conn(cr)
            result = ""
            if len(MATNR)>0:
                result = conn.call('ZSRM_BAPI_MATERIAL_GET_DETAIL',IT_MATNR=MATNR,IV_QC=IV_QC)
                return result
            if not IV_BEGIN==" " and not IV_END==" ":
                result = conn.call('ZSRM_BAPI_MATERIAL_GET_DETAIL',IV_BEGIN=IV_BEGIN, IV_END=IV_END,IV_QC=IV_QC)
                return result
        except BaseException as b:
            raise  exceptions.ValidationError(b)
            pass
        finally:
            if conn:
                conn.close()
