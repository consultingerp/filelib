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

from odoo import fields, models
from odoo import tools, api, _
import addons.decimal_precision as dp

'''
class ck_hours_worker_rep_four(models.Model):
    _name = 'ck.hours.worker.rep.four'
    _description = 'CK Hours Report Of Worker Four Sheets'
    _auto = False
    _columns = {
        'user_id': fields.integer(string='UserId'), readonly=True),
        'order_id': fields.integer(string='OrderId'), readonly=True),
        'amount': fields.Float(string='Confirm Amount'), digits=dp.get_precision('ck_workamount_digit'),
                               readonly=True),
        'date_worker': fields.date(string='Date Worker'), readonly=True),
        'fshift': fields.selection([('day', '白班')), ('night', '晚班'))],
                                   string='Shift'), readonly=True),
        'fmachine': fields.selection([('one', '单机')), ('multi', '双机'))],
                                     string='Number of machines'), readonly=True),
        'state': fields.selection([('new', 'New')), ('done', 'Done')), ('del', 'Delete'))],
                                  string='State'), readonly=True),
        'gqty': fields.Float(string='Good Quantity'), digits=dp.get_precision('ck_workqty_digit'), readonly=True),
        'sqty': fields.Float(string='Scrap Quantity'), digits=dp.get_precision('ck_workqty_digit'), readonly=True),
        'rqty': fields.Float(string='Remade Quantity'), digits=dp.get_precision('ck_workqty_digit'), readonly=True),
        'date_ascription': fields.date(string='Ascription Date'), readonly=True),
        'fmodel': fields.Char(string='Product Model'), readonly=True),
        'real_name': fields.Char(string='Worker Name'), readonly=True),
        'fopername': fields.Char(string='Operation Name'), readonly=True),
        'foperno': fields.Char(string='Operation No'), readonly=True),
        'fworkcentername': fields.Char(string='Work Center Name'), readonly=True),
        'froutingname': fields.Char(string='Routing Name'), readonly=True)
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ck_hours_worker_rep_four')
        cr.execute("""
            create or replace view ck_hours_worker_rep_four as
            select row_number() over(order by ck_hours_worker_line.id) id,
                ck_hours_worker_line."user_id", ck_hours_worker_line."order_id", ck_hours_worker_line."amount", 
                date(ck_hours_worker_line."date_worker"), ck_hours_worker_line."fshift", ck_hours_worker_line."fmachine", 
                ck_hours_worker_line."state", ck_hours_worker_line."gqty", ck_hours_worker_line."sqty", ck_hours_worker_line."rqty",
                date(case when extract(hour from ck_hours_worker_line."date_worker") >= 0 and extract(hour from ck_hours_worker_line."date_worker") < 12 and fshift='night' 
                then date_worker - INTERVAL'1day'
                else date_worker end) date_ascription, 
                ck_icmo_sync."fmodel", res_partner."name" real_name, ck_hours_worker."fopername",ck_hours_worker."foperno", ck_hours_worker."fworkcentername", 
                ck_routing_sync."froutingname"
                from ck_hours_worker_line
                left join ck_hours_worker on ck_hours_worker_line.order_id = ck_hours_worker."id"
                left join ck_icmo_sync on ck_icmo_sync."id" = ck_hours_worker.production_id
                left join res_users on res_users.id = ck_hours_worker_line.user_id
                left join res_partner on res_partner."id" = res_users.partner_id
                left join ck_routing_sync on ck_hours_worker.foperno = ck_routing_sync.foperno and ck_hours_worker.fworkcentername = ck_routing_sync.fworkcentername
                where ck_hours_worker_line.state = 'done'""")
'''


