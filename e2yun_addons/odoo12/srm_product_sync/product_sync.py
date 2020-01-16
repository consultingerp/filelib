#!/usr/bin/python
# -*- coding: UTF-8 -*-
from odoo import api, fields, models, exceptions, _

try:
    from odoo.addons.srm_pyrfc import ZSRM_BAPI_MATERIAL_GET_DETAIL
except:
    pass
import datetime
import time
class srm_po_sync_task(models.Model):
    _name = "srm.product.sync"

    def srm_product_sync_task_m(self,IV_BEGIN, IV_END, MATNR, IV_QC,context=None):

        cr=self._cr
        uid=self._uid

        bapi = ZSRM_BAPI_MATERIAL_GET_DETAIL.ZSRM_BAPI_MATERIAL_GET_DETAIL()
        IV_BEGIN_TEMP = datetime.datetime.now()
        temps = IV_BEGIN_TEMP.strftime('%Y%m%d')
        tempe = IV_BEGIN_TEMP + datetime.timedelta(days=+2)
        tempe = tempe.strftime('%Y%m%d')
        if IV_BEGIN == '':
            IV_BEGIN = temps
        else:
            try:
                datetime.datetime.strptime(IV_BEGIN, '%Y%m%d')
            except:
                raise exceptions.ValidationError(IV_BEGIN + '格式不正确')

        if IV_END == '':
            IV_END = tempe
        else:
            try:
                datetime.datetime.strptime(IV_BEGIN, '%Y%m%d')
            except:
                raise exceptions.ValidationError(IV_BEGIN + '格式不正确')
        MATNR_T = []
        for matnrs in MATNR:
            matnr_m = {'MATNR': matnrs}
            MATNR_T.append(matnr_m)

        result = bapi.BAPI_ZSRM_BAPI_MATERIAL_GET_DETAIL(cr, str(IV_BEGIN), str(IV_END), MATNR_T,IV_QC)
        ET_MATERIAL_INFO=result['ET_MATERIAL_INFO']
        i=0;

        for item in ET_MATERIAL_INFO:
            vals_temp = {}
            update_id=""

            updatetime_sap=""
            if item['UDATE'] and item['UTIME']:
             updatetime_sap = time.strptime(item['UDATE'] + item['UTIME'], "%Y%m%d%H%M%S")
             updatetime_sap_str = str(updatetime_sap.tm_year) + '-' + str(updatetime_sap.tm_mon) + '-' + str(
                updatetime_sap.tm_mday) + ' ' + str(updatetime_sap.tm_hour) + ':' + str(
                updatetime_sap.tm_min) + ':' + str(updatetime_sap.tm_sec)
             vals_temp['updatetime_sap'] = updatetime_sap_str

            # 产品是否存在
            sql = " select  id,updatetime_sap from product_template t where t.default_CODE='" + str(item['MATNR']) + "'  limit 1 "
            try:
                cr.execute(sql)
                sql_result = cr.fetchone()
            except BaseException  as e:
                raise exceptions.ValidationError(e)
            if sql_result:
                update_id=sql_result[0]

                # 删除标识
                if item['LVORM']:
                   self.env['product.template'].unlink(update_id)
                   continue
                if updatetime_sap=="":
                    continue

                #初始化导入启用
                #continue
                # 如果已导入，验证是否修改过，执行修改函数
                if sql_result[1] :
                    updatetime_sap0 = time.strptime(sql_result[1].replace('-', '').replace(':', '').replace(' ', ''),
                                                    "%Y%m%d%H%M%S")
                    isUpdate = int(time.strftime("%Y%m%d%H%M%S", updatetime_sap0)) - int(
                        time.strftime("%Y%m%d%H%M%S", updatetime_sap))
                    if isUpdate == 0:
                        continue





            #产品单位
            sql = " select  id from product_uom t where t.name like'" + str(item['MEINS']) + "'  limit 1 "
            try:
                cr.execute(sql)
                sql_result = cr.fetchone()
            except BaseException  as e:
                raise exceptions.ValidationError(e)


            if sql_result:
                vals_temp['uom_id'] = sql_result[0]
                product_variant_ids = []
                product_variant_ids.append((0, False, {'uom_po_id': sql_result[0]}))
                vals_temp['product_variant_ids'] = product_variant_ids
            else:
                if IV_QC=='MENU':
                    raise exceptions.ValidationError('SAP单位未匹配到,' + str(item['PO_UNIT']))
                continue

            vals_temp['name'] =item['MAKTX']
            vals_temp['default_code'] =item['MATNR']

             #公司
            sql = " select  id from res_company t where t.name ='" + str(item['COMPANY']) + "'  limit 1 "
            try:
                cr.execute(sql)
                sql_result = cr.fetchone()
            except BaseException  as e:
                raise exceptions.ValidationError(e)

            if sql_result:
                vals_temp['company_id'] = sql_result[0]  # 公司
            else:
                if IV_QC == 'MENU':
                  raise exceptions.ValidationError('SAP公司未匹配到,' + str(item['COMPANY']))
                continue

            #产品分类
            sql = " select  id from product_category t where t.name ='" + str(item['CATEG_ID']) + "'  limit 1 "
            try:
                cr.execute(sql)
                sql_result = cr.fetchone()
            except BaseException  as e:
                raise exceptions.ValidationError(e)

            if sql_result:
              vals_temp['categ_id'] = sql_result[0]  #分类
            else:
              vals_temp['categ_id'] = 2  # 分类
            #供应商
            seller_ids=[]
            ET_SUPPLIER_INFO=result['ET_SUPPLIER_INFO']
            for supplier in ET_SUPPLIER_INFO:
                seller_idm = {}
                if not supplier['MATNR']==item['MATNR'] or not supplier['NAME1']:
                    continue
                sql = " select  id from res_partner t where t.name='" + str(
                    supplier['NAME1']) + "' and t.supplier='True' "
                try:
                    cr.execute(sql)
                    sql_result = cr.fetchone()
                except BaseException  as e:
                    raise exceptions.ValidationError(e)

                if sql_result:
                   seller_idm['name'] = sql_result[0]
                else:
                    if IV_QC == 'MENU':
                        raise exceptions.ValidationError('供应商未匹配,' + str(supplier['NAME1']))
                    if supplier['LOEKZ']:
                        continue
                    continue
                if supplier['AUTO_PO']:
                   seller_idm['automatic_selection']=True
                else:
                   seller_idm['automatic_selection'] = False

                if supplier['DELIVERY_OVERDUE']:
                   seller_idm['delivery_overdue_days'] = int(supplier['DELIVERY_OVERDUE'])
                else:
                   seller_idm['delivery_overdue_days']=0

                if supplier['THE_QUOTA']:
                    seller_idm['the_quota'] = int(supplier['THE_QUOTA'])
                else:
                    seller_idm['the_quota'] = 0

                if supplier['TIME_TOLERANCE']:

                    seller_idm['time_tolerance'] = int(supplier['TIME_TOLERANCE'])
                else:
                    seller_idm['time_tolerance'] = 0

                if supplier['MIN_PACK']:
                    seller_idm['min_pack'] = int(supplier['MIN_PACK'])
                else:
                    seller_idm['min_pack'] = 0

                if supplier['MIN_QTY']:
                    seller_idm['min_qty'] = int(supplier['MIN_QTY'])
                else:
                    seller_idm['min_qty'] = 0

                if supplier['LEAD_TIME']:
                    seller_idm['delay'] = int(supplier['LEAD_TIME'])
                else:
                    seller_idm['delay'] = 0

                if update_id=="":
                    if not supplier['LOEKZ']:
                        seller_ids.append((0, False, seller_idm))
                else:

                    sql="select ID from product_supplierinfo where product_tmpl_id='"+str(update_id)+"' and name='"+str(seller_idm['name'])+"' ORDER BY ID DESC LIMIT 1"
                    try:
                        cr.execute(sql)
                        sql_result = cr.fetchone()
                    except BaseException  as e:
                        raise exceptions.ValidationError(e)

                    if sql_result:
                        if supplier['LOEKZ']:
                            seller_ids.append((2, sql_result[0], False))
                        else:
                            seller_ids.append((1, sql_result[0], seller_idm))
                    else:
                        if not supplier['LOEKZ']:
                            seller_ids.append((0, False, seller_idm))

            vals_temp['seller_ids']=seller_ids
            i+=1
            time.sleep(0.05)  # 休眠0.1秒
            if update_id=="":
                if vals_temp['seller_ids']:
                   self.env['product.template'].create(vals_temp)
            else:
                #sql = "update product_template set updatetime_sap='" + str(updatetime_sap_str) + "'"
                updata_vals_temp={}
                # sql="update ir_translation  set src='"+str(vals_temp['name'])+"' where name = 'product.template,name' and res_id = '"+str(update_id)+"' and lang='zh_CN'  "
                # cr.execute(sql)
                updata_vals_temp['name'] = vals_temp['name']
                #updata_vals_temp['default_code']=vals_temp['default_code']
                updata_vals_temp['updatetime_sap'] = vals_temp['updatetime_sap']
                updata_vals_temp['seller_ids'] = vals_temp['seller_ids']
                self.env['product.template'].write(update_id, updata_vals_temp)
            if i>=2000:
                break




class srm_product_template(models.Model):
    _inherit = 'product.template'
    updatetime_sap = fields.Datetime(string='updatetime_sap')  # SAP更新时间
