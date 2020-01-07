#!/usr/bin/python
# -*- coding: UTF-8 -*-
try:
    from odoo import api, fields, models,exceptions
    import pyrfc
    import platform
    import configparser
    import os, sys
except BaseException as b:
    print(b)
    pass
class get_pyrfc_conntion():

    def path(self):
        platform_ = platform.system()
        if platform_ == "Windows":
            wb_path = "" + str(sys.path[0]) + "/filelib/e2yun_addons/odoo12/e2yun_crm_sap_customer_interface_extend/rfc/pyrfc_config.ini"
        else:
            #wb_path = "/tmp/pyrfc_config.ini"
            wb_path = "" + str(sys.path[
                                   0]) + "/filelib/e2yun_addons/odoo12/e2yun_crm_sap_customer_interface_extend/rfc/pyrfc_config.ini"
        return wb_path

    def get_conn(self):
        try:
            config = configparser.ConfigParser()
            path=self.path()
            os.path.exists('pyrfc_config.ini')
            config.read(path)
            #lists_header = config.sections()  # 配置组名
            #print(lists_header)
            conn = pyrfc.Connection(user=config['pyrfc_conf']['user'],
                                                    passwd=config['pyrfc_conf']['passwd'],
                                                    ashost=config['pyrfc_conf']['ashost'],
                                                    sysnr=config['pyrfc_conf']['sysnr'],
                                                    client=config['pyrfc_conf']['client'],
                                                    saprouter=config['pyrfc_conf']['saprouter'],
                                                    lang='zh')

            print(conn)
            return conn
        except BaseException as b:
            raise exceptions.ValidationError(" Connection SAP exception"+str(b))

# import configparser
# config = configparser.ConfigParser()
# config.read('pyrfc_config.ini')
# conn = pyrfc.Connection(user=config['pyrfc_conf']['user'],
#                                                     passwd=config['pyrfc_conf']['passwd'],
#                                                     ashost=config['pyrfc_conf']['ashost'],
#                                                     sysnr=config['pyrfc_conf']['sysnr'],
#                                                     client=config['pyrfc_conf']['client'],
#                                                     saprouter=config['pyrfc_conf']['saprouter'],
#                                                     lang='zh')
# print(conn)
# conn.close()
#
# I_INPUT={}
# I_INPUT['ZTYPE']='1'
# I_INPUT['KTOKD']='C001'
# I_INPUT['KUNNR']='200682'
# I_INPUT['NAME_ORG1']='接口测试名称修改'
# I_INPUT['BU_SORT1']='789'
# I_INPUT['BU_SORT2']='55566'
# I_INPUT['REMARK']='接口测试修改'
# I_INPUT['LANGU']='zh'
# I_INPUT['COUNTRY']='CN'
#
# # I_INPUT['POST_CODE1']=0
# # I_INPUT['POST_CODE1']=0
#
# result = conn.call('ZCL_REST_CUSTOMER', I_INPUT=I_INPUT)
# print(result)
#
# conn.close()