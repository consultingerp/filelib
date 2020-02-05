from odoo import fields, models, api
from odoo import tools, _
import odoo.addons.decimal_precision as dp


class ck_working_summary_report(models.Model):
    _name = 'ck.working.summary.report'
    _description = 'CK Working Summary Report'
    _auto = False

    name = fields.Char(string='Production Number', readonly=True),
    fname = fields.Char(string='Product Dsescription', readonly=True),
    fnumber = fields.Char(string='Product No', readonly=True),
    fmodel = fields.Char(string='Product Model', readonly=True),
    gqty = fields.Float(string='Good Quantity Total', readonly=True),
    amount_total = fields.Float(string='Amount Total', readonly=True),
    date_worker = fields.Char(string='Working Day', readonly=True),

    def init(self):
        tools.drop_view_if_exists(self._cr, 'ck_working_summary_report')
        self._cr.execute("""
        create or replace view ck_working_summary_report as
        SELECT ck_hours_worker.id AS id, ck_icmo_sync.name,ck_icmo_sync.fmodel,ck_hours_worker.fname,ck_hours_worker.fnumber,ck_hours_worker_line.date_worker, ck_hours_worker.gqty,ck_hours_worker.amount_total
        from ck_hours_worker
	    left join ck_icmo_sync on ck_icmo_sync."id"=ck_hours_worker.production_id
	    left join ck_hours_worker_line on ck_hours_worker_line.order_id = ck_hours_worker."id" """)


class ck_date_summary_report(models.Model):
    _name = 'ck.date.summary.report'
    _description = 'CK Date Summary Report'
    _auto = False
    
    name = fields.Char(string='User', readonly=True),
    fname = fields.Char(string='Product No', readonly=True),
    year_worker = fields.Char(string='Working Year', readonly=True),
    month_worker = fields.Char(string='Working Month', readonly=True),
    day_worker = fields.Char(string='Working Day', readonly=True),
    gqty_sum = fields.Float(string='Good Quantity Total', readonly=True),
    amount_total = fields.Float(string='Amount Total', readonly=True),

    def init(self):
        tools.drop_view_if_exists(self._cr, 'ck_date_summary_report')
        self._cr.execute("""
                create or replace view ck_date_summary_report as
                SELECT ck_hours_worker_line.id as id, res_partner.name,ck_hours_worker.fname, 
                date_part('year',ck_hours_worker_line.date_worker) as year_worker,date_part('month',ck_hours_worker_line.date_worker) as month_worker,date_part('DAY',ck_hours_worker_line.date_worker) as day_worker,
                sum(ck_hours_worker.gqty) gqty_sum, sum(ck_hours_worker.amount_total) amount_total
                  from ck_hours_worker_line
		left join ck_hours_worker on ck_hours_worker_line.order_id = ck_hours_worker."id"
	    left join res_users on res_users.id = ck_hours_worker_line.user_id
        left join res_partner on res_partner."id" = res_users.partner_id
        GROUP BY  ck_hours_worker_line.id,res_partner.name,ck_hours_worker.fname,date_part('year',ck_hours_worker_line.date_worker),date_part('month',ck_hours_worker_line.date_worker),date_part('DAY',ck_hours_worker_line.date_worker)
        ORDER BY  convert_to(res_partner.name, 'GBK') """)


class ck_unfinished_accessary_form(models.Model):
    _name = 'ck.unfinished.accessary.form'
    _description = 'CK Unfinished Accessary Form'
    _auto = False
    
    name = fields.Char(string='Production Number', readonly=True),
    create_date = fields.Char(string='Create date', readonly=True),
    fmodel = fields.Char(string='Product Model', readonly=True),
    fname = fields.Char(string='Production name', readonly=True),
    fopername = fields.Char(string='Operation name', readonly=True),
    sum_gqty = fields.Float(string='Good Quantity Total', readonly=True),


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'ck_unfinished_accessary_form')
        self._cr.execute("""
            create or replace view ck_unfinished_accessary_form as
           SELECT ck_hours_worker.id AS id, ck_icmo_sync.name,ck_icmo_sync.create_date,ck_icmo_sync.fmodel,ck_hours_worker.fname, ck_hours_worker.fopername, sum(ck_hours_worker.gqty) sum_gqty
            from ck_hours_worker
            LEFT JOIN ck_icmo_sync on ck_icmo_sync."id"=ck_hours_worker.production_id
            GROUP BY ck_hours_worker.id,ck_icmo_sync.name,ck_icmo_sync.create_date,ck_icmo_sync.fmodel,ck_hours_worker.fname,ck_hours_worker.fopername""")


