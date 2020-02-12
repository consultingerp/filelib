# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
from datetime import datetime

class mat_demand_head(models.Model):
    _name = "mat.demand.head"
    _table = 'mat_demand_head'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "物料需求"
    _order = 'id desc '

    STATE_SELECTION = [
        ('create', 'Create'),
        ('publish', 'Publish'),
        ('edit_publish', 'Edit Publish')
    ]

    versi = fields.Char('Version', required=False, states={
        'create': [('readonly', True)],
        'publish': [('readonly', True)],
        'edit_publish': [('readonly', True)]
    })
    name = fields.Char('Name')
    comco = fields.Many2one('res.company', 'Company', required=True,
                            readonly=True,default=lambda self: self.env['res.company']._company_default_get('mat.demand.head'))
    werks = fields.Many2one('stock.warehouse', 'Factory', required=True,states={
        'create': [('readonly', True)],
        'publish': [('readonly', True)],
        'edit_publish': [('readonly', True)]
    })
    state = fields.Selection(STATE_SELECTION, 'Status',track_visibility='onchange',defaults='publish')
    history_data = fields.Boolean('History',default=False)
    flag = fields.Char('Business Flag')
    validator = fields.Many2one('res.users', 'Validated by', readonly=True, copy=False)
    mat_demand_line_details = fields.One2many('mat.demand.line.details', 'mat_demand_id','Mat Demand Line Details', copy=True)
    mat_demand_line = fields.One2many('mat.demand.line', 'mat_demand_id', 'Mat Demand Line', copy=True)
    send_lifnr = fields.Many2one('res.partner', 'Send Mail Supplier',readonly=True)
    mail_type = fields.Char('Mail Type')

    @api.model
    def create(self,vals):
        #cr, uid,
        cr=self._cr
        uid=self._uid
        vals['state'] = 'create'
        createversi=vals['versi']
        sql = 'select max(id) as versi from mat_demand_head'
        cr.execute(sql)
        isAdd = cr.fetchone()
        mat_id=0
        rmat_id=''
        if isAdd[0]:
            mat_id=isAdd[0]
            #更新行项目
            temp_lines = []
            for line_details in vals['mat_demand_line_details']:
                vals_temp= line_details[2]
                vals_temp['create_versi']=createversi
                vals_temp['mat_demand_id']=mat_id
                vals_temp['ddate']=self.env['mat.demand.line.details'].tranDate(vals_temp['ddate'])
                if vals_temp.get('pdate',False):
                    vals_temp['pdate'] = self.env['mat.demand.line.details'].tranDate(vals_temp['pdate'])

                sql = "select *  from mat_demand_line_details where 1=1  and  mat_demand_id=" + str(mat_id) + ""
                ids_temp=[]
                if 'needs_no' in vals_temp.keys():#需求号逻辑
                    sql+=" and needs_no='"+ str( vals_temp['needs_no']) + "'"
                    cr.execute(sql)
                    ids_temp = cr.dictfetchall()
                else:#没有需求号逻辑
                    if 'lifnr' in vals_temp.keys() and vals_temp['lifnr'] \
                            and 'matnr' in vals_temp.keys() and vals_temp['matnr'] \
                            and 'ddate' in vals_temp.keys() and vals_temp['ddate']:
                       sql += " and lifnr='" + str(vals_temp['lifnr']) + "'"
                       sql += " and ddate='" + str(vals_temp['ddate']) + "'"
                       sql += " and matnr='" + str(vals_temp['matnr']) + "'"
                       if 'prnum' in vals_temp.keys() and vals_temp['prnum']:
                         sql += " and prnum='" + str(vals_temp['prnum']) + "'"
                       cr.execute(sql)
                       ids_temp = cr.dictfetchall()

                if ids_temp:
                    if self.verify_data_update(vals_temp,ids_temp[0])==False:
                        continue
                    vals_temp['publish'] = 'f'
                    line_obj = self.env['mat.demand.line.details'].browse(ids_temp[0]['id'])
                    d = line_obj.write(vals_temp)
                    rmat_id = line_obj.mat_demand_id
                else:
                    temp_lines.append(vals_temp)
                    rmat_id = self.browse(vals_temp['mat_demand_id'])
                    # d = self.env['mat.demand.line.details'].create(vals_temp)
            if len(temp_lines) > 0:
                d = self.env['mat.demand.line.details'].create(temp_lines)
        else:
            #默认一个版本
            vals['versi']='1'
            vals['name'] = '1'
            rmat_id = super(mat_demand_head, self).create(vals)
            sql="update mat_demand_head set history_data='t' where id<>"+str(rmat_id.id)+" "
            cr.execute(sql)
            sql = "update mat_demand_head set state='publish' where id=" + str(rmat_id.id) + " "
            cr.execute(sql)

        return rmat_id

    def unlink(self):
        for id in self.ids:
            mat = self.browse(id)
            if mat.state == 'publish':
                raise exceptions.ValidationError('Publish Status not Delete')
            else:
                super(mat_demand_head, self).unlink(id)
        return True


    def verify_history_version(self,id):
        cr=self._cr
        sql="select id from mat_demand_head where history_data='t' and  id="+str(id)+""
        cr.execute(sql)
        result=cr.fetchall()
        if result:
            raise exceptions.ValidationError('You cannot change the history version')

    def verify_data_update(self,value1,value2):
        if not value1['matnr']==value2['matnr']:
            return True
        if not value1['prnum']==value2['prnum']:
            return True
        if not value1['ddate']==value2['ddate']:
            return True
        # if not value1['lifnr']==value2['lifnr']:
        #     return True
        if not value1['menge']==value2['menge']:
            return True
        return  False
    def publish_data(self,ids,lineids):
        cr=self._cr
        uid=self._uid
        lifnr_dict = {}
        for id in ids:
            #matlines = self.browse(cr, uid, id).mat_demand_line_details
            matlines = self.env['mat.demand.line.details'].search([ ('id', 'in', lineids)])
            for line_id in matlines :
              line=self.env['mat.demand.line.details'].browse(line_id.id)
              if line.lifnr.schedule_confirm == False:
                  sql = "update mat_demand_line_details set bmeng="+str(line.menge)+" ,state='"+str('not_confirm')+"' ,delivery='t'  where id="+str(line.id)+""
                  cr.execute(sql)
              inser_valss={}
              inser_valss['lifnr']=line.lifnr.id
              inser_valss['ddate'] = line.ddate
              inser_valss['matnr'] = line.matnr.id
              inser_valss['mat_demand_id'] =id
              inser_valss['state'] = line.state
              inser_valss['id'] = line.id
              self.env['mat.demand.line.details'].insert_mat_demand_line_details(inser_valss)

            for line_id in matlines :
                line=self.env['mat.demand.line.details'].browse(line_id.id)
                if line.lifnr.id not in lifnr_dict and line.lifnr.schedule_confirm != False:
                    sql = " select id from mat_demand_line_details t where t.calculate_initial_flag='f' and lifnr=" + str(
                        line.lifnr.id) + " and mat_demand_id=" + str(id) + ""
                    cr.execute(sql)
                    is_send_mail = cr.fetchone()
                    if is_send_mail:
                       lifnr_dict[line.lifnr.id] = 1
                       self.browse(id).send_lifnr = line.lifnr.id
                       self.browse(id).validator = uid
                       self.send_email_lifnr([id])
        sql = "update mat_demand_line_details set calculate_initial_flag='t'  where mat_demand_id=" + str(
            ids[0]) + ""  # 区别供应商是否有更新数据
        cr.execute(sql)


        return True

    def send_email_lifnr(self,ids):
        cr=self._cr
        uid=self._uid
        sql = "select id from  mat_demand_line_details where mat_demand_id=" + str(ids[0]) + " and spillover_scheduling=1"
        cr.execute(sql)
        spillover_scheduling = cr.fetchone()
        if not spillover_scheduling:
            sql = "update mat_demand_line_details set spillover_scheduling=1  where mat_demand_id=" + str(ids[0]) + ""  #邮件区分是否新增
            cr.execute(sql)
            sql = "update mat_demand_line set spillover_scheduling=1  where mat_demand_id=" + str(ids[0]) + ""
            cr.execute(sql)
        ir_model_data = self.env['ir.model.data']
        template_ids = ir_model_data.get_object_reference('srm_demand_publish', 'email_template_mat_demand')[1]
        email_template_obj_message = self.env['mail.compose.message']
        if template_ids:
            attachment_ids_value = email_template_obj_message.onchange_template_id(template_ids, 'comment',  'mat.demand.head', ids[0])
            vals = {}
            vals['composition_mode'] = 'comment'
            vals['template_id'] = template_ids
            vals['parent_id'] = False
            vals['notify'] = False
            vals['no_auto_thread'] = False
            vals['reply_to'] = False
            vals['model'] = 'mat.demand.head'
            partner_ids = []
            partner_ids.append([6, False, attachment_ids_value['value']['partner_ids']])
            vals['partner_ids'] = attachment_ids_value['value']['partner_ids']
            vals['body'] = attachment_ids_value['value']['body']
            vals['res_id'] = ids[0]
            vals['email_from'] = attachment_ids_value['value']['email_from']
            vals['subject'] = attachment_ids_value['value']['subject']
            emil_id = self.env['mail.compose.message'].create(vals)
            emil_id.send_mail()
        return True


