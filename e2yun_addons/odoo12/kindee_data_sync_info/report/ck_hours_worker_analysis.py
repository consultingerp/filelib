# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api
from odoo import tools, _
import odoo.addons.decimal_precision as dp


class ck_hours_worker_rep(models.Model):
    _name = "ck.hours.worker.rep"
    _description = "CK Hours Report Of Worker"
    _auto = False

    moid = fields.Many2one('ck.icmo.sync', string='Production', readonly=True),   # 生产订单ID
    sono = fields.Char(string='SaleOrderNo', readonly=True),                # 销售订单号
    custno = fields.Char(string='CustmerNo', readonly=True),               # 客户编号
    sodate = fields.Datetime(string='DeliveryDate', readonly=True),          # 产品交期
    modate = fields.Datetime(string='UpdateDate', readonly=True),           # 更新时间
    model = fields.Char(string='ProductModel', readonly=True),              # 产品规格
    product_id = fields.Char(string='ProductNo', readonly=True),            # 产品编码（长）
    product_name = fields.Char(string='ProductDesc', readonly=True),        # 产品描述
    mo_qty = fields.Float('MO Quantity',
                           digits=dp.get_precision('ck_workqty_digit'), readonly=True),  # 生产订单数量
    date_start = fields.Datetime(string='Valid From', readonly=True),         # 开始时间
    date_stop = fields.Datetime(string='Valid Until', readonly=True),        # 结束时间
    state = fields.Selection([('draft', 'Draft'), ('open', 'In Progress'), ('cancel', 'Cancelled'),
                             ('done', 'Finished')], 'Status', readonly=True),  # 生产状态
    user_id = fields.Many2one('res.users', string=_('Owner'), readonly=True),  # 用户ID
    pid = fields.Char(string='User No', readonly=True),                    # 员工编号
    operno = fields.Char(string='OperationNo', readonly=True),             # 工序编码
    opername = fields.Char(string='OperationName', readonly=True),         # 工序名称
    feed_qty = fields.Float(string='Picking Quantity',
                             digits=dp.get_precision('ck_workqty_digit'), readonly=True),  # 发料数量
    accept_qty = fields.Float(string='Good Quantity',
                               digits=dp.get_precision('ck_workqty_digit'), readonly=True),  # 良品数量
    reject_qty = fields.Float(string='Scrap Quantity',
                               digits=dp.get_precision('ck_workqty_digit'), readonly=True),  # 报废数量
    accepted_qty = fields.Float(string='Confirm Good Quantity',
                               digits=dp.get_precision('ck_workqty_digit'), readonly=True),  # 确认良品数量
    rejected_qty = fields.Float(string='Confirm Scrap Quantity',
                           digits=dp.get_precision('ck_workqty_digit'), readonly=True),  # 确认报废数量
    amount = fields.Float(string='Confirm Amount',
                           digits=dp.get_precision('ck_workamount_digit'), readonly=True),  # 确认工费
    price = fields.Float(string='Price',
                          digits=dp.get_precision('ck_workprice_digit'), readonly=True)  # 已确认部分工价

    def init(self):
        tools.drop_view_if_exists(self._cr, 'ck_hours_worker_rep')
        self._cr.execute("""
            create or replace view ck_hours_worker_rep as (
               select  a.id as moid, a.seobillno as sono,a.fcustno as custno,a.fdate as sodate,
                      a.fconfirmdate as modate,a.fmodel as model,a.fnumber as product_id,
                      a.fname as product_name,a.fqty as mo_qty,
                      c.date_start as date_start ,c.date_stop AS date_stop,
                      c.state ,c.user_id,c.pid,
                      c.operno,c.opername,
                      case when c.feed_qty > 0 then c.feed_qty
                           else 0 END
                      as feed_qty,
                      case when c.accept_qty > 0 then c.accept_qty
                           else 0 END
                      as accept_qty,
                      case when c.reject_qty > 0 then c.reject_qty
                           else 0 END
                      as reject_qty,
                      case when c.accepted_qty > 0 then c.accepted_qty
                           else 0 END
                      as accepted_qty,
                      case when c.rejected_qty > 0 then c.rejected_qty
                           else 0 END
                      as rejected_qty,
                      case when c.amount > 0 then c.amount
                           else 0 end
                      as amount,
                      case when c.accepted_qty > 0  and cast(c.amount / c.accepted_qty * 1000.00  as numeric)  > 0 then
                              cast(c.amount / c.accepted_qty * 1000.00  as numeric)
                           else 0 end
                      as price,
                      ROW_NUMBER() OVER(ORDER BY a.id) AS  id

              from ck_icmo_sync a RIGHT JOIN  (
                  select  b.production_id ,  min(b.date_start) as date_start , max(b.date_stop) as date_stop,
                          case  when max(b.state) = 'open' then 'open'
                                when max(b.state) = 'done' then 'done'
                          ELSE 'draft' END as state,
                          b.user_id as user_id, d.login as pid,
                          b.foperno as operno,b.fopername as opername,
                          sum(b.pqty) as feed_qty,sum(b.gqty) AS accept_qty,sum(b.sqty)as reject_qty,
                          sum(f.gqty) as accepted_qty,sum(f.sqty) as rejected_qty,sum(f.amount) as amount
                  from ck_hours_worker b  LEFT JOIN res_users d on b.user_id = d.id
                                          LEFT JOIN ck_hours_worker_line f on b.id = f.order_id and f.state ='done'
                  GROUP BY b.production_id,b.user_id,b.foperno,b.fopername,d.login)  c
              on a.id = c.production_id
        )""")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