class ck_unfinished_summary_report(models.Model):
    _name = 'ck.unfinished.summary.report'
    _description = 'CK Unfinished Summary Report'
    _auto = False
    
    name = fields.Char(string='Production Number', readonly=True),
    create_date = fields.Char(string='Create date', readonly=True),
    fmodel = fields.Char(string='Product Model', readonly=True),
    fname = fields.Char(string='Production name', readonly=True),
    fopername = fields.Char(string='Operation name', readonly=True),
    sum_gqty = fields.Float(string='Good Quantity Total', readonly=True),
    unfinished = fields.Float(string='unfinished Quantity', readonly=True),


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'ck_unfinished_summary_report')
        self._cr.execute("""
            create or replace view ck_unfinished_summary_report as
            select ck_unfinished_accessary_form.*, (1+rate.attrition_rate)*ck_icmo_sync.fqty-ck_unfinished_accessary_form.sum_gqty unfinished from ck_unfinished_accessary_form 
            left join ck_icmo_sync on ck_unfinished_accessary_form."name"=ck_icmo_sync."name"
	        left join (select DISTINCT attrition_rate,fmodel from ck_attrition_rate )  rate on ck_unfinished_accessary_form."fmodel"=rate."fmodel" """)


class ck_work_unfinished_accessary_form(models.Model):
    _name = 'ck.work.unfinished.accessary.form'
    _description = 'CK Work Unfinished Accessary Form'
    _auto = False
    
    fname = fields.Char(string='Production name', readonly=True),
    date_worker = fields.Char(string='Working Day', readonly=True),
    fnumber = fields.Char(string='Product No', readonly=True),
    fmodel = fields.Char(string='Product Model', readonly=True),
    name = fields.Char(string='Production Number', readonly=True),
    fopername = fields.Char(string='Operation name', readonly=True),
    sum_gqty = fields.Float(string='Good Quantity Total', readonly=True),


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'ck_work_unfinished_accessary_form')
        self._cr.execute("""
                create or replace view ck_work_unfinished_accessary_form as
               SELECT ck_hours_worker.id AS id, ck_hours_worker.fname,cast(ck_hours_worker_line.date_worker as DATE),
               ck_hours_worker.fnumber,ck_icmo_sync.fmodel,ck_icmo_sync.name, ck_hours_worker.fopername, sum(ck_hours_worker.gqty) sum_gqty
                from ck_hours_worker
                LEFT JOIN ck_icmo_sync on ck_icmo_sync."id"=ck_hours_worker.production_id
              left join ck_hours_worker_line on ck_hours_worker_line.order_id = ck_hours_worker."id"  
              GROUP BY ck_hours_worker.id,ck_icmo_sync.name,cast(ck_hours_worker_line.date_worker as DATE),
              ck_icmo_sync.fmodel,ck_hours_worker.fnumber,ck_hours_worker.fname, ck_hours_worker.fopername """)


class ck_work_unfinished_summary_report(models.Model):
    _name = 'ck.work.unfinished.summary.report'
    _description = 'CK Work Unfinished Summary Report'
    _auto = False
    
    fname = fields.Char(string='Production name', readonly=True),
    date_worker = fields.Char(string='Working Day', readonly=True),
    fnumber = fields.Char(string='Product No', readonly=True),
    fmodel = fields.Char(string='Product Model', readonly=True),
    name = fields.Char(string='Production Number', readonly=True),
    fopername = fields.Char(string='Operation name', readonly=True),
    gqty = fields.Float(string='Good Quantity', readonly=True),
    sum_gqty = fields.Float(string='Good Quantity Total', readonly=True),
    unfinished = fields.Float(string='unfinished Quantity', readonly=True),


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'ck_work_unfinished_summary_report')
        self._cr.execute("""
        create or replace view ck_work_unfinished_summary_report as
        SELECT ck_work_unfinished_accessary_form.*,ck_hours_worker_line.gqty,(1+rate.attrition_rate)*ck_icmo_sync.fqty-ck_work_unfinished_accessary_form.sum_gqty unfinished 
	    from ck_work_unfinished_accessary_form
	    left join ck_hours_worker_line on ck_hours_worker_line.order_id = ck_work_unfinished_accessary_form."id"  
        left join ck_icmo_sync on ck_work_unfinished_accessary_form."name"=ck_icmo_sync."name"
	    left join (select DISTINCT attrition_rate,fmodel from ck_attrition_rate )  rate on ck_work_unfinished_accessary_form."fmodel"=rate."fmodel"
		where ck_hours_worker_line.state='done'""")