class mat_demand_line_details(models.Model):
    _name = "mat.demand.line.details"
    _table = 'mat_demand_line_details'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "物料需求明细行"

    STATE_SELECTION = [
        ('create', 'Create'),
        ('supplier_confirm', 'Supplier Confirm'),
        ('supplier_edit', 'Supplier Edit'),
        ('purchase_edit', 'Purchase Edit'),
        ('sys_cancel', 'System Cancel'),
        ('purchase_confirm', 'Purchase Confirm'),
        ('not_confirm', 'Not Confirm'),
        ('delete', 'Delete'),
    ]

    mat_demand_id = fields.Many2one('mat.demand.head','Mat Demand Id',required=True, readonly=True, ondelete='cascade')
    lifnr = fields.Many2one('res.partner', 'Supplier', required=False,domain=[('supplier', '=', True)])
    ekgrp = fields.Many2one('product.category', 'Purchase Group')
    matnr = fields.Many2one ('product.product', 'Material', required=True,domain=[('purchase_ok', '=', True)])
    menge = fields.Integer('Demand Amount', required=True,track_visibility='onchange')
    meins = fields.Many2one('uom.uom', 'Unit', required=False)
    ddate = fields.Date('Demand Date', required=True, track_visibility='onchange')
    bmeng = fields.Integer('Confirm Amount')
    memo = fields.Text('Remark', track_visibility='onchange')
    state = fields.Selection(STATE_SELECTION, 'Status', track_visibility='onchange',default='create')
    prnum = fields.Char('Produce Order')
    monum = fields.Char('Model')
    delivery = fields.Boolean('Delivery')
    calculate_initial_flag =fields.Boolean('Calculate initial flag',default=False)  #用来识别发送邮件，F 发送 T不发送 默认发送
    spillover_scheduling = fields.Integer('spillover scheduling')   #用作邮件发送时识别是修改还是新增
    pdate=fields.Date('Production date')  #生产日期
    needs_no=fields.Char('Needs No')
    publish = fields.Boolean('publish',default=False)  #行项目发布状态
    create_versi=fields.Char('Create versi')

    @api.constrains('matnr')
    def check_matnr(self):
        if self.matnr:
            supplierinfo = self.env['product.supplierinfo'].search(
                [('product_tmpl_id', '=', self.matnr.product_tmpl_id.id)]);
            if not supplierinfo:
                raise exceptions.ValidationError("Material does not maintain the supplier")
        self.unique_check(self.mat_demand_id.id,self.lifnr.id,self.matnr.id,self.ddate,self.prnum,self.id)


    def unique_check(self,mat_demand_id,lifnr,matnr,ddate,prnum,id):
        sql = "select id  from mat_demand_line_details where needs_no='"+str(self.needs_no)+"' and  mat_demand_id=" + str(self.mat_demand_id.id) + " "
        sql += "and lifnr=" + str(self.lifnr.id) + " and matnr=" + str(self.matnr.id) + " "
        sql += " and ddate='" + str(self.ddate) + "' and prnum='" + str(self.prnum) + "' and id<>" + str(self.id) + ""
        self._cr.execute(sql)
        isf = self._cr.fetchone()
        if isf:
            raise exceptions.ValidationError(" Data duplication ")

    # @api.constrains('needs_no')
    # def check_needs_no(self):
    #     sql = "select id  from mat_demand_line_details where needs_no='" + str(
    #         self.needs_no) + "' and  mat_demand_id=" + str(self.mat_demand_id.id) + " and id<>" + str(self.id) + ""
    #     self.env.cr.execute(sql)
    #     isf = self.env.cr.fetchone()
    #     if isf:
    #         raise exceptions.ValidationError(" needs_no duplication ")

    @api.constrains('ddate')
    def check_ddate(self):
      self.unique_check(self.mat_demand_id.id,self.lifnr.id,self.matnr.id,self.ddate,self.prnum,self.id)
    @api.constrains('lifnr')
    def check_lifnr(self):
        self.unique_check(self.mat_demand_id.id, self.lifnr.id, self.matnr.id, self.ddate, self.prnum, self.id)
    @api.constrains('prnum')
    def check_prnum(self):
        self.unique_check(self.mat_demand_id.id, self.lifnr.id, self.matnr.id, self.ddate, self.prnum, self.id)

    def update_state(self,id):
        cr=self._cr
        line = self.browse(id)
        is_publish = False
        if line.mat_demand_id.state == 'publish' or line.mat_demand_id.state == 'edit_publish':
            if line.lifnr.schedule_confirm:
                sql = "update mat_demand_line_details set state = 'purchase_edit' where id =" + str(id)
                #cr.execute(sql)

            else:
                sql = "update mat_demand_line_details set state = 'not_confirm' ,bmeng=menge where id =" + str(id)
                cr.execute(sql)

    def tranDate(self,strDate):
        strDate1 = ''
        try:
            if strDate.find('/',0,len(strDate)) > 0:
                strDate1 = datetime.strftime(datetime.strptime(strDate, '%Y/%m/%d'), '%Y-%m-%d');
            elif strDate.find('.', 0, len(strDate)) > 0:
                strDate1 = datetime.strftime(datetime.strptime(strDate, '%Y.%m.%d'), '%Y-%m-%d');
            elif strDate.find('-', 0, len(strDate)) > 0:
                strDate1 = strDate

            if len(strDate1) < 10 or len(strDate1) > 10:
                raise exceptions.ValidationError("Date format error, correct case example: 2018-07-02. Please re-enter.");
        except:
            raise exceptions.ValidationError("Date format error, correct case example: 2018-07-02. Please re-enter.");
        return strDate1

    @api.model_create_multi
    def create(self,values):

        is_supplier = self.env['res.users']._get_default_supplier()
        # 供应商不能创建
        if is_supplier != 0:
            return True

        supplier_self = self.env['product.supplierinfo']
        comco = self.env['res.company']._company_default_get('mat.demand.head')

        add_vals = []

        for vals in values:
            matobj = self.env['product.product'].browse(vals['matnr'])
            uom_id = matobj.product_tmpl_id.uom_id.id
            supplierinfo_temp = supplier_self.search([('product_tmpl_id', '=', matobj.product_tmpl_id.id),
                                                          ('company_id', '=', comco.id)],)

            if not supplierinfo_temp:
                raise exceptions.ValidationError(matobj.default_code + " Material does not maintain the supplier")

            supplierinfo = []
            pe=0
            sinfo = []

            for supplier in supplierinfo_temp:
                s_obj = supplier_self.browse(supplier.id)
                if s_obj.the_quota > 0:
                    pe = s_obj.the_quota + pe
                    sinfo.append(s_obj)

            supplierinfo=supplierinfo_temp

            head_history_data_id = vals.get('mat_demand_id',False)
            if not head_history_data_id:
                head = self.env['mat.demand.head'].search([('history_data','=',False)],limit=1)
                head_history_data_id = head.id
                vals['mat_demand_id'] = head_history_data_id


            head_history_data = self.env['mat.demand.head'].browse(head_history_data_id)
            self.valida_is_history_data(head_history_data.history_data)
            ddate = str(vals['ddate'])
            vals['ddate'] = self.tranDate(ddate)

            try:
               pdate = str(vals['pdate'])
               vals['pdate'] = self.tranDate(pdate)
            except:
              pass

            if len(supplierinfo) == 1:
                s_obj = supplier_self.browse(supplierinfo.id)
                vals['lifnr'] = s_obj.name.id
                vals['meins'] = uom_id
                # lid = super(mat_demand_line_details, self).create(vals)
                # self.update_state(lid.id)
                # return lid
            else:
                if len(sinfo) == 1:
                    s_obj = sinfo[0]
                    vals['lifnr'] = s_obj.name.id
                    vals['meins'] = uom_id
                    # lid = super(mat_demand_line_details, self).create(vals)
                    # self.update_state(lid.id)
                    # return lid
                elif len(sinfo) == 0:
                    menge = vals['menge'] / len(supplierinfo)
                    num = 0
                    copy_vals = vals.copy()

                    for supplier in supplierinfo:
                        s_obj = supplier_self.browse(supplier.id)
                        if num > 0:
                            copy_vals['lifnr'] = s_obj.name.id
                            copy_vals['meins'] = uom_id
                            copy_vals['menge'] = menge
                            add_vals.append(copy_vals)
                        else:
                            vals['lifnr'] = s_obj.name.id
                            vals['meins'] = uom_id
                            vals['menge'] = menge
                        num = num + 1
                        # lid = super(mat_demand_line_details, self).create(vals)
                        # self.update_state(lid.id)
                else:
                    total_menge = vals['menge']
                    remaining_quantity = 0
                    i = 1
                    num = 0
                    copy_vals = vals.copy()
                    for s in sinfo:
                        s_obj = s
                        if num > 0:
                            if i == len(sinfo):
                                copy_vals['lifnr'] = s_obj.name.id
                                copy_vals['meins'] = uom_id
                                copy_vals['menge'] = remaining_quantity
                            else:
                                copy_vals['lifnr'] = s_obj.name.id
                                copy_vals['meins'] = uom_id
                                copy_vals['menge'] = round(s_obj.the_quota / pe * total_menge, 0)
                                remaining_quantity = total_menge - copy_vals['menge']
                                add_vals.append(copy_vals)
                        else:
                            if i == len(sinfo):
                                vals['lifnr'] = s_obj.name.id
                                vals['meins'] = uom_id
                                vals['menge'] = remaining_quantity
                            else:
                                vals['lifnr'] = s_obj.name.id
                                vals['meins'] = uom_id
                                vals['menge'] = round(s_obj.the_quota / pe * total_menge, 0)
                                remaining_quantity = total_menge - vals['menge']


                        # lid = super(mat_demand_line_details, self).create(vals)
                        i = i + 1
                        # self.update_state(lid.id)
        values.extend(add_vals)

        lid = super(mat_demand_line_details, self).create(values)
        for l in lid:
            # l = super(mat_demand_line_details, self).create(v)
            # lid.append(l)
            self.update_state(l.id)

        return lid



    def unlink(self):
        cr=self._cr
        uid=self._uid

        for id in self.ids:
            sql = "update mat_demand_line_details set calculate_initial_flag='f' where id=" + str(id) + ""
            cr.execute(sql)
            mat = self.browse(id)
            self.valida_delivery_order(mat,'D')
            vals = {}
            vals['id'] = id
            vals['lifnr'] = mat.lifnr.id
            vals['matnr'] = mat.matnr.id
            vals['ddate'] = mat.ddate
            vals['mat_demand_id'] = mat.mat_demand_id.id
            vals['state'] = 'purchase_edit'
            if mat.mat_demand_id.state == 'publish':
                sql = "update mat_demand_line_details set bmeng=0,menge=0 where id =" + str(id)
                cr.execute(sql)
                super(mat_demand_line_details, self).write({'state': 'delete'})
                # raise exceptions.ValidationError('Publish Status not Delete')
            else:
                sql = "update mat_demand_line_details set bmeng=0,menge=0 where id =" + str(id)
                cr.execute(sql)
                super(mat_demand_line_details, self).write({'state': 'delete'})
            self.insert_mat_demand_line_details(vals,)
        return True

    def write(self, vals):
        cr = self._cr
        ids= self.ids
        uid =self._uid
        is_supplier = self.env['res.users']._get_default_supplier()
        if len(ids)>0:
            line_obj = self.browse(ids[0])
        elif 'ids' in vals.keys():
            ids=vals['ids']
            line_obj = self.browse(ids[0])
        else:
            raise exceptions.ValidationError("更新异常。")
        if is_supplier != 0 :
            # 供应商批量确认

            if 'bmeng' in vals.keys():
                if line_obj.menge < float(vals['bmeng']):
                    raise exceptions.ValidationError("确认数量大于需求数量")
                sql = "update mat_demand_line_details set bmeng=" + str(vals['bmeng']) + " where id=" + str(ids[0]) + ""
                cr.execute(sql)
                sql = "select  sum(bmeng) as bmeng  from mat_demand_line_details   WHERE lifnr=" + str(
                    line_obj.lifnr.id) + " and ddate='" + str(line_obj.ddate) + "' and matnr=" + str(
                    line_obj.matnr.id) + "  and mat_demand_id=" + str(
                    line_obj.mat_demand_id.id) + " and state<>'delete' and publish='t'"
                cr.execute(sql)
                sumbmeng = cr.fetchone()
                if sumbmeng:
                    sql = "update mat_demand_line set bmeng=" + str(sumbmeng[0]) + " WHERE lifnr=" + str(
                        line_obj.lifnr.id) + "  and ddate='" + str(line_obj.ddate) + "' and matnr=" + str(
                        line_obj.matnr.id) + "  and mat_demand_id=" + str(
                        line_obj.mat_demand_id.id) + " and state<>'delete' and publish='t'"
                    cr.execute(sql)
                return True
            else:
                return
        else:
            if 'bmeng' in vals.keys():
                if float(vals['bmeng']) > line_obj.bmeng:
                    print(vals)
                sql = "update mat_demand_line_details set bmeng=" + str(vals['bmeng']) + " where id=" + str(ids[0]) + ""
                cr.execute(sql)
                return True

        mat_obj = self.browse(ids[0]).mat_demand_id
        self.valida_delivery_order(line_obj,'W')
        super(mat_demand_line_details, self).write(vals)
        if (mat_obj.state == 'publish'):
            for id in ids:
                sql = "update mat_demand_line_details set calculate_initial_flag='f' where id=" + str(id) + ""
                cr.execute(sql)
                line_obj = self.browse(id)

                if line_obj.state != 'not_confirm' and line_obj.state != 'delete':
                    if 'publish' in vals.keys():
                        if vals['publish'] != 't':
                            sql = "update mat_demand_line_details set publish='f',state='purchase_edit' where id=" + str(
                                id) + ""
                            cr.execute(sql)
                    else:
                        sql = "update mat_demand_line_details set publish='f',state='purchase_edit' where id=" + str(
                            id) + ""
                        cr.execute(sql)
                vals['id'] = id
                vals['lifnr'] = line_obj.lifnr.id
                vals['matnr'] = line_obj.matnr.id
                vals['ddate'] = line_obj.ddate
                vals['mat_demand_id'] = line_obj.mat_demand_id.id
                state_temp = line_obj.state
                if line_obj.lifnr.schedule_confirm == True and line_obj.state == 'not_confirm':
                    sql = " update mat_demand_line_details set  state='purchase_edit',publish='f' where id=" + str(
                        id) + " "
                    cr.execute(sql)
                    state_temp = 'purchase_edit'
                elif line_obj.lifnr.schedule_confirm == False and line_obj.state != 'not_confirm':
                    sql = " update mat_demand_line_details set  state='not_confirm',publish='t' where id=" + str(
                        id) + " "
                    cr.execute(sql)
                    state_temp = 'not_confirm'
                vals['state'] = state_temp
                if line_obj.menge != line_obj.bmeng:
                    sql = "update mat_demand_line_details set delivery='f' where id=" + str(id) + ""
                    cr.execute(sql)
                self.insert_mat_demand_line_details(vals)
        else:
            for id in ids:
                sql = "update mat_demand_line_details set calculate_initial_flag='f' where id=" + str(id) + ""
                cr.execute(sql)
                line_obj = self.browse(id)
                if line_obj.state != 'not_confirm' and line_obj.state != 'delete':
                    self.valida_delivery_order(line_obj, 'W')
                vals['id'] = id
                vals['lifnr'] = line_obj.lifnr.id
                vals['matnr'] = line_obj.matnr.id
                vals['ddate'] = line_obj.ddate
                vals['mat_demand_id'] = line_obj.mat_demand_id.id
                vals['state'] = line_obj.state
                if line_obj.menge != line_obj.bmeng:
                    sql = "update mat_demand_line_details set delivery='f' where id=" + str(id) + ""
                    cr.execute(sql)
                self.insert_mat_demand_line_details (vals)
        return True

    def valida_delivery_order(self,line_obj,type):
        cr=self._cr
        uid=self._uid
        delivery_sql = "select sum(dnmng) as admng,sum(aomng) as aomng  from delivery_order h inner join delivery_order_line l "
        delivery_sql += " on h.id = l.delivery_order_id "
        delivery_sql += " where h.comco = %s and h.werks = %s and h.lifnr = %s and l.matnr = %s"
        delivery_sql += " and h.datoo = %s and h.state not in ('supplier_cancel') "
        delivery_sql += " and l.version_id = %s and l.prnum=%s"
        cr.execute(delivery_sql, (
            line_obj.mat_demand_id.comco.id, line_obj.mat_demand_id.werks.id, line_obj.lifnr.id, line_obj.matnr.id,
            str(line_obj.ddate),
            line_obj.mat_demand_id.id,line_obj.prnum or ''))
        delivery_dnmng = cr.fetchone()
        if type=='W':
            if delivery_dnmng and delivery_dnmng[0] and delivery_dnmng[0]>0:
                isExceptions=True
                exceptionsMsg = line_obj.lifnr.name + "," + line_obj.matnr.default_code + "," + line_obj.ddate + ",修改失败，已创建交货单"
                if 'lifnr' in uid.keys():
                    if uid['lifnr']==line_obj.lifnr.id:
                        isExceptions=False
                if 'matnr' in uid.keys():
                    if uid['matnr']==line_obj.matnr.id:
                        isExceptions=False

                if 'ddate' in uid.keys():
                    if uid['ddate']==line_obj.ddate:
                        isExceptions=False

                if 'menge' in uid.keys():
                    if delivery_dnmng[0]<= uid['menge']:
                        isExceptions = False
                        exceptionsMsg=line_obj.lifnr.name + "," + line_obj.matnr.default_code + "," + line_obj.ddate + ",不能小于已交货数," + str(delivery_dnmng[0])

                if isExceptions:
                   raise exceptions.ValidationError(exceptionsMsg)





        if type == 'D':
            if delivery_dnmng and delivery_dnmng[0] and delivery_dnmng[0] >0:
                raise exceptions.ValidationError(
                    line_obj.lifnr.name + "," + line_obj.matnr.default_code + "," + line_obj.ddate + ",删除失败，已创建交货单," + str(
                        delivery_dnmng[0]))

    def valida_is_history_data(self,history_data):
        if history_data==True:
            raise exceptions.ValidationError('Cannot edit history version')

    def insert_mat_demand_line_details(self,valss):
        cr=self._cr
        sql = "delete from mat_demand_line WHERE lifnr=" + str(valss['lifnr']) + " and ddate='" + str(valss['ddate']) + "' and matnr=" + str( valss['matnr'])+" and mat_demand_id ="+str(valss['mat_demand_id'])+""
        cr.execute(sql)

        sql = "delete from mat_demand_line WHERE id=" + str(valss['id']) + " "
        cr.execute(sql)

        sql = "SELECT "
        sql += " ID, "
        sql += " bmeng,"
        sql += " mat_demand_id,"
        sql += " create_uid,"
        sql += " menge,"
        sql += " STATE,"
        sql += " matnr,"
        sql += " memo,"
        sql += " monum,"
        sql += " meins,"
        sql += " ddate,"
        sql += " ekgrp,"
        sql += " prnum,"
        sql += " lifnr,"
        sql += " spillover_scheduling,"
        sql += " delivery,"
        sql+="   publish"
        sql += " FROM "
        sql += " mat_demand_line_details"
        sql += " WHERE lifnr=" + str(valss['lifnr']) + " and ddate='" + str(valss['ddate']) + "' and matnr=" + str( valss['matnr'])+" and mat_demand_id ="+str(valss['mat_demand_id'])+" and publish='t'"


        cr.execute(sql)
        vals = cr.fetchone()
        if not vals:
          return

        sql = "INSERT into "
        sql += " mat_demand_line ( "
        sql += "ID, "
        sql += "bmeng, "
        sql += "mat_demand_id, "
        sql += "create_uid, "
        sql += "menge, "
        sql += "STATE, "
        sql += "matnr, "
        sql += "memo, "
        sql += "monum, "
        sql += "meins, "
        sql += "ddate, "
        sql += "ekgrp, "
        sql += "prnum, "
        sql += "lifnr,  "

        sql += "spillover_scheduling ,delivery,publish  "
        sql += " )  "
        sql += " values "
        sql += "( %s, "
        sql += "%s,  "
        sql += "%s,  "
        sql += "%s, "
        sql += "%s , "
        sql += "%s , "
        sql += "%s , "
        sql += "%s , "
        sql += "%s , "
        sql += "%s , "
        sql += "%s , "
        sql += "%s , "
        sql += "%s , "
        sql += "%s,  "
        sql += "%s,%s,%s ) "
        # cr.execute(sql,(vals['id'],vals['bmeng'],vals['mat_demand_id'],vals['create_uid'],vals['menge'],vals['STATE'],
        #                 vals['matnr'],vals['memo'],vals['monum'],vals['meins'],vals['ddate'],vals['ekgrp'],
        #                 vals['prnum'],vals['lifnr'],))
        is_flag = False
        if vals[1]:
            is_flag = False
        else:
            vals[1] == ''

        if vals[7]:
            is_flag = False
        else:
            vals[7] == ''

        if vals[8]:
            is_flag = False
        else:
            vals[8] == ''

        if vals[12]:
            is_flag = False
        else:
            vals[12] == ''

        if vals[14]:
            is_flag = False
        else:
            vals[14] == ''

        if vals[15]:
            is_flag = False
        else:
            vals[15] == ''


        cr.execute(sql,
                   (vals[0], vals[1], vals[2], vals[3], vals[4], valss['state'],
                    vals[6], vals[7], vals[8], vals[9], vals[10], vals[11],
                    vals[12], vals[13],vals[14],vals[15],vals[16]))

        # 合并原始表数据
        sql = "SELECT "
        sql += " ID, "
        sql += " bmeng,"
        sql += " mat_demand_id,"
        sql += " create_uid,"
        sql += " menge,"
        sql += " STATE,"
        sql += " matnr,"
        sql += " memo,"
        sql += " monum,"
        sql += " meins,"
        sql += " ddate,"
        sql += " ekgrp,"
        sql += " prnum,"
        sql += " lifnr,"
        sql += " spillover_scheduling"
        sql += " FROM "
        sql += " mat_demand_line_details"
        sql += " WHERE lifnr=" + str(vals[13]) + " and ddate='" + str(vals[10]) + "' and matnr=" + str(
            vals[6]) + "  and mat_demand_id=" + str(vals[2]) + " and state<>'delete' and publish='t'"
        cr.execute(sql)

        list_value = cr.dictfetchall()
        menge = 0
        bmeng = 0

        spillover_scheduling=1
        for data_value in list_value:
            if data_value['menge']:
                menge = menge + data_value['menge']

            if data_value['bmeng']:
                bmeng = bmeng + data_value['bmeng']
                #bmeng =data_value['bmeng']
            if not data_value['spillover_scheduling']:
                spillover_scheduling='NULL'

        state=''
        if 'state' in valss.keys():
            state=valss['state']

        if menge==bmeng:
            sql = "update mat_demand_line_details set delivery='t',state='"+str(state)+"' WHERE lifnr=" + str(
                vals[13]) + " and ddate='" + str(vals[10]) + "' and matnr=" + str(
                vals[6]) + "  and mat_demand_id=" + str(vals[2]) + " and publish='t' "
            cr.execute(sql)

            sql = "update mat_demand_line set menge=" + str(menge) + " ,bmeng=" + str(
                bmeng) + " ,spillover_scheduling=" + str(spillover_scheduling) + " ,state='"+str(state)+"',delivery='t'  WHERE lifnr=" + str(
                vals[13]) + " and ddate='" + str(vals[10]) + "' and matnr=" + str(
                vals[6]) + "  and mat_demand_id=" + str(vals[2]) + " and publish='t' "
            cr.execute(sql)
        else:
            if bmeng==0:
                 sql = "update mat_demand_line set menge=" + str(menge) + " ,bmeng=" + str(
                 bmeng) + " ,spillover_scheduling=" + str(
                 spillover_scheduling) + " ,state='create'  WHERE lifnr=" + str(
                 vals[13]) + " and ddate='" + str(vals[10]) + "' and matnr=" + str(
                 vals[6]) + "  and mat_demand_id=" + str(vals[2]) + " and publish='t' "
                 cr.execute(sql)
            else:
                sql = "update mat_demand_line set menge=" + str(menge) + " ,bmeng=" + str(
                    bmeng) + " ,spillover_scheduling=" + str(
                    spillover_scheduling) + "  WHERE lifnr=" + str(
                    vals[13]) + " and ddate='" + str(vals[10]) + "' and matnr=" + str(
                    vals[6]) + "  and mat_demand_id=" + str(vals[2]) + " and publish='t' "
                cr.execute(sql)