class ck_operation_productivity_rep(models.Model):
    _name = 'ck.operation.productivity.rep'
    _description = 'CK Operation Productivity Report'
    _auto = False

    froutingname = fields.Char(string='Routing Name', readonly=True),
    fopername = fields.Char(string='Operation Name', readonly=True),
    foperno = fields.Char(string='Operation No', readonly=True),
    gqty = fields.Float(string='Good Quantity Sum', readonly=True),
    sqty = fields.Float(string='Scrap Quantity Sum', readonly=True),
    grate = fields.Float(string='良品率(%)', digits=dp.get_precision('ck_workprice_digit')),
    srate = fields.Float(string='报废率(%)', digits=dp.get_precision('ck_workprice_digit')),
    uid_count = fields.Float(string='报工人数', readonly=True),
    uid_avg = fields.Float(string='人均产量', readonly=True),
    fworkcenterno_count = fields.Float(string='工位数', readonly=True),
    fworkcenterno_avg = fields.Float(string='工位平均产能', readonly=True),
    rqty = fields.Float(string='Remade Quantity Sum', readonly=True),
    date_ascription = fields.Date(string='Date_Ascription', readonly=True)
    

    @api.one
    def _compute_rate(self):
        if self.gqty & self.sqty:
            self.rate = self.sqty / (self.gqty + self.sqty)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'ck_operation_productivity_rep')
        tools.drop_view_if_exists(self._cr, 'ck_operation_productivity_rep_ext')
        '''
        cr.execute("""
                create or replace view ck_operation_productivity_rep as
                select froutingname, fopername,foperno, sum(gqty) gqty_sum, sum(sqty) sqty_sum, sum(rqty) rqty_sum, 
                (sum(sqty) / (sum(gqty) + sum(sqty) + sum(rqty))) * 100 srate, 
                (sum(gqty) / (sum(gqty) + sum(sqty) + sum(rqty))) * 100 grate,
                (sum(rqty) / (sum(gqty) + sum(sqty) + sum(rqty))) * 100 rrate,
                count(distinct user_id) rep_num, sum(gqty) / count(distinct user_id) pavg_out,
                count(distinct fworkcentername) workcenter_num, sum(gqty) / count(distinct fworkcentername) wavg_out,
                date_ascription,
                row_number() over() id
                from ck_hours_worker_rep_four
                group by date_ascription, froutingname, fopername, foperno""")
        '''
        self._cr.execute("""
            CREATE OR REPLACE VIEW ck_operation_productivity_rep_ext AS
              SELECT ck_routing_sync.froutingname,
                ck_hours_worker.fopername,
                ck_hours_worker.foperno,
                sum(ck_hours_worker_line.gqty) AS gqty,
                sum(ck_hours_worker_line.sqty) AS sqty,
                sum(ck_hours_worker_line.rqty) AS rqty,
                COUNT(DISTINCT ck_hours_worker.create_uid) uid_count,
                COUNT(DISTINCT ck_hours_worker.fworkcenterno) fworkcenterno_count,
                date(
                    CASE
                        WHEN ((date_part('hour'::text, ck_hours_worker_line.date_worker) >= (0)::double precision) AND (date_part('hour'::text, ck_hours_worker_line.date_worker) < (12)::double precision) AND ((ck_hours_worker_line.fshift)::text = 'night'::text)) THEN (ck_hours_worker_line.date_worker - '1 day'::interval)
                        ELSE ck_hours_worker_line.date_worker
                    END) AS date_ascription
               FROM ((ck_hours_worker_line
                 LEFT JOIN ck_hours_worker ON ((ck_hours_worker_line.order_id = ck_hours_worker.id)))
                 LEFT JOIN ck_routing_sync ON (((ck_hours_worker.fworkcenterno)::text = (ck_routing_sync.fworkcenterno)::text)))
              WHERE ((ck_hours_worker_line.state)::text = 'done'::text)
              GROUP BY ck_routing_sync.froutingname, ck_hours_worker.fopername, ck_hours_worker.foperno, (date(
                    CASE
                        WHEN ((date_part('hour'::text, ck_hours_worker_line.date_worker) >= (0)::double precision) AND (date_part('hour'::text, ck_hours_worker_line.date_worker) < (12)::double precision) AND ((ck_hours_worker_line.fshift)::text = 'night'::text)) THEN (ck_hours_worker_line.date_worker - '1 day'::interval)
                        ELSE ck_hours_worker_line.date_worker
                    END));
        """)
        self._cr.execute("""
                create or replace view ck_operation_productivity_rep as
                    select
                   concat(date_ascription,froutingname,fopername,gqty) id,
                   (ck_operation_productivity_rep_ext.gqty/(ck_operation_productivity_rep_ext.gqty + 
                   ck_operation_productivity_rep_ext.sqty))*100 grate,
                   (ck_operation_productivity_rep_ext.sqty/(ck_operation_productivity_rep_ext.gqty + 
                   ck_operation_productivity_rep_ext.sqty))*100 srate,
                   (ck_operation_productivity_rep_ext.gqty/uid_count) uid_avg,
                   (ck_operation_productivity_rep_ext.gqty/fworkcenterno_count) fworkcenterno_avg,
                   ck_operation_productivity_rep_ext.*
                    from ck_operation_productivity_rep_ext
                    
        """)


