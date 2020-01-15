# -*- coding: utf-8 -*-

from odoo import models, fields, api,exceptions
from odoo import tools, _
from datetime import datetime

class srm_demand_delivery_line_view(models.Model):
    _name = 'srm.demand.delivery.line.view'
    _auto = False

    STATE_SELECTION = [
        ('create', '创建'),
        ('supplier_confirm', '供应商确认'),
        ('supplier_edit', '供应商修改'),
        ('purchase_edit', '采购修改'),
        ('sys_cancel', '系统取消'),
        ('purchase_confirm', '采购确认'),
        ('not_confirm', '无需确认'),
        ('delete', '删除'),
    ]

    versi = fields.Char('Version', readonly=True)
    prefix_code = fields.Char('Matnr Code', readonly=True)
    matnr = fields.Char('Matnr', readonly=True)
    lifnr = fields.Char('Supplier',default=lambda self: self.env['res.users']._get_default_supplier())
    supplier_code = fields.Char('Supplier Code', readonly=True)
    supplier_name = fields.Char('Supplier Name', readonly=True)
    datoo = fields.Date('Demand Date', readonly=True)
    menge = fields.Integer('Demand Qty', required=True,default=0)
    bmeng = fields.Integer('Confirm Qty', required=True,default=0)
    dnmng = fields.Integer('Delivery Qty', required=True,default=0)
    done_menge = fields.Integer('Goods Qty', required=True,default=0)
    prnum = fields.Char('Production Order')
    monum = fields.Char('Model')
    state = fields.Selection(STATE_SELECTION, 'Status')
    publish = fields.Boolean('Publish', default=False)
    werks = fields.Char('werks')  # 工厂
    allow_create_days = fields.Integer(String='Allow create days')
    isscheduledate = fields.Boolean('isscheduledate',default=True)
    isallownoschedulecreate = fields.Boolean('isallownoschedulecreate',default=True)

    @api.one
    def _compute_diff_qty(self):
        self.diff_qty = self.menge - self.bmeng

    def _get_isAllowCreate(self):
        for obj in self:
            datoo = datetime.strptime(obj.datoo, '%Y-%m-%d')
            nowstr = datetime.strftime(datetime.now(), '%Y-%m-%d')
            nowdate = datetime.strptime(nowstr, '%Y-%m-%d')
            if obj.allow_create_days > 0 and (datoo - nowdate).days > obj.allow_create_days:
                obj.isAllowCreate = False
            else:
                obj.isAllowCreate = True

    diff_qty = fields.Integer('Difference Qty', compute=_compute_diff_qty)
    isAllowCreate = fields.Boolean('isAllowCreate', compute='_get_isAllowCreate',default=True)

    def search(self,args, offset=0, limit=None, order=None,count=False):
        lifnr = self.env['res.users']._get_default_supplier()
        if lifnr > 0:
            args += [('lifnr', '=', lifnr)]

        return super(srm_demand_delivery_line_view, self).search(args, offset=offset, limit=limit, order=order,count=count)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'srm_demand_delivery_line_view')
        self._cr.execute(""" 
                        create or replace view srm_demand_delivery_line_view as (
                            select t.* from (select (select allow_create_days from res_partner where id = lifnr) as allow_create_days,'True' as isAllowCreate,
                            'True' as isscheduledate,'True' as isallownoschedulecreate,
                            d.id as id,h.versi,pr.default_code as prefix_code,pt.name as matnr,lifnr,d.prnum,d.monum,0 as diff_qty,d.state,
                            rp.supplier_code as supplier_code ,rp.name as supplier_name,ddate as datoo ,menge,bmeng ,publish,mdh.werks,
                            COALESCE((select sum(dnmng) from delivery_order_line where line_version_id = d.id
                            GROUP BY d.id 
                            ),0) dnmng,
                            COALESCE((select sum(dp.done_menge) from delivery_purchase_orders dp inner join delivery_order_line dol on dp.delivery_order_line_id = dol.id and dol.line_version_id = d.id
                            GROUP BY d.id),0) done_menge 
                            from mat_demand_line_details d inner join mat_demand_head h on d.mat_demand_id  = h.id
                            left join product_product pr on pr.id = d.matnr
                            left join product_template pt on pt.id = pr.product_tmpl_id
                            left join res_partner rp on rp.id = lifnr
                            LEFT JOIN  mat_demand_head mdh on mdh.id=d.mat_demand_id
                            where d.publish = 't'
                        ) t where t.menge - t.done_menge >0 )""")



    def get_last_day_data(self,lifnr,datoo):
        self._cr.execute("select id from srm_demand_delivery_line_view where (menge - coalesce(dnmng,0)) > 0 and lifnr=%s and datoo < %s ", (lifnr,datoo))
        data = self._cr.dictfetchall()
        if data and len(data) > 0:
            return True
        else:
            return False

    @api.multi
    def action_delivery(self):
        id2 = self.env.ref('srm_delivery_order.srm_delivery_order_form')
        ctx = self._context.copy()
        ctx['werks'] = self.werks
        ctx['datoo'] = self.datoo
        ctx['isscheduledate'] = self.isscheduledate
        ctx['isallownoschedulecreate'] = self.isallownoschedulecreate
        ctx['prnum'] = self.prnum
        ctx['versi'] = self.versi
        return {
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'delivery.order',
            'views': [(id2.id, 'form')],
            'view_id': id2.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': ctx
        }

    @api.multi
    def check_create_delivery(self):
        if self.get_last_day_data(self.lifnr, self.datoo) and self.versi:

            msg_obj = self.env['confirm.msg'].create(
                {'confirm_title': "提示",
                 'confirm_msg': "历史日期有未完成的排程交货，是否继续创建交货单?",
                 'previous_id': self[0].id,
                 'previous_type': self._name,
                 'previous_method': 'action_delivery'})
            if msg_obj:
                return msg_obj.do_confirm_action()
        else:
            return self.action_delivery()