class mat_demand_line(models.Model):
    _name = "mat.demand.line"
    _table = 'mat_demand_line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "物料需求汇总行"

    STATE_SELECTION = [
        ('create', 'Create'),
        ('supplier_confirm', 'Supplier Confirm'),
        ('supplier_edit', 'Supplier Edit'),
        ('purchase_edit', 'Purchase Edit'),
        ('sys_cancel', 'System Cancel'),
        ('purchase_confirm', 'Purchase Confirm'),
        ('not_confirm', 'Not Confirm'),
        ('delete', 'Delete'),
    ]

    mat_demand_id = fields.Many2one('mat.demand.head','Mat Demand Id',required=True, readonly=True, ondelete='cascade')
    lifnr = fields.Many2one('res.partner', 'Supplier', required=False, domain=[('supplier', '=', True)])
    ekgrp = fields.Many2one('product.category', 'Purchase Group')
    matnr = fields.Many2one('product.product', 'Material', required=True, domain=[('purchase_ok', '=', True)])
    menge = fields.Integer('Demand Amount', required=True,track_visibility='onchange')
    meins = fields.Many2one('uom.uom', 'Unit', required=False)
    ddate = fields.Date('Demand Date', required=True, track_visibility='onchange')
    bmeng = fields.Integer('Confirm Amount')
    memo = fields.Text('Remark', track_visibility='onchange')
    state = fields.Selection(STATE_SELECTION, 'Status', track_visibility='onchange',default='create')
    prnum = fields.Char('Produce Order')
    monum = fields.Char('Model')
    delivery = fields.Boolean('Delivery')
    calculate_initial_flag =fields.Boolean('Calculate initial flag',default=False)
    spillover_scheduling = fields.Integer('spillover scheduling')
    pdate = fields.Date('Production date')  # 生产日期
    needs_no = fields.Char('Needs No')
    publish = fields.Boolean('publish', default=False)  # 行项目发布状态