class ck_daily_income_rep(models.Model):
    _name = 'ck.daily.income.rep'
    _description = 'CK Daily Income Report'
    _auto = False

    real_name = fields.Char(string='Worker Name', readonly=True),
    # 'fmodel': fields.Char(string='Product Model'), readonly=True),
    gqty = fields.Float(string='Good Quantity Sum', readonly=True),
    amount = fields.Float(string='Amount Sum', readonly=True),
    froutingname = fields.Char(string='Routing Name', readonly=True),
    fopername = fields.Char(string='Operation Name', readonly=True),
    foperno = fields.Char(string='Operation No', readonly=True),
    date_ascription = fields.Date(string='Date_Ascription', readonly=True)


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'ck_daily_income_rep')
        tools.drop_view_if_exists(self._cr, 'ck_daily_income_rep_ext')
        '''
        cr.execute("""
        create or replace view ck_daily_income_rep as
        SELECT real_name, fmodel, sum(gqty) gqty_sum, sum(amount) amount_sum, froutingname, fopername, date_ascription,
              row_number() over() id
	    from ck_hours_worker_rep_four
	    GROUP BY date_ascription, real_name, froutingname, fopername, fmodel""")
	    '''
        self._cr.execute("""
        create or replace view ck_daily_income_rep_ext as
            select
            res_partner."name" real_name,
                    date(case when extract(hour from ck_hours_worker_line."date_worker") >= 0 and extract(hour from ck_hours_worker_line."date_worker") < 12 and fshift='night'
                    then date_worker - INTERVAL'1day'
                    else date_worker end) date_ascription,
                     ck_hours_worker."fopername",ck_hours_worker."foperno", ck_routing_sync."froutingname",
                    sum(ck_hours_worker_line."gqty") gqty,  sum(ck_hours_worker_line."amount") amount
                    from ck_hours_worker_line
                    left join ck_hours_worker on ck_hours_worker_line.order_id = ck_hours_worker."id"
                    left join ck_icmo_sync on ck_icmo_sync."id" = ck_hours_worker.production_id
                    left join res_users on res_users.id = ck_hours_worker_line.user_id
                    left join res_partner on res_partner."id" = res_users.partner_id
                    left join ck_routing_sync on ck_hours_worker.fworkcenterno = ck_routing_sync.fworkcenterno
                    where ck_hours_worker_line.state = 'done'
                    group by ck_hours_worker.foperno , ck_hours_worker.fopername,date_ascription,real_name,ck_routing_sync.froutingname
                    ORDER BY  convert_to(res_partner.name, 'GBK'),date_ascription desc
          """)
        self._cr.execute("""
        create or replace view ck_daily_income_rep as
            select
                   concat(date_ascription,real_name,gqty) id,
                   ck_daily_income_rep_ext.*
                    from ck_daily_income_rep_ext
          """)


class ck_daily_scrap_rep(models.Model):
    _name = 'ck.daily.scrap.rep'
    _description = 'CK Daily Scrap Report'
    _auto = False

    date_worker = fields.Date(string='Date Worker', readonly=True),
    fworkcentername = fields.Char(string='Work Center Name', readonly=True),
    fshift = fields.Char(string='Shift', readonly=True),
    fmodel = fields.Char(string='Model', readonly=True),
    gqty = fields.Char(string='Good Quantity', readonly=True),
    qty = fields.Char(string='Scrap Quantity', readonly=True),
    reason = fields.Char(string='Scrap Reason', readonly=True)


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'ck_daily_scrap_rep')
        self._cr.execute("""
        create or replace view ck_daily_scrap_rep as
        SELECT ck_route_scrap_reasons_line.id id,
        date(ck_route_scrap_reasons_line.create_date) date_worker,
        ck_hours_worker.fworkcentername,
        ck_hours_worker_line.fshift, ck_icmo_sync.fmodel, ck_hours_worker_line.gqty, 
        ck_route_scrap_reasons_line.qty, ck_route_scrap_reasons_line.reason
        from ck_route_scrap_reasons_line
        left join ck_hours_worker_line on ck_hours_worker_line."id" = ck_route_scrap_reasons_line.order_id
        left join ck_hours_worker on ck_hours_worker."id" = ck_hours_worker_line.order_id
        left join ck_icmo_sync on ck_icmo_sync.id = ck_hours_worker.production_id
        """)

class ck_work_order_production_rep(models.Model):
    _name = 'ck.work.order.production.rep'
    _description = 'CK Work Order Production Report'
    _auto = False

    name = fields.Char(string='Worder Order Name',readonly=True),
    froutingname = fields.Char(string='Routing Name', readonly=True),
    fopername = fields.Char(string='Operation Name', readonly=True),
    gqty = fields.Float(string='Good Quantity', readonly=True),
    date_ascription = fields.Date(string='Date Ascription', readonly=True)


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'ck_work_order_production_rep')
        self._cr.execute(""" 
            create or replace view ck_work_order_production_rep as
            select ck_hours_worker_line."id", ck_icmo_sync."name",
            ck_routing_sync."froutingname", ck_hours_worker."fopername", ck_hours_worker_line."gqty",
            ck_hours_worker_line."date_worker", ck_hours_worker_line."fshift",
            date(case when extract(hour from ck_hours_worker_line."date_worker") >= 0 and extract(hour from ck_hours_worker_line."date_worker") < 12 and fshift='night' 
            then date_worker - INTERVAL'1day'
            else date_worker end) date_ascription
            from ck_hours_worker_line
            left join ck_hours_worker on ck_hours_worker_line.order_id = ck_hours_worker."id"
            left join ck_routing_sync on ck_hours_worker.foperno = ck_routing_sync.foperno and ck_hours_worker.fworkcentername = ck_routing_sync.fworkcentername
            left join ck_icmo_sync on ck_icmo_sync."id" = ck_hours_worker.production_id
            where ck_hours_worker_line.state = 'done'
            """)