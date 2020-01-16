#!/usr/bin/python
# -*- coding: UTF-8 -*-
try:
    from odoo import api, fields, models,exceptions
    import pyrfc
except BaseException as b:
    print(b)
    #pass
class get_pyrfc_conntion():


    def get_conn(self,cr):
        try:
            sql="SELECT t.service_name,t.user,t.passwd FROM srm_pyrfc_config t where enabled='t' "
            cr.execute(sql)
            datname=cr.fetchone()
            user = ''
            passwd = ''
            if datname[1]:
                user = datname[1]
            if datname[2]:
                passwd = datname[2]
            if datname[0]=='yuechen_prd':
                if user=='':
                    user = 'ddic'
                    passwd = 'yc123456'
                conn = pyrfc.Connection(user=user,
                                        passwd=passwd,
                                        ashost='192.168.1.253',
                                        sysnr='00',
                                        client='800',
                                        saprouter='/H/116.6.193.100/H/',
                                        lang='zh')
            elif datname[0]=='yuechen_dev':
                if user=='':
                    user = 'ddic_kf'
                    passwd = '123456'
                conn = pyrfc.Connection(user=user,
                                    passwd=passwd,
                                    ashost='192.168.1.186',
                                    sysnr='00',
                                    client='800',
                                    saprouter='/H/116.6.193.100/H/',
                                    lang='zh')
            else:
                if user=='':
                    user = 'srm_user'
                    passwd = '1234567'
                conn = pyrfc.Connection(user=user,
                                        passwd=passwd,
                                        ashost='192.168.0.56',
                                        sysnr='00',
                                        client='400',
                                        saprouter='/H/116.31.82.220/H/',
                                        lang='zh')
            #print(conn.get_connection_attributes())
            print(conn)
            return conn
        except BaseException as b:
            raise exceptions.ValidationError(" Connection SAP exception"+str(b))

        # reload(sys)
        # sys.setdefaultencoding('utf8')
        # conn = pyrfc.Connection(user=user_a,
        #                         passwd=passwd_a,
        #                         ashost=ashost_a,
        #                         sysnr='00',
        #                         client='800',
        #                         saprouter='/H/116.6.193.100/H/',
        #                         lang='zh')

