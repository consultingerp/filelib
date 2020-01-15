# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
import datetime


class srm_scheduling(models.Model):
    _name = 'srm.scheduling'
    _inherit = 'mat.demand.line'
    _inherit = 'mat.demand.head'

    @api.model
    def intitle_data(self,size,page,supplier,werks,query_xqrq_e,matnr):
        result = {}
        msg=""
        version=""
        revisions_edit_flag=0
        is_supplier=self.env['res.users']._get_default_supplier()
        result['is_supplier']=is_supplier
        sql_max_versi="select  max(versi) as version  from mat_demand_head where 1=1 and state='publish' and history_data='f' "
        self._cr.execute(sql_max_versi)
        max_versi =self._cr.fetchone()
        if max_versi and max_versi[0]:
            version = max_versi[0]
        else:
            msg = "请检查数据是否正确"
            result['msg'] = msg
            result['count'] = 0
            return result

        if matnr:
            matnr = matnr.strip()
            sql="select id  from  product_product where default_code='"+str(matnr)+"'"
            self._cr.execute(sql)
            result_temp=self._cr.fetchone();
            if result_temp:
                matnr=result_temp[0]
            else:
                matnr="00"
                msg = "请输入正确的物料号"
        if supplier:
            sql = "select id  from res_partner where supplier_code='"+str(supplier)+"'"
            self._cr.execute(sql)
            result_temp = self._cr.fetchone();
            if result_temp:
                supplier = result_temp[0]
            else:
                supplier = "00"
                msg = "请输入正确的供应商代码"

        if werks:
            werks=werks.strip()
            sql = "select id  from stock_warehouse where factory_code='" + str(werks) + "'"
            self._cr.execute(sql)
            result_temp = self._cr.fetchone();
            if result_temp:
                werks = result_temp[0]
            else:
                werks = "00"
                msg = "请输入正确的工厂代码"

        result['title'] = ['供应商', '物料号', '期初需求', '  ', '未清PO', '总需求']
        count=0
        now = datetime.datetime.now()
        today_where = now.strftime('%Y-%m-%d')
        init_list_requirement=[]  #表格抬头数据
        init_list_requirement_map = {} #表格标题数据
        initial_requirement_map = {}  # 期初需求

        while (count < 62):
            delta = datetime.timedelta(days=count)
            n_days = now + delta;
            today = n_days.strftime('%Y-%m-%d')
            if query_xqrq_e:
                if query_xqrq_e<today:
                    break
            today_temp = n_days.strftime('%m-%d')
            result['title'].append(today)
            init_list_requirement.append(today);
            week=""
            weekday=n_days.weekday()+1
            if weekday==0:
                week="周天"
            elif  weekday==1:
                week = "周一"
            elif weekday== 2:
                week = "周二"
            elif  weekday == 3:
                week = "周三"
            elif  weekday == 4:
                week = "周四"
            elif  weekday== 5:
                week = "周五"
            elif  weekday == 6:
                week = "周六"
            else :
                week = "周天"
            init_list_requirement_map[today]={'week':week,'date':today_temp}
            count = count + 1

        s_c_schedule_map = {}  # 供应商排程确认数量


        #获取总数量
        sql_count=self.get_sqlcount(version,is_supplier,query_xqrq_e,supplier,werks,matnr)
        self._cr.execute(sql_count)
        count_sql = self._cr.fetchone()
        result['count'] = count_sql[0]

        #获取数据KEY列表
        sql_key=self.get_sqlkey(version,is_supplier,size,page,query_xqrq_e,supplier,werks,matnr)
        self._cr.execute(sql_key)
        list_key_sql = self._cr.dictfetchall()

        #获取VALUE数据列表
        sql=self.get_sql(version,is_supplier,today_where,query_xqrq_e,supplier,werks,matnr)
        self._cr.execute(sql)
        list_value_sql = self._cr.dictfetchall()
        list_data=[]
        qcxqsl = 0
        ysqcxqsl = 0
        for data in list_key_sql:
            if data['matnr']:
                qcxqsl = 0
                ysqcxqsl = 0
                total_requirement = 0
                jhd_sum = 0
                qrs_sum = 0
            else:
                msg = "请检查数据是否正确"
                result['msg']=msg
                result['count'] =0
                return result
            map_data={}
            list_requirement_line = {};
            s_c_schedule_maps={}
            for r_line in init_list_requirement:
                list_requirement_line[r_line]={}  #初始化30天的数据
                s_c_schedule_maps[r_line] = {}

            map_data['supplier']=data['supplier_code']
            map_data['supplier_name'] = data['supplier']
            map_data['matnr'] = data['matnr']
            map_data['versi'] = data['versi']
            map_data['lifnr'] = data['lifnr']
            map_data['matnr_a'] = data['matnr_a']
            map_data['matnrdesc'] = data['matnr_name_a']
            map_data['the_quota'] = data['the_quota']
            map_data['min_qty'] = data['min_qty']
            map_data['time_tolerance'] = data['time_tolerance']
            map_data['schedule_confirm'] = data['schedule_confirm']  #是否需要确认排程




            # 期初需求
            qcxq_sql = "select sum(menge) as menge from mat_demand_line  where  matnr=%s and lifnr=%s and ddate<%s and mat_demand_id="+str(data['id'])+" and state!='delete'  "
            self._cr.execute(qcxq_sql, (data['matnr'],data['lifnr'],  today_where))
            qcxq_menge = self._cr.fetchone()
            if qcxq_menge[0]:
                qcxqsl = qcxq_menge[0]
                ysqcxqsl=qcxq_menge[0]
            delivery_overdue_days=0
            if data['delivery_overdue_days']:
                delivery_overdue_days=data['delivery_overdue_days']



            # 未失效交货单
            wslxjhd_sql = " select sum(t1.dnmng) as admng  from ("
            wslxjhd_sql += " select to_char(datoo ::timestamp + '" + str(
                delivery_overdue_days) + "day', 'yyyy-mm-dd') as datoo ,dnmng "
            wslxjhd_sql += "from delivery_order h "
            wslxjhd_sql += "inner join delivery_order_line l "
            wslxjhd_sql += " on h.id = l.delivery_order_id "
            wslxjhd_sql += " where h.comco = %s "
            wslxjhd_sql += " and h.werks = %s  "
            wslxjhd_sql += " and h.lifnr = %s  "
            wslxjhd_sql += " and l.matnr = %s  "
            wslxjhd_sql += " and h.state not in ('supplier_cancel') "
            wslxjhd_sql += " and to_number(datoo,'9999999999999999999') <to_number('" + str(
                today_where) + "', '9999999999999999999')"
            wslxjhd_sql += " and l.version_id = %s "



            wslxjhd_sql += " ) t1 where 1=1 "

            if delivery_overdue_days > 0:
                wslxjhd_sql += "and to_number(t1.datoo, '9999999999999999999')>=to_number('" + str(today_where) + "', '9999999999999999999') "

            #, today_where
            self._cr.execute(wslxjhd_sql, (
                data['comco'], data['werks'], data['lifnr'], data['matnr'],data['id']))
            wsxjhd = self._cr.fetchone()
            if wsxjhd[0]:
                qcxqsl = qcxqsl - wsxjhd[0]  # 期初需求减去失效范围内的交货数
                ysqcxqsl = ysqcxqsl - wsxjhd[0]




            #未清PO
            # po_sql= "select sum(p1.product_qty) as unclean_po,p.name  "
            # po_sql += "from purchase_order p "
            # po_sql += "left join purchase_order_line p1  "
            # po_sql += "on p1.order_id = p.id  "
            # po_sql += "where p.partner_id = "+str(data['lifnr'])+"  "
            # po_sql += "and p.state = 'supply_confirm'  "
            # po_sql += "and p1.product_id ="+str(data['matnr'])+""
            # po_sql +=" group by p.name "
            # self._cr.execute(po_sql)
            # value_po = self._cr.fetchall()
            # map_data['unclean_po'] = ""
            # if value_po:
            #  value_po_str=""
            #  valuepo_temp=0
            #  for po_value in value_po:
            #      if po_value[1]:
            #          if value_po_str == "":
            #              value_po_str = "'" + po_value[1] + "'"
            #          else:
            #              value_po_str = value_po_str + ",'" + po_value[1] + "'"
            #      if po_value[0]:
            #          valuepo_temp = valuepo_temp + po_value[0];
            #  yshs=self.get_ysh(value_po_str,data['matnr'],data['werks'])
            #  if yshs["0"]>0: #0-收货数 1-退货数
            #        map_data['unclean_po'] =(valuepo_temp - yshs["0"])+yshs["1"] #未清PO
            #        if yshs["1"]>0:  #退货
            #          map_data['yjhsl'] = yshs["0"]-yshs["1"]   #已收货数量 收货数-退货数就是=收货数
            #          qcxqsl=qcxqsl-map_data['yjhsl']
            #          ysqcxqsl=ysqcxqsl-map_data['yjhsl']
            #        else:
            #          map_data['yjhsl'] = yshs["0"]
            #  else:
            #      map_data['unclean_po']=valuepo_temp;
            # else:
            #  map_data['unclean_po']=""

            #未清PO
            po_sql= " select SUM (p1.product_qty) - SUM (p1.delivery_qty) AS unclean_po  "
            po_sql += "from purchase_order p "
            po_sql += "left join purchase_order_line p1  "
            po_sql += "on p1.order_id = p.id  "
            po_sql += "where p.partner_id = "+str(data['lifnr'])+"  "
            po_sql += "and p.state = 'supply_confirm'  "
            po_sql += "and p1.product_id ="+str(data['matnr'])+""
            self._cr.execute(po_sql)
            value_po = self._cr.fetchone()
            if value_po and value_po[0]:
                map_data['unclean_po'] =value_po[0]
            else:
                map_data['unclean_po'] = ""

            if qcxqsl==0:
                qcxqsl=0
                ysqcxqsl=0
            data_key=str(data['versi'])+str(data['lifnr'])+str(data['matnr']);
            initial_requirement_map[data_key]={}
            if ysqcxqsl>0:
               initial_requirement_map[data_key]['total_requirement']=ysqcxqsl


            #时间容差
            # sjrcday = []
            # if data['time_tolerance']:
            #     dvdate = datetime.datetime.strptime(data_value['ddate'], '%Y-%m-%d')
            #     d = 0
            #     while d < int(data['time_tolerance']):  # 时间容差
            #         d = d + 1
            #         delta = datetime.timedelta(days=d)
            #         n_days = dvdate + delta;
            #         sjrcday.append(n_days.strftime('%Y-%m-%d'))
            # map_data['sjrcday'] = sjrcday
            #初始化第一天的数据，期初数量大于0的情况初始
            for data_value in list_value_sql:
                  data_value_key = str(data_value['versi']) + str(data_value['lifnr']) + str(data_value['matnr'])
                  if (data_key==data_value_key):
                      map_data_value={}

                      #记录当天已排程数量，用于计算不能超过总需求+期初需求+数量容差+最小包装量
                      s_c_schedule_maps[data_value['ddate']] = {'bmeng': data_value['bmeng'],
                                                                'menge': data_value['menge']}
                      bmeng_temp=0
                      menge_temp=0
                      if data_value['bmeng']:
                          bmeng_temp=data_value['bmeng']
                          menge_temp=data_value['menge']


                      if qcxqsl>0:
                         qcxqsl=qcxqsl-(bmeng_temp-menge_temp)
                      map_data_value['ddate']=data_value['ddate']
                      map_data_value['versi'] = data_value['versi']
                      map_data_value['lifnr'] = data_value['lifnr']
                      map_data_value['menge']=data_value['menge']

                      total_requirement=total_requirement+int(data_value['menge'])

                      map_data_value['bmeng'] =data_value['bmeng']
                      if data_value['bmeng']:
                        qrs_sum = qrs_sum+int(data_value['bmeng'])

                      map_data_value['memo'] =data_value['memo']
                      map_data_value['delivery_overdue_days'] = data['delivery_overdue_days']
                      map_data_value['the_quota'] = data['the_quota']

                      map_data_value['min_qty'] = data['min_qty']
                      if data_value['line_state']=='not_confirm':
                          map_data_value['line_state']="无需确认"
                      elif (data_value['line_state']=='supplier_confirm') :
                          map_data_value['line_state'] = "供应商确认"
                      elif  (data_value['line_state']=='supplier_edit') :
                          map_data_value['line_state'] = "供应商修改"
                      elif data_value['line_state'] == 'purchase_confirm':
                          map_data_value['line_state'] = "采购员确认"
                      else:
                          map_data_value['line_state'] = "业务新建"



                      #已建交货单数量
                      delivery_sql = "select sum(dnmng) as admng,sum(aomng) as aomng  from delivery_order h inner join delivery_order_line l "
                      delivery_sql += " on h.id = l.delivery_order_id "
                      delivery_sql += " where h.comco = %s and h.werks = %s and h.lifnr = %s and l.matnr = %s"
                      delivery_sql += " and h.datoo = %s and h.state not in ('supplier_cancel') "
                      delivery_sql += " and l.version_id = %s "
                      self._cr.execute(delivery_sql, (data_value['comco'], data_value['werks'], data_value['lifnr'], data_value['matnr'], data_value['ddate'], data['id']))
                      delivery_dnmng = self._cr.fetchone()
                      if delivery_dnmng[0]:
                          map_data_value['jhtsl']  = delivery_dnmng[0]
                          jhd_sum = jhd_sum+int(delivery_dnmng[0])
                      else:
                          map_data_value['jhtsl'] =""

                      if delivery_dnmng[1]:
                          map_data_value['yjhsl'] = delivery_dnmng[1]
                      else:
                          map_data_value['yjhsl'] =""

                      list_requirement_line[map_data_value['ddate']]=map_data_value

            initial_requirement_map[data_key]['qcxqsl'] =qcxqsl; # 原始期初需求， #计算当前排程考虑的期初需求后剩余的期初需求
            initial_requirement_map[data_key]['ysqcxqsl'] = ysqcxqsl;
            map_data['min_qty_jsh'] = 0

            the_quota=0;
            #不考虑数量容差
            # if data['the_quota']:
            #     the_quota=data['the_quota']

            total_requirement_sum=ysqcxqsl+total_requirement+the_quota
            if (total_requirement>0 or ysqcxqsl>0) :
                #差多少满足最小包装数--按天算
                if  data['min_qty']:
                    b = total_requirement_sum
                    a = data['min_qty']
                    i_temp = 1
                    while (a *i_temp)< b:
                        i_temp = i_temp + 1
                    a = a * i_temp
                    total_requirement_sum=total_requirement_sum+(a-b)
                #initial_requirement_map[data_key]['total_requirement']=ysqcxqsl+int(map_data['total_requirement'])   #期初需求+总需求数+数量容差+最小包装

            map_data['total_requirement_sum'] = total_requirement_sum  #期初需求+总需求数+数量容差+最小包装
            if total_requirement<=0:
                map_data['total_requirement'] = ""
            else:
                map_data['total_requirement'] = total_requirement

            map_data['requirement_line'] = list_requirement_line;   #行数据列表
            map_data['initial_requirement'] = ysqcxqsl  # 期初需求
            if jhd_sum>0:
                map_data['jhd_sum'] = jhd_sum  # 交货单
            else:
                map_data['jhd_sum'] = ""
            if qrs_sum > 0:
                map_data['qrs_sum'] = qrs_sum  # 确认数
            else:
                map_data['qrs_sum'] = ""



            s_c_schedule_map[data_key]=s_c_schedule_maps
            list_data.append(map_data)
        result['data'] = list_data #数据
        if not list_data:
            result['count'] = 0
        result['version'] = version #版本
        result['title_map']=init_list_requirement_map #表格标题动态MAP
        result['s_c_schedule'] = s_c_schedule_map  # 供应商确认排程数，用于前端计算
        result['initial_requirement']=initial_requirement_map  #期初需求
        result['revisions_edit_flag']=revisions_edit_flag  #验证是否历史版本，历史版本：0，不能编辑
        result['msg'] = msg  # 返回消息
        return result

    #更新排产确认数量
    @api.model
    def update_bmeng(self, versi,lifnr,ddate,matnr,bmeng,state,is_h_hu_l):
        delivery=False
        if is_h_hu_l==2:
            delivery=True
        if state=="supplier_edit":
            delivery = False
        #汇总行项目回写
        sql =" UPDATE mat_demand_line t2 "
        sql += "SET bmeng = "+str(bmeng)+",state='"+str(state)+"' "
        sql += ",delivery ='"+str(delivery)+"'"
        sql +=" FROM (SELECT id, versi FROM mat_demand_head) t1 "
        sql += " WHERE t2.mat_demand_id = t1.id "
        sql += " and t1.versi  = '"+str(versi)+"'"
        sql += " and t2.lifnr = '"+str(lifnr)+"' "
        sql += " and t2.ddate = '"+str(ddate)+"' "
        sql += " and t2.matnr = '"+str(matnr)+"'"
        #采购员已确认，或者等于绿色 delivery=True
        try:
         self._cr.execute(sql)
         #行项目明细回写方案
         sql="select prnum,menge,t2.id  from mat_demand_line_details t2 LEFT JOIN mat_demand_head t1 on t2.mat_demand_id = t1.id "
         sql += " WHERE 1=1 "
         sql += " and t1.versi  = '" + str(versi) + "'"
         sql += " and t2.lifnr = '" + str(lifnr) + "' "
         sql += " and t2.ddate = '" + str(ddate) + "' "
         sql += " and t2.matnr = '" + str(matnr) + "'"
         sql += " and t2.publish = 't'"
         sql += " ORDER BY t2.prnum asc "
         self._cr.execute(sql)
         prnums=self._cr.fetchall()
         bmeng=float(bmeng)
         if prnums:
             i=0
             size=len(prnums)
             for prnum in prnums:
                 i=i+1
                 bmeng_temp=0;
                 if bmeng>float(prnum[1]):
                     bmeng_temp=prnum[1]
                     if i==size:
                         bmeng_temp = bmeng
                     else:
                         bmeng=bmeng-bmeng_temp
                 else:
                     bmeng_temp=bmeng
                     bmeng=0
                 sql = " UPDATE mat_demand_line_details t2 "
                 sql += "SET bmeng = " + str(bmeng_temp) + ",state='" + str(state) + "' "
                 sql += ",delivery ='" + str(delivery) + "'"
                 sql += " WHERE t2.id = " + str(prnum[2]) + " "
                 self._cr.execute(sql)



        except RuntimeWarning:
            return 0
        else:
            return 1




     # 新增排程数据
    @api.model
    def add_demand(self, versi, lifnr, ddate, matnr, bmeng, state,is_h_hu_l):

            delivery = False
            if is_h_hu_l == 2:
                delivery = 'True'
            if state == "supplier_edit":
                delivery ='False'
            sql=""
            sql += " select t2.create_uid, "
            sql += " matnr,meins,ekgrp, lifnr, mat_demand_id,t2.write_uid  "
            sql += " from mat_demand_line t2  "
            sql += " left join mat_demand_head t1  "
            sql += " on t2.mat_demand_id = t1.id "
            sql += " where  t1.versi = '" + str(versi) + "'"
            sql += " and t2.lifnr = '" + str(lifnr) + "' "
            sql += " and matnr = '" + str(matnr) + "'"
            sql += " limit 1  "
            self._cr.execute(sql)
            inser_value = self._cr.fetchone()

            sql="select nextval('mat_demand_line_id_seq') as id "
            self._cr.execute(sql)
            maxid = self._cr.fetchone()
            id=0;
            if maxid:
                id=maxid[0]

            #
            # sql = " UPDATE mat_demand_line t2 "
            #
            # sql += "SET bmeng = " + str(bmeng) + ",state='" + str(state) + "' "
            # sql += " FROM (SELECT id, versi FROM mat_demand_head) t1 "
            # sql += " WHERE t2.mat_demand_id = t1.id "
            # sql += " and t1.versi = '" + str(versi) + "'"
            # sql += " and t2.lifnr = '" + str(lifnr) + "' "
            # sql += " and t2.ddate = '" + str(ddate) + "' "
            # sql += " and matnr = '" + str(matnr) + "'"

            # ddate_temp = datetime.datetime.strptime(ddate, "%Y%m%d")
            # ddate=ddate_temp.strftime('%Y-%m-%d')
            try:

                sql = "insert into mat_demand_line(id,create_uid,matnr,bmeng,meins,ekgrp,lifnr,state,mat_demand_id,write_uid,menge,ddate,delivery) values "
                sql += "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                self._cr.execute(sql,(id, inser_value[0],
                                    inser_value[1],bmeng, inser_value[2],
                                    inser_value[3],inser_value[4],state,inser_value[5],inser_value[6],0,ddate,delivery) )

                sql = "select nextval('mat_demand_line_details_id_seq') as id "
                self._cr.execute(sql)
                maxid = self._cr.fetchone()
                id = 0;
                if maxid:
                    id = maxid[0]
                sql = "insert into mat_demand_line_details   (id,create_uid,matnr,bmeng,meins,ekgrp,lifnr,state,mat_demand_id,write_uid,menge,ddate,delivery) values "
                sql += "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                self._cr.execute(sql, (id, inser_value[0],
                                          inser_value[1], bmeng, inser_value[2],
                                      inser_value[3], inser_value[4], state, inser_value[5], inser_value[6], 0, ddate,
                                      delivery))


            except RuntimeWarning:
                return 0
            else:
                return 1


    @api.model
    def get_ysh(self,origin,product_id,werks):
         sql ="  SELECT "
         sql += " sum(product_uom_qty) as product_uom_qty  FROM  	stock_move t1 LEFT JOIN stock_picking_type t2 ON t1.picking_type_id = t2. ID "
         sql += " WHERE t1.origin in ("+str(origin)+")  AND t1.product_id ='"+str(product_id)+"'  "
         sql += "  and state ='done' AND t2.code='incoming'  and t2.warehouse_id='"+str(werks)+"' "
         self._cr.execute(sql)
         ysh = self._cr.fetchone()
         result={"0":0,"1":0}
         if ysh[0]:
             result["0"]=float(ysh[0])
             sql = "  SELECT "
             sql += " sum(product_uom_qty) as product_uom_qty  FROM  	stock_move t1 "
             sql += " WHERE t1.origin in ("+str(origin)+")   AND t1.product_id ='" + str(product_id) + "'  "
             sql += "  and state ='done' AND T1.origin_returned_move_id is not null and t1.warehouse_id='" + str(werks) + "' "
             self._cr.execute(sql)
             yth = self._cr.fetchone()
             if yth[0]:
                 result["1"]=float(yth[0])
         return result


    def get_sqlcount(self, version, is_supplier,query_xqrq_e,supplier,werks,matnr):
        sql_count = " select count(1) as c from ( select t2.matnr "
        sql_count += " from mat_demand_head  t1 "
        sql_count += " left join mat_demand_line t2 "
        sql_count += " on t2.mat_demand_id = t1.id "
        sql_count += " where 1 = 1 "
        sql_count += " and t1.state='publish'"
        if version:
            sql_count += "and t1.versi ='" + str(version) + "'"

        if is_supplier != 0:
            sql_count += " and t2.lifnr =" + str(is_supplier) + " "

        if supplier:
            sql_count += " and t2.lifnr ='" + str(supplier) + "' "

        if werks:
            sql_count += " and t1.werks ='" + str(werks) + "' "

        if matnr:
            sql_count += " and t2.matnr ='" + str(matnr) + "' "

        if query_xqrq_e:
            sql_count += " and t2.ddate<='" + str(query_xqrq_e) + "' ";

        sql_count += " group by t2.lifnr, "
        sql_count += " t2.matnr, "
        sql_count += " t1.versi "
        sql_count += " order by t2.matnr ) t3 "
        return sql_count

    def get_sqlkey(self,version,is_supplier,size,page,query_xqrq_e,supplier,werks,matnr):
        sql_key = " select t1.id,t1.werks,t1.versi,t2.lifnr, t2.matnr, "
        sql_key += "t3.name as supplier,"
        sql_key += "t3.supplier_code,t3.schedule_confirm, "
        sql_key += " t5.delivery_overdue_days, "
        sql_key += " t5.time_tolerance, "
        sql_key += "t5.number_tolerance as the_quota, "   #数量容差
        sql_key += "t5.min_pack as min_qty, "
        sql_key += "t1.comco, "
        sql_key += " t4.default_code as matnr_a ,"
        sql_key += " t6.name  as matnr_name_a "
        sql_key += "  from mat_demand_head t1 "
        sql_key += " left join mat_demand_line t2 "
        sql_key += " on t2.mat_demand_id = t1.id "
        sql_key += " left join res_partner t3 on t3.id=t2.lifnr "
        sql_key += " left join product_product t4 on t4.id=t2.matnr "
        sql_key += " LEFT JOIN product_supplierinfo t5 ON t5. NAME = t2.lifnr AND t5.product_tmpl_id = t4.product_tmpl_id"
        sql_key += " LEFT JOIN product_template t6 ON t6.id = t4.product_tmpl_id "
        sql_key += " where 1=1  "
        sql_key += " and t1.state='publish'"
        sql_key += " and t2.publish='t'"
        if version:
            sql_key += "and t1.versi ='" + str(version) + "'"
        if is_supplier != 0:
            sql_key += " and t2.lifnr =" + str(is_supplier) + " "
        if supplier:
            sql_key += "and t2.lifnr ='" + str(supplier) + "'"
        if werks:
            sql_key += "and t1.werks ='" + str(werks) + "'"
        if matnr:
            sql_key += "and t2.matnr ='" + str(matnr) + "'"

        if query_xqrq_e:
            sql_key += " and t2.ddate<='" + str(query_xqrq_e) + "' ";

        sql_key += " group by t1.werks,t1.id,t2.lifnr,t2.matnr,t1.versi,t1.state,t3.supplier_code ," \
                   " t3.name,t4.default_code,t5.time_tolerance,t6.name,t5.delivery_overdue_days,t5.min_pack," \
                   " t5.number_tolerance,t3.schedule_confirm ,t1.comco  "
        sql_key += " ORDER BY t3.supplier_code,t4.default_code "
        sql_key += "limit " + str(size) + " OFFSET " + str(page * size) + ""
        return sql_key

    def get_sql(self,version,is_supplier,today_where,query_xqrq_e,supplier,werks,matnr):
         sql = "select t1.id,t2.matnr ,t2.lifnr, "
         sql += "t1.versi,"
         sql += "t1.state,"
         # sql += "t5.delivery_overdue_days, "
         #  sql += "t5.time_tolerance, "
         #  sql += "t5.the_quota, "
         #  sql += "t5.min_qty, "
         sql += "t2.memo, "
         sql += "t2.ddate,"
         sql += "t2.bmeng, "
         sql += "t2.state as line_state, "
         #sql += "t2.calculate_initial_flag, "
         sql += "t1.werks, "
         sql += "t1.comco, "
         sql += "t2.menge "
         sql += "from mat_demand_head t1 "
         sql += "left join mat_demand_line t2 "
         sql += "on t2.mat_demand_id = t1.id "
         #   sql += "left join product_supplierinfo t5 "
         #  sql += " on t5.name = t2.lifnr "
         #  sql += " and t5.product_id = t2.matnr "
         sql += "where 1=1"
         sql += " and t1.state='publish'"
         sql += " and t2.ddate>='" + today_where + "'"
         sql += " and t2.state<>'delete'"
         sql += " and t2.publish='t'"
         if version:
             sql += "and t1.versi ='" + str(version) + "'"

         if is_supplier != 0:
             sql += " and t2.lifnr =" + str(is_supplier) + " "

         if supplier:
             sql += "and t2.lifnr ='" + str(supplier) + "'"

         if werks:
             sql += "and t1.werks ='" + str(werks) + "'"

         if matnr:
             sql += "and t2.matnr ='" + str(matnr) + "'"

         if query_xqrq_e :
             sql +=" and t2.ddate<='"+str(query_xqrq_e)+"' ";

         return sql

    #更是需求数是否有效标识
    @api.model
    def update_calculate_initial_flag(self, value):
        #spillover_scheduling 溢出可排程数
        sql = " UPDATE mat_demand_line t2 "
        sql += "SET calculate_initial_flag =%s "
       # sql += ",spillover_scheduling =%s "
        sql += " FROM (SELECT id, versi FROM mat_demand_head) t1 "
        sql += " WHERE t2.mat_demand_id = t1.id "
        sql += " and t1.versi = %s "
        sql += " and t2.lifnr = %s "
        sql += " and t2.ddate = %s "
        sql += " and t2.matnr = %s "

        try:
            if value:
                for v in value:
                    if v:
                        self._cr.execute(sql, (v['flag'],v['versi'],v['lifnr'],v['ddate'],v['matnr']))
        except RuntimeWarning:
            return 0
        else:
            return 1