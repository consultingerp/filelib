# -*- coding: utf-8 -*-

import logging
from odoo import models, osv, fields, exceptions, api, _

import datetime
import time

import pytz

import odoo.addons.decimal_precision as dp

DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d"
_logger = logging.getLogger(__name__)


class CK_ICNO_Opra(models.Model):
    _name = 'ck.icno.opra'
    _description = _("Production Opration")
    _order = "company_id, production_id, foperno"
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.users'].browse(self._uid).company_id.id
                                 )  # 公司
    production_id = fields.Many2one(comodel_name='ck.icmo.sync', string=_('ProductionOrder'),
                                    readonly=False)  # 用户ID
    foperno = fields.Char(string=_('OperationNo'))  # 工序编码
    pqty = fields.Float(compute='_compute_qty', string=_('Picking Quantity'),
                        default=0, store=True)  # 已发料数量
    _sql_constraints = [
        ("production_opration_unique", "unique(company_id,production_id,foperno)", _("Duplicated ProductionOp"))
    ]

    @api.one
    @api.depends('production_id')
    def _compute_qty(self):

        pqty = 0
        self._cr.execute('select id,pqty,foperno from ck_hours_worker where production_id =%s and foperno = %s and state != %s', (self.production_id.id, self.foperno, 'del',))
        hw_ids = self._cr.fetchall()
        if self.foperno and self.production_id and hw_ids:
            for hw in hw_ids:
                if hw[2] == self.foperno:
                    pqty += hw[1]
        self.pqty = pqty


class CK_ICMO_Sync(models.Model):
    _name = 'ck.icmo.sync'
    _description = _("Production Order Sync")
    _order = "company_id,name"

    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.users'].browse(self._uid).company_id.id
                                 )  # 公司
    finterid = fields.Integer(string=_('ProductionOrderID'), required=True)  # '生产任务单ID'
    name = fields.Char(string=_('ProductionNo'), index=True)  # '生产任务单号'
    fitemid = fields.Integer(string=_('ProductID'), required=True)  # '产品ID'
    fnumber = fields.Char(string=_('ProductNo'))  # 产品编码（长）
    fname = fields.Char(string=_('ProductDesc'))  # 产品描述
    fmodel = fields.Char(string=_('ProductModel'))  # 产品规格
    fqty = fields.Float(string=_('Quantity'))  # 订单数量
    # pqty        = fields.Float(compute='_compute_qty', string=_('Picking Quantity'),
    #                           default=0, store=True)                                     # 已报工数量
    funit = fields.Char(string=_('Unit'))  # 产品单位
    froutingid = fields.Integer(string=_('RoutingID'))  # 工艺路线ID
    froutingno = fields.Char(string=_('RoutingNo'))  # 工艺编码
    forderinterid = fields.Integer(string=_('SaleOrderID'))  # 销售订单ID
    fsourceentryid = fields.Integer(string=_('SaleItemID'))  # 销售订单行ID
    seobillno = fields.Char(string=_('SaleOrderNo'))  # 销售订单号
    fcustid = fields.Integer(string=_('CustmerID'))  # 客户ID
    fcustno = fields.Char(string=_('CustmerNo'))  # 客户编号
    fnote = fields.Char(string=_('CustomerNote'))  # 客户备注
    fdate = fields.Datetime(string=_('DeliveryDate'))  # 产品交期
    fconfirmdate = fields.Datetime(string=_('UpdateDate'))  # 更新时间
    hw_ids = fields.One2many('ck.hours.worker', 'production_id', string='Hours Worker Lines',
                             readonly=True, copy=True, domain=[('state', '!=', 'del')])  # 报工单
    state = fields.Selection(
        [('new', _('New')), ('update', _('Update')), ('run', _('Running')), ('done', _('Done'))], _('State'), readonly=False, default='new')  # 状态
    _sql_constraints = [
        ("fbillno_unique", "unique(company_id,name)", _("Duplicated ProductionNo"))
    ]
    '''
    @api.one
    def _compute_qty(self):
        pqty = 0
        if self.finterid :
            for hw in self.hw_ids:
                pqty += hw.pqty
        self.pqty=pqty
    '''

    @api.multi
    def write(self, vals):
        if vals.get('finterid', False):
            record = self.search([('finterid', '=', vals.get('finterid'))])
            if len(record) > 0 and record.state != 'new':
                return True
        else:
            vals.update({'state': 'update'})

        return super(CK_ICMO_Sync, self).write(vals)

    @api.multi
    def button_hw_confirms(self):
        for hw in self.hw_ids:
            if hw.state != 'done':
                for line in hw.lines:
                    if line.state != 'done':
                        line.state = 'done'
                hw.uflag = not hw.uflag
                hw.check_complete()
        return True


class CK_Routing_Sync(models.Model):
    _name = 'ck.routing.sync'
    _description = _("Routing Sync")
    _order = "company_id, froutingid, fopersn, fworkcenterid "

    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.users'].browse(self._uid).company_id.id
                                 )  # 公司
    froutingid = fields.Integer(string=_('RoutingID'))  # 工艺路线ID
    # fitemid =  fields.Integer(string=_('ProductID'), required=True)                           # 产品ID
    foperid = fields.Integer(string=_('OperationID'))  # 工序ID
    fworkcenterid = fields.Integer(string=_('WorkCenterID'))  # 工作中心ID
    froutingno = fields.Char(string=_('RoutingNo'))  # 工艺编码
    froutingname = fields.Char(string=_('RoutingName'))  # 工艺名称
    # fnumber =  fields.Char(string=_('ProductNo'))                                              # 产品编码（长）
    # fname =  fields.Char(string=_('ProductDesc'))                                             # 产品描述
    fopersn = fields.Integer(string=_('OperationSN'))  # 工序序号
    foperno = fields.Char(string=_('OperationNo'), index=True)  # 工序编码
    fopername = fields.Char(string=_('OperationName'))  # 工序名称
    fworkcenterno = fields.Char(string=_('WorkCenterNo'), index=True)  # 工作中心编码
    fworkcentername = fields.Char(string=_('WorkCenterName'))  # 工作中心名称
    routing_key = fields.Char(string="Key")
    if_needrqty = fields.Boolean(string="If Need Input Repair Number")  # 是否需要返修排插数
    if_need_manypeoplereport = fields.Boolean(string="If Need Many People Report")  # 是否需要报多人


class CK_Price(models.Model):
    _name = 'ck.price'
    _description = _("Work Price")
    _order = "company_id, fitemid, froutingno, foperno"

    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.users'].browse(self._uid).company_id.id
                                 )  # 公司
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency',
                                  related="company_id.currency_id")  # 币别
    fitemid = fields.Integer(string=_('ProductID'), required=True)  # 产品ID
    fnumber = fields.Char(string=_('ProductNo'))  # 产品编码（长）
    fname = fields.Char(string=_('ProductDesc'))  # 产品描述
    froutingid = fields.Integer(string=_('RoutingID'))  # 工艺路线ID
    froutingno = fields.Char(string=_('RoutingNo'))  # 工艺编码
    froutingname = fields.Char(string=_('RoutingName'))  # 工艺名称
    foperid = fields.Integer(string=_('OperationID'))  # 工序ID
    foperno = fields.Char(string=_('OperationNo'))  # 工序编码
    fopername = fields.Char(string=_('OperationName'))  # 工序名称
    funit = fields.Char(string=_('Unit'), required=True, default='PCS')  # 产品单位
    fqty = fields.Float(string=_('Quantity'))  # 任务单数量
    fprice = fields.Float(digits=dp.get_precision('ck_workprice_digit'), string=_('WorkPrice'))  # 价格
    date_start = fields.Date('Valid From', default=fields.Date.today())  # 生效开始日期
    date_stop = fields.Date('Valid Until', default=fields.Date.from_string('9999-12-31'))  # 生效结束日期

    @api.one
    @api.onchange('fitemid')
    def change_fitemid(self):
        if self.fitemid:
            foper_ids = self.env['ck.icmo.sync'].search([('fitemid', '=', self.fitemid)], limit=1)
            if any(foper_ids):
                self.fnumber = foper_ids[0].fnumber
                self.fname = foper_ids[0].fname

    @api.one
    @api.onchange('fnumber')
    def change_fnumber(self):
        if self.fnumber:
            foper_ids = self.env['ck.icmo.sync'].search([('fnumber', '=', self.fnumber)], limit=1)
            if any(foper_ids):
                self.fitemid = foper_ids[0].fitemid
                self.fname = foper_ids[0].fname

    @api.one
    @api.onchange('foperno')
    def change_foperno(self):
        if self.foperno:
            foper_ids = self.env['ck.routing.sync'].search([('foperno', '=', self.foperno)], limit=1)
            if any(foper_ids):
                self.fopername = foper_ids[0].fopername
                self.foperid = foper_ids[0].foperid

    @api.one
    @api.onchange('foperid')
    def change_foperid(self):
        if self.foperid:
            foper_ids = self.env['ck.routing.sync'].search([('foperid', '=', self.foperid)], limit=1)
            if any(foper_ids):
                self.fopername = foper_ids[0].fopername
                self.foperno = foper_ids[0].foperno

    @api.one
    @api.onchange('froutingno')
    def change_froutingno(self):
        if self.froutingno:
            foper_ids = self.env['ck.routing.sync'].search([('froutingno', '=', self.froutingno)], limit=1)
            if any(foper_ids):
                self.froutingname = foper_ids[0].froutingname
                self.froutingid = foper_ids[0].froutingid

    @api.one
    @api.onchange('froutingid')
    def change_froutingid(self):
        if self.froutingid:
            foper_ids = self.env['ck.routing.sync'].search([('froutingid', '=', self.froutingid)], limit=1)
            if any(foper_ids):
                self.froutingname = foper_ids[0].froutingname
                self.froutingno = foper_ids[0].froutingno


class CK_Hours_Worker(models.Model):
    _name = 'ck.hours.worker'
    _description = _("Hours of Worker")
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "company_id, production_id, user_id, foperno"
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.users'].browse(self._uid).company_id.id
                                 )  # 公司
    name = fields.Char('Order Reference', required=True, copy=False, readonly=False,
                       select=True, default=lambda obj: '/', )  # 报工单
    user_id = fields.Many2one(comodel_name='res.users', string=_('Owner'), readonly=False, index=True)  # 用户ID
    production_id = fields.Many2one(comodel_name='ck.icmo.sync', string=_('ProductionOrder'),
                                    readonly=False, index=True)  # 用户ID

    # 'finterid =  fields.Integer(string=_('ProductionOrderID'), required=True),  # '生产任务单ID'
    # 'fbillno =  fields.Char(string=_('ProductionNo')),  # '生产任务单号'
    # 'fworkcenterid =  fields.Integer(string=_('WorkCenterID')),  # 工作中心ID
    fnumber = fields.Char(string=_('ProductNo'))  # 产品编码（长）
    fname = fields.Char(string=_('ProductDesc'))  # 产品描述
    fworkcenterno = fields.Char(string=_('WorkCenterNo'), index=True)  # 工作中心编码
    fworkcentername = fields.Char(string=_('WorkCenterName'))  # 工作中心名称
    # 'foperid =  fields.Integer(string=_('OperationID')),  # 工序ID
    foperno = fields.Char(string=_('OperationNo'), index=True)  # 工序编码
    fopername = fields.Char(string=_('OperationName'))  # 工序名称

    date_start = fields.Datetime(string=_('Valid From'), default=lambda self: fields.datetime.now())  # 开始时间
    date_stop = fields.Datetime(string=_('Valid Until'))  # 结束时间
    pqty = fields.Float(string=_('Picking Quantity'))  # 发料数量
    sqty = fields.Float(compute='_compute_qty', string=_('Scrap Quantity'), store=True)  # 总报废数量
    gqty = fields.Float(compute='_compute_qty', string=_('Good Quantity'), store=True)  # 总良品数量
    price = fields.Float(compute='_compute_qty', string=_('Price'), digits=dp.get_precision('ck_workprice_digit')
                         , store=True)  # 平均单价
    amount_total = fields.Float(compute='_compute_qty', string=_('Total'), digits=dp.get_precision('ck_workprice_digit')
                                , store=True)  # 总工费
    lines = fields.One2many('ck.hours.worker.line', 'order_id', string='Hours Worker Lines',
                            readonly=False, copy=True, domain=[('state', '!=', 'del')], auto_join=True)  # 报工明细
    state = fields.Selection(
        [('open', _('Open')), ('done', _('Done')), ('del', _('Delete'))], _('State'), readonly=False, default='open')  # 状态
    uflag = fields.Boolean(string=_('update qty flag'), default=False)  # 更新标志

    department = fields.Char(compute='_compute_department', string=_('部门'))
    rqty = fields.Float(string=_('Remade Quantity'), default=0)  # 插排数量

    def _search_department(self, opeartor, value):
        employees = self.env['hr.employee'].search(['|', ('department_id', opeartor, value), ('department_id.parent_id', opeartor, value)])
        ids = [employee.user_id.id for employee in employees]
        return [('user_id', 'in', ids)]

    @api.one
    @api.depends('user_id', 'state')
    def _compute_department(self):
        if self.user_id.employee_ids:
            self.department = self.user_id.employee_ids[0].department_id.complete_name

    @api.one
    @api.depends('uflag')
    def _compute_qty(self):
        if len(self.lines) > 0:
            gqty = 0
            sqty = 0
            amount_total = 0
            rqty = 0
            complete = True
            for line in self.lines:
                gqty += line.gqty
                sqty += line.sqty
                rqty += line.rqty
                amount_total += line.amount or 0
                if line.state == 'new':
                    complete = False
            amount_qty = gqty + sqty + rqty
            if self.pqty <= amount_qty and self.pqty > 0 and complete:
                price = amount_total / amount_qty if amount_qty > 0 else 0
                self.gqty = gqty
                self.sqty = sqty
                self.rqty = rqty
                self.price = price
                self.amount_total = amount_total
            else:
                self.gqty = gqty
                self.sqty = sqty
                self.rqty = rqty

    @api.multi
    def check_complete(self):
        if self.amount_total > 0:
            # self.date_stop = lambda self: fields.datetime.now())
            self.date_stop = fields.datetime.now()
            self.state = 'done'

    @api.multi
    def check_number(self):
        totalgqty = 0
        totalsqty = 0
        totalprice = 0
        totalamount = 0
        for line in self.lines:
            if line.state != 'del':
                totalgqty += line.gqty
                totalsqty += line.sqty
                totalamount += line.amount
                totalprice = line.price
        self.gqty = totalgqty
        self.sqty = totalsqty
        self.price = totalprice
        self.amount_total = totalamount

    @api.multi
    def button_confirms(self):
        for line in self.lines:
            if line.state != 'done':
                line.state = 'done'
        self.uflag = not self.uflag
        self.check_complete()
        return True

    @api.model
    def create(self, vals):
        if vals.get('user_id', False) == False:
            vals['user_id'] = self._uid
        if vals.get('production_id', False) != False and \
                (vals.get('fnumber', False) == False or vals.get('fname', False) == False):
            production_id = self.env['ck.icmo.sync'].browse([vals['production_id']])
            vals['fnumber'] = production_id.fnumber
            vals['fname'] = production_id.fname
        if vals.get('fworkcentername', False) != False and vals.get('fworkcenterno', False) == True:
            foper_ids = self.env['ck.routing.sync'].search([('fworkcenterno', '=', vals['fworkcenterno'])], limit=1)
            if any(foper_ids):
                vals['fworkcentername'] = foper_ids[0].fworkcentername
        if vals.get('fopername', False) != False and vals.get('foperno', False) == True:
            foper_ids = self.env['ck.routing.sync'].search([('foperno', '=', vals['foperno'])], limit=1)
            if any(foper_ids):
                vals['fopername'] = foper_ids[0].fopername
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('ck.hours.worker') or '/'
        import_flag = self.env.context.get('batch_import', False)
        if vals.get('batch_import', False):
            if not import_flag:
                self = self.with_context(batch_import=True)
            import_flag = True
            vals.pop('batch_import')
        new_id = super(CK_Hours_Worker, self).create(vals)
        if import_flag == False:
            totalpqty = new_id.pqty

            self._cr.execute('select id,pqty,foperno  from ck_hours_worker where production_id =%s and state != %s and foperno = %s',
                             (new_id.production_id.id, 'del', new_id.foperno,))

            hw_ids = self._cr.fetchall()

            for line in hw_ids:
                if new_id.id != line[0]:
                    totalpqty = totalpqty + line[1]

            attrition_rate = self.env['ck.attrition.rate'].search([
                ('fnumber', '=', new_id.production_id.fnumber)], limit=1)

            if not attrition_rate:
                attrition_rate = self.env['ck.attrition.rate'].search([
                    ('fmodel', '=', new_id.production_id.fmodel)], limit=1)
            attrition_rate_no = 0
            if attrition_rate:
                attrition_rate_no = attrition_rate.attrition_rate

            if totalpqty > (new_id.production_id.fqty * (100 + attrition_rate_no * 100) / 100) and new_id.state != 'done':
                raise exceptions.Warning(_('Feeding quantity can not exceed work order quantity!'))

        if new_id and vals.get('production_id', False) != False and vals.get('foperno', False) != False:
            production_opra = self.env['ck.icno.opra'].search([('company_id', '=', new_id.company_id.id),
                                                               ('production_id', '=', new_id.production_id.id),
                                                               ('foperno', '=', new_id.foperno)], limit=1)
            if any(production_opra):
                production_opra._compute_qty()
            else:
                self.env['ck.icno.opra'].create(
                    {
                        'company_id': new_id.company_id.id,
                        'production_id': new_id.production_id.id,
                        'foperno': new_id.foperno
                    })
        return new_id

    def create_new(self, vals):
        head_vals = {}
        line_vals = {}
        # head
        head_vals['user_id'] = vals['user_id']
        head_vals['production_id'] = vals['production_id']
        head_vals['fworkcenterno'] = vals['fworkcenterno']
        head_vals['foperno'] = vals['foperno']
        head_vals['fopername'] = vals['fopername']
        head_vals['fworkcentername'] = vals['fworkcentername']
        head_vals['pqty'] = vals['pqty']
        order_id = self.create_new(head_vals)
        # line
        line_vals['user_id'] = vals['user_id']
        line_vals['order_id'] = order_id.id
        line_vals['state'] = vals['state']
        line_vals['sqty'] = vals['sqty']
        line_vals['gqty'] = vals['gqty']
        line_vals['rqty'] = vals['rqty']
        line_vals['fshift'] = vals['fshift']
        line_vals['fmachine'] = vals['fmachine']

        line_vals['production_id'] = vals['production_id']
        line_vals['fworkcenterno'] = vals['fworkcenterno']
        line_vals['foperno'] = vals['foperno']
        line_vals['fopername'] = vals['fopername']
        line_vals['fworkcentername'] = vals['fworkcentername']

        self.env['ck.hours.worker.line'].create(line_vals)

    @api.multi
    def write(self, vals):
        _logger.debug("zhoufeng:  call write start : %s" % (datetime.datetime.now()))
        import_flag = self.env.context.get('batch_import', False)
        if vals.get('batch_import', False):
            if not import_flag:
                self = self.with_context(batch_import=True)
            import_flag = True
            vals.pop('batch_import')
        flag = super(CK_Hours_Worker, self).write(vals)
        if import_flag == False:
            totalpqty = self.pqty

            self._cr.execute('select id,pqty,foperno from ck_hours_worker where production_id =%s and foperno = %s and state != %s',
                             (self.production_id.id, self.foperno, 'del',))

            hw_ids = self._cr.fetchall()

            for line in hw_ids:
                if self.id != line[0]:
                    totalpqty = totalpqty + line[1]

            attrition_rate = self.env['ck.attrition.rate'].search([
                ('fnumber', '=', self.production_id.fnumber)], limit=1)

            if not attrition_rate:
                attrition_rate = self.env['ck.attrition.rate'].search([
                    ('fmodel', '=', self.production_id.fmodel)], limit=1)

            attrition_rate_no = 0
            if attrition_rate:
                attrition_rate_no = attrition_rate.attrition_rate

            if totalpqty > (self.production_id.fqty * (100 + attrition_rate_no * 100) / 100) and self.state != 'done':
                raise exceptions.Warning(_('Feeding quantity can not exceed work order quantity!'))

        production_opra = self.env['ck.icno.opra'].search([('company_id', '=', self.company_id.id),
                                                           ('production_id', '=', self.production_id.id),
                                                           ('foperno', '=', self.foperno)], limit=1)
        if any(production_opra):
            production_opra._compute_qty()
        else:
            self.env['ck.icno.opra'].create(
                {
                    'company_id': self.company_id.id,
                    'production_id': self.production_id.id,
                    'foperno': self.foperno
                })
        _logger.debug("zhoufeng:  call write end : %s" % (datetime.datetime.now()))
        return flag

    '''
    @api.multi
    def unlink(self):
        flag = False
        for line in self:
            production_opra = self.env['ck.icno.opra'].search([('company_id', '=', line.company_id.id),
                                                               ('production_id', '=', line.production_id.id),
                                                               ('foperno', '=', line.foperno)], limit=1)
            # flag = super(CK_Hours_Worker, line).unlink()
            line.state = 'del'
            for lineline in line.lines:
                lineline.state = 'del'
            if any(production_opra):
                production_opra._compute_qty()
        return True
    '''

    @api.one
    @api.onchange('production_id')
    def change_production_id(self):
        self.foperno = False
        self.fopername = False
        self.fworkcenterno = False
        self.fworkcentername = False
        self.fnumber = False
        self.fname = False
        self.pqty = 0
        if self.production_id:
            if not self.fnumber or not self.fname:
                self.fnumber = self.production_id.fnumber or False
                self.fname = self.production_id.fname or False
        if not self.user_id:
            self.usr_id = self.env.user

    @api.one
    @api.onchange('foperno')
    def change_foperno(self):
        self.fopername = False
        self.fworkcenterno = False
        self.fworkcentername = False
        self.pqty = 0
        if self.foperno:
            foper_ids = self.env['ck.routing.sync'].search([('foperno', '=', self.foperno)], limit=1)
            if any(foper_ids):
                self.fopername = foper_ids[0].fopername

    @api.one
    @api.onchange('fworkcenterno')
    def change_fworkcenterno(self):
        self.pqty = 0
        self.fworkcentername = False
        if self.fworkcenterno:
            foper_ids = self.env['ck.routing.sync'].search([('fworkcenterno', '=', self.fworkcenterno)], limit=1)
            if any(foper_ids):
                self.fworkcentername = foper_ids[0].fworkcentername
            if self.company_id and self.production_id and self.foperno:

                production_opra = self.env['ck.icno.opra'].search([('company_id', '=', self.company_id.id),
                                                                   ('production_id', '=', self.production_id.id),
                                                                   ('foperno', '=', self.foperno)], limit=1)

                attrition_rate = self.env['ck.attrition.rate'].search([
                    ('fnumber', '=', self.production_id.fnumber)], limit=1)

                if not attrition_rate:
                    attrition_rate = self.env['ck.attrition.rate'].search([
                        ('fmodel', '=', self.production_id.fmodel)], limit=1)

                attrition_rate_no = 0
                if attrition_rate:
                    attrition_rate_no = attrition_rate.attrition_rate

                if production_opra:
                    production_opra._compute_qty()
                    self.pqty = self.production_id.fqty * (1 + attrition_rate_no) - production_opra.pqty
                else:
                    self.pqty = self.production_id.fqty * (1 + attrition_rate_no)

    @api.multi
    def search_by_userid(self, start_date, end_date, name, fmodel):
        # start_date = '2017-06-15'
        # end_date = '2017-07-21'
        # name = '00'
        # fmodel = '0'
        domain = []
        if start_date:
            startdate = (datetime.datetime.strptime(start_date, '%Y-%m-%d')).replace(
                tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
            start_date = startdate.strftime('%Y-%m-%d %H:%M:%S')
            domain_start_date = ('date_worker', '>=', start_date)
            domain.append(domain_start_date)
        if end_date:
            enddate = (datetime.datetime.strptime(end_date, '%Y-%m-%d')).replace(
                tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
            end_date = enddate.strftime('%Y-%m-%d %H:%M:%S')
            domain_end_date = ('date_worker', '<', end_date)
            domain.append(domain_end_date)
        if name:
            domain_name = ('order_id.production_id.name', 'like', '%' + name + '%')
            domain.append(domain_name)
        if fmodel:
            domain_fmodel = ('order_id.production_id.fmodel', 'like', '%' + fmodel + '%')
            domain.append(domain_fmodel)
        domain.append(('state', '!=', 'del'))
        thisinfos = self.env['ck.hours.worker.line'].search(domain, order='id desc', limit=500)
        l = []
        data = []
        while len(thisinfos) > 0:
            thisinfo = thisinfos[:100]
            thisinfos = thisinfos - thisinfo
            if len(thisinfo) > 0:
                idstr_cond = str(thisinfo.mapped('id')).replace('[', '').replace(']', '')
                query_sql = '''
                                 select ck_hours_worker.user_id as user_id ,
                                   (select name from res_partner where id = (select partner_id from res_users where id =     ck_hours_worker.user_id limit 1) limit 1) as name ,
                                   ck_hours_worker.fworkcenterno,
                                   ck_icmo_sync.name as production_id_name,
                                   ck_icmo_sync.fnumber as production_id_fnumber,
                                   ck_icmo_sync.fname as production_id_fname,
                                   ck_icmo_sync.fmodel as production_id_fmodel,
                                   ck_icmo_sync.froutingno as production_id_froutingno,
                                   pqty,
                                   ck_icmo_sync.funit as production_id_funit,
                                   ck_icmo_sync.seobillno as production_id_seobillno,
                                   ck_icmo_sync.fcustno as production_id_fcustno,
                                   ck_icmo_sync.fnote as production_id_fnote,
                                   ck_icmo_sync.fdate as production_id_fdate,
                                   ck_routing_sync.froutingname as routing_froutingname,
                                   ck_routing_sync.fopername as routing_fopername,
                                   ck_routing_sync.fworkcentername as routing_fworkcentername,
                                   ck_routing_sync.if_needrqty as routing_if_needrqty,
                                   ck_routing_sync.if_need_manypeoplereport as routing_if_need_manypeoplereport,
                                   ck_hours_worker_line.gqty,
                                   ck_hours_worker_line.sqty,
                                   ck_hours_worker_line.price,
                                   ck_hours_worker_line.amount,
                                   ck_hours_worker_line.date_worker,
                                   ck_hours_worker_line.state,
                                   ck_hours_worker_line.fshift,
                                   ck_hours_worker_line.fmachine,
                                   ck_hours_worker_line.fpass,
                                   ck_hours_worker.name as order_id_name,
                                   ck_hours_worker_line.id,
                                   ck_hours_worker_line.rqty,
                                   ck_icmo_sync.fqty as production_id_fqty,
                                   ck_hours_worker_line.reportpeople
                                   from ck_hours_worker_line inner join ck_hours_worker on ck_hours_worker_line.order_id = ck_hours_worker.id
                                  inner join ck_icmo_sync on ck_hours_worker.production_id = ck_icmo_sync.id
                          left join ck_routing_sync on ck_routing_sync.fworkcenterno = ck_hours_worker.fworkcenterno and ck_routing_sync.foperno = ck_hours_worker.foperno
                          where ck_hours_worker_line.id in (%s)
                       ''' % (idstr_cond)
                self._cr.execute(query_sql)
                data = data + self._cr.fetchall()
                # for item in data:
                #     print item

            for line in data:
                thisinfo = line
                # for line in thisinfo.lines:
                ml = {}
                i = 0
                ml['userid'] = line[i] or ''
                i = i + 1
                ml['username'] = line[i] or ''
                i = i + 1
                ml['fworkcenterno'] = line[i] or ''  # 工作中心编码
                i = i + 1
                ml['production_name'] = line[i] or ''  # 生产任务单号
                i = i + 1
                ml['fnumber'] = line[i] or ''  # 产品编码
                i = i + 1
                ml['fname'] = line[i] or ''  # 产品描述
                i = i + 1
                ml['fmodel'] = line[i] or ''  # 产品型号
                i = i + 1
                ml['froutingno'] = line[i] or ''  # 工艺编码
                i = i + 1
                ml['fqty'] = line[i] or 0.0  # 数量
                i = i + 1
                ml['funit'] = line[i] or ''  # 单位
                i = i + 1
                ml['seobillno'] = line[i] or '' or ''  # 销售订单号
                i = i + 1
                ml['fcustno'] = line[i] or ''  # 客户编号
                i = i + 1
                ml['fnote'] = line[i] or ''  # 客户备注
                i = i + 1
                ml['fdate'] = line[i] or ''  # 产品交期
                i = i + 1

                # routing = self.env['ck.routing.sync'].search([('fworkcenterno', '=', thisinfo.fworkcenterno), ('foperno', '=', thisinfo.foperno)], limit=1)

                ml['froutingname'] = line[i] or ''  # 工艺名称
                i = i + 1
                ml['fopername'] = line[i] or ''  # 工序名称
                i = i + 1
                ml['fworkcentername'] = line[i] or ''  # 工作中心名称
                i = i + 1
                ml['if_needrqty'] = line[i] or False  # 是否需要插排数
                i = i + 1
                ml['if_need_manypeoplereport'] = line[i] or False  # 是否需报多人
                i = i + 1

                ml['gqty'] = line[i] or 0.0  # 良品数量
                i = i + 1
                ml['sqty'] = line[i] or 0.0  # 报废数量
                i = i + 1
                ml['price'] = line[i] or 0.0  # 工价
                i = i + 1
                ml['amount'] = line[i] or 0.0  # 金额
                i = i + 1
                date = line[i] or ''
                ml['date_worker'] = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).strftime(
                    '%Y-%m-%d')
                i = i + 1
                # ml['date_worker'] = datetime.datetime.strptime(line.date_worker, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).date() #报工时间
                # ml['date_worker']  = line.date_worker
                ml['date_worker'] = ml['date_worker'][0:10]  # 报工时间
                ml['state'] = line[i] or ''  # 报工时间
                i = i + 1

                ml['fshift'] = line[i] or ''  # 班次
                i = i + 1
                ml['fmachine'] = line[i] or ''  # 单双机
                i = i + 1
                ml['fpass'] = line[i] or ''  # 合格率
                i = i + 1

                ml['name'] = line[i] or ''  # 编号
                i = i + 1
                ml['id'] = line[i] or ''  # ID
                i = i + 1
                ml['rqty'] = line[i] or 0.0  # 插排数量
                i = i + 1
                ml['production_fqty'] = line[i] or 0.0  # 工单数量
                i = i + 1
                ml['reportpeople'] = line[i] or ''  # 多人报工人员备注
                l.append(ml)

            #     print l
            # print l
        return l

    @api.multi
    def search_by_useridcustomerdefault(self, start_date, end_date, name, fmodel, user_id, foperno):
        # start_date = '2017-06-15'
        # end_date = '2017-06-21'
        # startdate = (datetime.datetime.strptime(start_date, '%Y-%m-%d')).replace(tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
        # enddate = (datetime.datetime.strptime(end_date, '%Y-%m-%d')).replace(tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
        # start_date = startdate.strftime('%Y-%m-%d %H:%M:%S')
        # end_date =  enddate.strftime('%Y-%m-%d %H:%M:%S')

        domain = []
        if start_date:
            startdate = (datetime.datetime.strptime(start_date, '%Y-%m-%d')).replace(
                tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
            start_date = startdate.strftime('%Y-%m-%d %H:%M:%S')
            domain_start_date = ('date_worker', '>=', start_date)
            domain.append(domain_start_date)
        if end_date:
            enddate = (datetime.datetime.strptime(end_date, '%Y-%m-%d')).replace(
                tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
            end_date = enddate.strftime('%Y-%m-%d %H:%M:%S')
            domain_end_date = ('date_worker', '<', end_date)
            domain.append(domain_end_date)
        if name:
            domain_name = ('order_id.production_id.name', 'like', '%' + name + '%')
            domain.append(domain_name)
        if fmodel:
            domain_fmodel = ('order_id.production_id.fmodel', 'like', '%' + fmodel + '%')
            domain.append(domain_fmodel)
        if user_id:
            domain_user_id = ('user_id', '=', user_id)
            domain.append(domain_user_id)
        if foperno:
            domain_foperno = ('foperno', '=', foperno)
            domain.append(domain_foperno)

        domain.append(('state', '!=', 'del'))

        thisinfos = self.env['ck.hours.worker.line'].search(domain)
        l = []
        data = []
        while len(thisinfos) > 0:
            thisinfo = thisinfos[:100]
            thisinfos = thisinfos - thisinfo
            if len(thisinfo) > 0:
                idstr_cond = str(thisinfo.mapped('id')).replace('[', '').replace(']', '')
                query_sql = '''
                                 select ck_hours_worker.user_id as user_id ,
                                   (select name from res_partner where id = (select partner_id from res_users where id =     ck_hours_worker.user_id limit 1) limit 1) as name ,
                                   ck_hours_worker.fworkcenterno,
                                   ck_icmo_sync.name as production_id_name,
                                   ck_icmo_sync.fnumber as production_id_fnumber,
                                   ck_icmo_sync.fname as production_id_fname,
                                   ck_icmo_sync.fmodel as production_id_fmodel,
                                   ck_icmo_sync.froutingno as production_id_froutingno,
                                   pqty,
                                   ck_icmo_sync.funit as production_id_funit,
                                   ck_icmo_sync.seobillno as production_id_seobillno,
                                   ck_icmo_sync.fcustno as production_id_fcustno,
                                   ck_icmo_sync.fnote as production_id_fnote,
                                   ck_icmo_sync.fdate as production_id_fdate,
                                   ck_routing_sync.froutingname as routing_froutingname,
                                   ck_routing_sync.fopername as routing_fopername,
                                   ck_routing_sync.fworkcentername as routing_fworkcentername,
                                   ck_routing_sync.if_needrqty as routing_if_needrqty,
                                   ck_routing_sync.if_need_manypeoplereport as routing_if_need_manypeoplereport,
                                   ck_hours_worker_line.gqty,
                                   ck_hours_worker_line.sqty,
                                   ck_hours_worker_line.price,
                                   ck_hours_worker_line.amount,
                                   ck_hours_worker_line.date_worker,
                                   ck_hours_worker_line.state,
                                   ck_hours_worker_line.fshift,
                                   ck_hours_worker_line.fmachine,
                                   ck_hours_worker_line.fpass,
                                   ck_hours_worker.name as order_id_name,
                                   ck_hours_worker_line.id,
                                   ck_hours_worker_line.rqty,
                                   ck_icmo_sync.fqty as production_id_fqty,
                                   ck_hours_worker_line.reportpeople
                                   from ck_hours_worker_line inner join ck_hours_worker on ck_hours_worker_line.order_id = ck_hours_worker.id
                                  inner join ck_icmo_sync on ck_hours_worker.production_id = ck_icmo_sync.id
                          left join ck_routing_sync on ck_routing_sync.fworkcenterno = ck_hours_worker.fworkcenterno and ck_routing_sync.foperno = ck_hours_worker.foperno
                          where ck_hours_worker_line.id in (%s)
                       ''' % (idstr_cond)
                self._cr.execute(query_sql)
                data = data + self._cr.fetchall()
                # for item in data:
                #     print item

            for line in data:
                thisinfo = line
                # for line in thisinfo.lines:
                ml = {}
                i = 0
                ml['userid'] = line[i] or ''
                i = i + 1
                ml['username'] = line[i] or ''
                i = i + 1
                ml['fworkcenterno'] = line[i] or ''  # 工作中心编码
                i = i + 1
                ml['production_name'] = line[i] or ''  # 生产任务单号
                i = i + 1
                ml['fnumber'] = line[i] or ''  # 产品编码
                i = i + 1
                ml['fname'] = line[i] or ''  # 产品描述
                i = i + 1
                ml['fmodel'] = line[i] or ''  # 产品型号
                i = i + 1
                ml['froutingno'] = line[i] or ''  # 工艺编码
                i = i + 1
                ml['fqty'] = line[i] or 0.0  # 数量
                i = i + 1
                ml['funit'] = line[i] or ''  # 单位
                i = i + 1
                ml['seobillno'] = line[i] or '' or ''  # 销售订单号
                i = i + 1
                ml['fcustno'] = line[i] or ''  # 客户编号
                i = i + 1
                ml['fnote'] = line[i] or ''  # 客户备注
                i = i + 1
                ml['fdate'] = line[i] or ''  # 产品交期
                i = i + 1

                # routing = self.env['ck.routing.sync'].search([('fworkcenterno', '=', thisinfo.fworkcenterno), ('foperno', '=', thisinfo.foperno)], limit=1)

                ml['froutingname'] = line[i] or ''  # 工艺名称
                i = i + 1
                ml['fopername'] = line[i] or ''  # 工序名称
                i = i + 1
                ml['fworkcentername'] = line[i] or ''  # 工作中心名称
                i = i + 1
                ml['if_needrqty'] = line[i] or False  # 是否需要插排数
                i = i + 1
                ml['if_need_manypeoplereport'] = line[i] or False  # 是否需报多人
                i = i + 1

                ml['gqty'] = line[i] or 0.0  # 良品数量
                i = i + 1
                ml['sqty'] = line[i] or 0.0  # 报废数量
                i = i + 1
                ml['price'] = line[i] or 0.0  # 工价
                i = i + 1
                ml['amount'] = line[i] or 0.0  # 金额
                i = i + 1
                date = line[i] or ''
                ml['date_worker'] = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).strftime(
                    '%Y-%m-%d')
                i = i + 1
                # ml['date_worker'] = datetime.datetime.strptime(line.date_worker, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).date() #报工时间
                # ml['date_worker']  = line.date_worker
                ml['date_worker'] = ml['date_worker'][0:10]  # 报工时间
                ml['state'] = line[i] or ''  # 报工时间
                i = i + 1

                ml['fshift'] = line[i] or ''  # 班次
                i = i + 1
                ml['fmachine'] = line[i] or ''  # 单双机
                i = i + 1
                ml['fpass'] = line[i] or ''  # 合格率
                i = i + 1

                ml['name'] = line[i] or ''  # 编号
                i = i + 1
                ml['id'] = line[i] or ''  # ID
                i = i + 1
                ml['rqty'] = line[i] or 0.0  # 插排数量
                i = i + 1
                ml['production_fqty'] = line[i] or 0.0  # 工单数量
                i = i + 1
                ml['reportpeople'] = line[i] or ''  # 多人报工人员备注
                l.append(ml)

            #     print l
            # print l
        return l

    '''
    @api.multi
    def groupline_by_userid(self):
        # start_date = '2017-06-15'
        # end_date = '2017-06-21'
        thisinfos = self.env['ck.hours.worker.line'].search([('state', '=', 'new')])
        l = []
        for line in thisinfos:
            thisinfo = line
            # for line in thisinfo.lines:
            ml = {}
            ml['userid'] = thisinfo.user_id.id
            ml['username'] = thisinfo.user_id.name

            ml['fworkcenterno'] = thisinfo.fworkcenterno  # 工作中心编码
            ml['production_name'] = thisinfo.production_id.name  # 生产任务单号
            ml['fnumber'] = thisinfo.production_id.fnumber  # 产品编码
            ml['fname'] = thisinfo.production_id.fname  # 产品描述
            ml['fmodel'] = thisinfo.production_id.fmodel  # 产品型号
            ml['froutingno'] = thisinfo.production_id.froutingno  # 工艺编码
            ml['fqty'] = thisinfo.pqty  # 数量
            ml['funit'] = thisinfo.production_id.funit  # 单位
            ml['seobillno'] = thisinfo.production_id.seobillno  # 销售订单号
            ml['fcustno'] = thisinfo.production_id.fcustno  # 客户编号
            ml['fnote'] = thisinfo.production_id.fnote  # 客户备注
            ml['fdate'] = thisinfo.production_id.fdate  # 产品交期

            routing = self.env['ck.routing.sync'].search([('fworkcenterno', '=', thisinfo.fworkcenterno), ('foperno', '=', thisinfo.foperno)], limit=1)

            ml['froutingname'] = routing.froutingname  # 工艺名称
            ml['fopername'] = routing.fopername  # 工序名称
            ml['fworkcentername'] = routing.fworkcentername  # 工作中心名称
            ml['if_needrqty'] = routing.if_needrqty  # 是否需要插排数
            ml['if_need_manypeoplereport'] = routing.if_need_manypeoplereport  # 是否需报多人

            ml['gqty'] = line.gqty  # 良品数量
            ml['sqty'] = line.sqty  # 报废数量
            ml['price'] = line.price  # 工价
            ml['amount'] = line.amount  # 金额
            ml['date_worker'] = datetime.datetime.strptime(line.date_worker, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).strftime(
                '%Y-%m-%d')
            # ml['date_worker'] = datetime.datetime.strptime(line.date_worker, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).date() #报工时间
            # ml['date_worker']  = line.date_worker
            ml['date_worker'] = ml['date_worker'][0:10]  # 报工时间
            ml['state'] = line.state  # 报工时间

            ml['fshift'] = line.fshift  # 班次
            ml['fmachine'] = line.fmachine  # 单双机
            ml['fpass'] = line.fpass  # 合格率

            ml['name'] = thisinfo.order_id.name  # 编号
            ml['id'] = thisinfo.id  # ID
            ml['rqty'] = thisinfo.rqty  # 插排数量
            ml['production_fqty'] = thisinfo.production_id.fqty  # 工单数量
            ml['rqty'] = thisinfo.rqty  # 插排数量
            ml['reportpeople'] = thisinfo.reportpeople  # 多人报工人员备注
            flag = True;
            for ll in l:
                line_date = datetime.datetime.strptime(line.date_worker, "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).strftime('%Y-%m-%d')
                group_date = ll['date_worker'][0:10]
                if (ll['userid'] == thisinfo.user_id.id) and (line_date == group_date):
                    flag = False;
                    ll['gqty'] = ll['gqty'] + line.gqty

            if flag:
                l.append(ml)

        #     print l
        # print l
        return l
        '''

    @api.multi
    def groupline_by_userid(self):
        # start_date = '2017-06-15'
        # end_date = '2017-06-21'
        thisinfos = self.env['ck.hours.worker.line'].search([('state', '=', 'new')])
        l = []
        data = []
        while len(thisinfos) > 0:
            thisinfo = thisinfos[:100]
            thisinfos = thisinfos - thisinfo
            if len(thisinfo) > 0:
                idstr_cond = str(thisinfo.mapped('id')).replace('[', '').replace(']', '')
                query_sql = '''
                          select ck_hours_worker.user_id as user_id ,
                            (select name from res_partner where id = (select partner_id from res_users where id =     ck_hours_worker.user_id limit 1) limit 1) as name ,
                            ck_hours_worker.fworkcenterno,
                            ck_icmo_sync.name as production_id_name,
                            ck_icmo_sync.fnumber as production_id_fnumber,
                            ck_icmo_sync.fname as production_id_fname,
                            ck_icmo_sync.fmodel as production_id_fmodel,
                            ck_icmo_sync.froutingno as production_id_froutingno,
                            pqty,
                            ck_icmo_sync.funit as production_id_funit,
                            ck_icmo_sync.seobillno as production_id_seobillno,
                            ck_icmo_sync.fcustno as production_id_fcustno,
                            ck_icmo_sync.fnote as production_id_fnote,
                            ck_icmo_sync.fdate as production_id_fdate,
                            ck_routing_sync.froutingname as routing_froutingname,
                            ck_routing_sync.fopername as routing_fopername,
                            ck_routing_sync.fworkcentername as routing_fworkcentername,
                            ck_routing_sync.if_needrqty as routing_if_needrqty,
                            ck_routing_sync.if_need_manypeoplereport as routing_if_need_manypeoplereport,
                            ck_hours_worker_line.gqty,
                            ck_hours_worker_line.sqty,
                            ck_hours_worker_line.price,
                            ck_hours_worker_line.amount,
                            ck_hours_worker_line.date_worker,
                            ck_hours_worker_line.state,
                            ck_hours_worker_line.fshift,
                            ck_hours_worker_line.fmachine,
                            ck_hours_worker_line.fpass,
                            ck_hours_worker.name as order_id_name,
                            ck_hours_worker_line.id,
                            ck_hours_worker_line.rqty,
                            ck_icmo_sync.fqty as production_id_fqty,
                            ck_hours_worker_line.reportpeople
                            from ck_hours_worker_line inner join ck_hours_worker on ck_hours_worker_line.order_id = ck_hours_worker.id
                           inner join ck_icmo_sync on ck_hours_worker.production_id = ck_icmo_sync.id
                   left join ck_routing_sync on ck_routing_sync.fworkcenterno = ck_hours_worker.fworkcenterno and ck_routing_sync.foperno = ck_hours_worker.foperno
                   where ck_hours_worker_line.id in (%s)
                ''' % (idstr_cond)
                self._cr.execute(query_sql)
                data = data + self._cr.fetchall()
                # for item in data:
                #     print item

            for line in data:
                # for line in thisinfo.lines:
                ml = {}
                i = 0
                ml['userid'] = line[i] or ''
                i = i + 1
                ml['username'] = line[i] or ''
                i = i + 1
                ml['fworkcenterno'] = line[i] or ''  # 工作中心编码
                i = i + 1
                ml['production_name'] = line[i] or ''  # 生产任务单号
                i = i + 1
                ml['fnumber'] = line[i] or ''  # 产品编码
                i = i + 1
                ml['fname'] = line[i] or ''  # 产品描述
                i = i + 1
                ml['fmodel'] = line[i] or ''  # 产品型号
                i = i + 1
                ml['froutingno'] = line[i] or ''  # 工艺编码
                i = i + 1
                ml['fqty'] = line[i] or ''  # 数量
                i = i + 1
                ml['funit'] = line[i] or ''  # 单位
                i = i + 1
                ml['seobillno'] = line[i] or '' or ''  # 销售订单号
                i = i + 1
                ml['fcustno'] = line[i] or ''  # 客户编号
                i = i + 1
                ml['fnote'] = line[i] or ''  # 客户备注
                i = i + 1
                ml['fdate'] = line[i] or ''  # 产品交期
                i = i + 1

                # routing = self.env['ck.routing.sync'].search([('fworkcenterno', '=', thisinfo.fworkcenterno), ('foperno', '=', thisinfo.foperno)], limit=1)

                ml['froutingname'] = line[i] or ''  # 工艺名称
                i = i + 1
                ml['fopername'] = line[i] or ''  # 工序名称
                i = i + 1
                ml['fworkcentername'] = line[i] or ''  # 工作中心名称
                i = i + 1
                ml['if_needrqty'] = line[i] or False  # 是否需要插排数
                i = i + 1
                ml['if_need_manypeoplereport'] = line[i] or False  # 是否需报多人
                i = i + 1

                ml['gqty'] = line[i] or 0.0  # 良品数量
                i = i + 1
                ml['sqty'] = line[i] or 0.0  # 报废数量
                i = i + 1
                ml['price'] = line[i] or 0.0  # 工价
                i = i + 1
                ml['amount'] = line[i] or 0.0  # 金额
                i = i + 1
                date = line[i] or ''
                ml['date_worker'] = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).strftime(
                    '%Y-%m-%d')
                i = i + 1
                # ml['date_worker'] = datetime.datetime.strptime(line.date_worker, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).date() #报工时间
                # ml['date_worker']  = line.date_worker
                ml['date_worker'] = ml['date_worker'][0:10]  # 报工时间
                ml['state'] = line[i] or ''  # 报工时间
                i = i + 1

                ml['fshift'] = line[i] or ''  # 班次
                i = i + 1
                ml['fmachine'] = line[i] or ''  # 单双机
                i = i + 1
                ml['fpass'] = line[i] or 100  # 合格率
                i = i + 1

                ml['name'] = line[i] or ''  # 编号
                i = i + 1
                ml['id'] = line[i] or ''  # ID
                i = i + 1
                ml['rqty'] = line[i] or 0.0  # 插排数量
                i = i + 1
                ml['production_fqty'] = line[i] or 0.0  # 工单数量
                i = i + 1
                ml['reportpeople'] = line[i] or ''  # 多人报工人员备注
                flag = True
                for ll in l:
                    line_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").replace(
                        tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).strftime('%Y-%m-%d')
                    group_date = ll['date_worker'][0:10]
                    if (ll['userid'] == ml['userid']) and (line_date == group_date):
                        flag = False;
                        ll['gqty'] = ll['gqty'] + ml['gqty']

                if flag:
                    l.append(ml)

            #     print l
            # print l
        return l

    '''
    @api.multi
    def search_by_userid_approve(self, userid, date):
        # date = '2017-06-15'
        # userid = 1

        date_from = date + ' 00:00:00'
        date_to = date + ' 23:59:59'

        current_date_from = (datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')).replace(tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
        current_date_to = (datetime.datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')).replace(tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))

        # current_date = (datetime.datetime.strptime(date, '%Y-%m-%d')).replace(tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
        # date = current_date.strftime('%Y-%m-%d')
        date_format_from = current_date_from.strftime('%Y-%m-%d %H:%M:%S')
        date_format_to = current_date_to.strftime('%Y-%m-%d %H:%M:%S')
        thisinfos = self.env['ck.hours.worker.line'].search(
            [('state', '=', 'new'), ('date_worker', '>=', date_format_from), ('date_worker', '<=', date_format_to), ('user_id', '=', userid)], order='date_worker desc')
        l = []
        for line in thisinfos:
            thisinfo = line
            # for line in thisinfo.lines:
            ml = {}
            ml['username'] = thisinfo.user_id.name

            ml['production_name'] = thisinfo.production_id.name  # 生产任务单号
            ml['fnumber'] = thisinfo.production_id.fnumber  # 产品编码
            ml['fname'] = thisinfo.production_id.fname  # 产品描述
            ml['fmodel'] = thisinfo.production_id.fmodel  # 产品型号
            ml['froutingno'] = thisinfo.production_id.froutingno  # 工艺编码
            ml['fqty'] = thisinfo.pqty  # 数量
            ml['funit'] = thisinfo.production_id.funit  # 单位
            ml['seobillno'] = thisinfo.production_id.seobillno  # 销售订单号
            ml['fcustno'] = thisinfo.production_id.fcustno  # 客户编号
            ml['fnote'] = thisinfo.production_id.fnote  # 客户备注
            ml['fdate'] = thisinfo.production_id.fdate  # 产品交期

            ml['totalgqty'] = thisinfo.gqty  # 总良品数
            ml['totalsqty'] = thisinfo.sqty  # 总报废数

            routing = self.env['ck.routing.sync'].search([('fworkcenterno', '=', thisinfo.fworkcenterno), ('foperno', '=', thisinfo.foperno)], limit=1)

            ml['froutingname'] = routing.froutingname  # 工艺名称
            ml['fopername'] = routing.fopername  # 工序名称
            ml['fworkcentername'] = routing.fworkcentername  # 工作中心名称
            ml['if_needrqty'] = routing.if_needrqty  # 是否需要插排数
            ml['if_need_manypeoplereport'] = routing.if_need_manypeoplereport  # 是否需报多人

            ml['gqty'] = line.gqty  # 良品数量
            ml['sqty'] = line.sqty  # 报废数量
            ml['price'] = line.price  # 工价
            ml['amount'] = line.amount  # 金额

            #          dt = line.date_worker.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))

            ml['date_worker'] = datetime.datetime.strptime(line.date_worker, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).strftime(
                '%Y-%m-%d %H:%M:%S')  # 报工时间

            ml['state'] = line.state  # 报工时间
            ml['id'] = line.id  # 报工时间

            ml['fshift'] = line.fshift  # 班次
            ml['fmachine'] = line.fmachine  # 单双机
            ml['fpass'] = line.fpass  # 合格率

            ml['name'] = thisinfo.order_id.name  # 编号
            ml['id'] = thisinfo.id  # ID
            ml['production_fqty'] = thisinfo.production_id.fqty  # 工单数量
            ml['rqty'] = thisinfo.rqty  # 插排数量
            ml['reportpeople'] = thisinfo.reportpeople  # 多人报工人员备注
            l.append(ml)

        #     print l
        # print l
        return l
    '''

    @api.multi
    def search_by_userid_approve(self, userid, date):
        # date = '2017-06-15'
        # userid = 1

        date_from = date + ' 00:00:00'
        date_to = date + ' 23:59:59'

        current_date_from = (datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')).replace(tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
        current_date_to = (datetime.datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')).replace(tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))

        # current_date = (datetime.datetime.strptime(date, '%Y-%m-%d')).replace(tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
        # date = current_date.strftime('%Y-%m-%d')
        date_format_from = current_date_from.strftime('%Y-%m-%d %H:%M:%S')
        date_format_to = current_date_to.strftime('%Y-%m-%d %H:%M:%S')
        thisinfos = self.env['ck.hours.worker.line'].search(
            [('state', '=', 'new'), ('date_worker', '>=', date_format_from), ('date_worker', '<=', date_format_to), ('user_id', '=', userid)], order='date_worker desc')
        l = []
        data = []
        while len(thisinfos) > 0:
            thisinfo = thisinfos[:100]
            thisinfos = thisinfos - thisinfo
            if len(thisinfo) > 0:
                idstr_cond = str(thisinfo.mapped('id')).replace('[', '').replace(']', '')
                query_sql = '''
                                 select ck_hours_worker.user_id as user_id ,
                                   (select name from res_partner where id = (select partner_id from res_users where id =     ck_hours_worker.user_id limit 1) limit 1) as name ,
                                   ck_hours_worker.fworkcenterno,
                                   ck_icmo_sync.name as production_id_name,
                                   ck_icmo_sync.fnumber as production_id_fnumber,
                                   ck_icmo_sync.fname as production_id_fname,
                                   ck_icmo_sync.fmodel as production_id_fmodel,
                                   ck_icmo_sync.froutingno as production_id_froutingno,
                                   pqty,
                                   ck_icmo_sync.funit as production_id_funit,
                                   ck_icmo_sync.seobillno as production_id_seobillno,
                                   ck_icmo_sync.fcustno as production_id_fcustno,
                                   ck_icmo_sync.fnote as production_id_fnote,
                                   ck_icmo_sync.fdate as production_id_fdate,
                                   ck_routing_sync.froutingname as routing_froutingname,
                                   ck_routing_sync.fopername as routing_fopername,
                                   ck_routing_sync.fworkcentername as routing_fworkcentername,
                                   ck_routing_sync.if_needrqty as routing_if_needrqty,
                                   ck_routing_sync.if_need_manypeoplereport as routing_if_need_manypeoplereport,
                                   ck_hours_worker_line.gqty,
                                   ck_hours_worker_line.sqty,
                                   ck_hours_worker_line.price,
                                   ck_hours_worker_line.amount,
                                   ck_hours_worker_line.date_worker,
                                   ck_hours_worker_line.state,
                                   ck_hours_worker_line.fshift,
                                   ck_hours_worker_line.fmachine,
                                   ck_hours_worker_line.fpass,
                                   ck_hours_worker.name as order_id_name,
                                   ck_hours_worker_line.id,
                                   ck_hours_worker_line.rqty,
                                   ck_icmo_sync.fqty as production_id_fqty,
                                   ck_hours_worker_line.reportpeople
                                   from ck_hours_worker_line inner join ck_hours_worker on ck_hours_worker_line.order_id = ck_hours_worker.id
                                  inner join ck_icmo_sync on ck_hours_worker.production_id = ck_icmo_sync.id
                          left join ck_routing_sync on ck_routing_sync.fworkcenterno = ck_hours_worker.fworkcenterno and ck_routing_sync.foperno = ck_hours_worker.foperno
                          where ck_hours_worker_line.id in (%s)
                       ''' % (idstr_cond)
                self._cr.execute(query_sql)
                data = data + self._cr.fetchall()
                # for item in data:
                #     print item

            for line in data:
                thisinfo = line
                # for line in thisinfo.lines:
                ml = {}
                i = 0
                ml['userid'] = line[i] or ''
                i = i + 1
                ml['username'] = line[i] or ''
                i = i + 1
                ml['fworkcenterno'] = line[i] or ''  # 工作中心编码
                i = i + 1
                ml['production_name'] = line[i] or ''  # 生产任务单号
                i = i + 1
                ml['fnumber'] = line[i] or ''  # 产品编码
                i = i + 1
                ml['fname'] = line[i] or ''  # 产品描述
                i = i + 1
                ml['fmodel'] = line[i] or ''  # 产品型号
                i = i + 1
                ml['froutingno'] = line[i] or ''  # 工艺编码
                i = i + 1
                ml['fqty'] = line[i] or 0.0  # 数量
                i = i + 1
                ml['funit'] = line[i] or ''  # 单位
                i = i + 1
                ml['seobillno'] = line[i] or '' or ''  # 销售订单号
                i = i + 1
                ml['fcustno'] = line[i] or ''  # 客户编号
                i = i + 1
                ml['fnote'] = line[i] or ''  # 客户备注
                i = i + 1
                ml['fdate'] = line[i] or ''  # 产品交期
                i = i + 1

                # routing = self.env['ck.routing.sync'].search([('fworkcenterno', '=', thisinfo.fworkcenterno), ('foperno', '=', thisinfo.foperno)], limit=1)

                ml['froutingname'] = line[i] or ''  # 工艺名称
                i = i + 1
                ml['fopername'] = line[i] or ''  # 工序名称
                i = i + 1
                ml['fworkcentername'] = line[i] or ''  # 工作中心名称
                i = i + 1
                ml['if_needrqty'] = line[i] or False  # 是否需要插排数
                i = i + 1
                ml['if_need_manypeoplereport'] = line[i] or False  # 是否需报多人
                i = i + 1

                ml['gqty'] = line[i] or 0.0  # 良品数量
                i = i + 1
                ml['sqty'] = line[i] or 0.0  # 报废数量
                i = i + 1
                ml['price'] = line[i] or 0.0  # 工价
                i = i + 1
                ml['amount'] = line[i] or 0.0  # 金额
                i = i + 1
                date = line[i] or ''
                ml['date_worker'] = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).strftime(
                    '%Y-%m-%d')
                i = i + 1
                # ml['date_worker'] = datetime.datetime.strptime(line.date_worker, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).date() #报工时间
                # ml['date_worker']  = line.date_worker
                ml['date_worker'] = ml['date_worker'][0:10]  # 报工时间
                ml['state'] = line[i] or ''  # 报工时间
                i = i + 1

                ml['fshift'] = line[i] or ''  # 班次
                i = i + 1
                ml['fmachine'] = line[i] or ''  # 单双机
                i = i + 1
                ml['fpass'] = line[i] or ''  # 合格率
                i = i + 1

                ml['name'] = line[i] or ''  # 编号
                i = i + 1
                ml['id'] = line[i] or ''  # ID
                i = i + 1
                ml['rqty'] = line[i] or 0.0  # 插排数量
                i = i + 1
                ml['production_fqty'] = line[i] or 0.0  # 工单数量
                i = i + 1
                ml['reportpeople'] = line[i] or ''  # 多人报工人员备注
                l.append(ml)

            #     print l
            # print l
        return l

    @api.multi
    def getusergroupmenuino(self):
        group_rw_admin = self.env.ref('kindee_data_sync_info.group_rw_admin')
        group_rw_manager = self.env.ref('kindee_data_sync_info.group_rw_manager')
        group_rw_termleader = self.env.ref('kindee_data_sync_info.group_rw_termleader')
        group_rw_employee = self.env.ref('kindee_data_sync_info.group_rw_employee')
        thisinfos = self
        mygroup = group_rw_employee
        flag = True
        if flag:
            for group in thisinfos.env.user.groups_id:
                if group == group_rw_admin:
                    # print group_rw_admin
                    flag = False
                    mygroup = group_rw_admin
        if flag:
            for group in thisinfos.env.user.groups_id:
                if group == group_rw_manager:
                    # print group_rw_manager
                    flag = False
                    mygroup = group_rw_manager
        if flag:
            for group in thisinfos.env.user.groups_id:
                if group == group_rw_termleader:
                    # print group_rw_termleader
                    flag = False
                    mygroup = group_rw_termleader
        if flag:
            for group in thisinfos.env.user.groups_id:
                if group == group_rw_employee:
                    # print group_rw_employee
                    flag = False
                    mygroup = group_rw_employee

        menu_ck_personal_information = self.env.ref('kindee_data_sync_info.menu_ck_personal_information')
        menu_ck_change_password = self.env.ref('kindee_data_sync_info.menu_ck_change_password')
        menu_ck_my_report = self.env.ref('kindee_data_sync_info.menu_ck_my_report')
        menu_ck_approve_report = self.env.ref('kindee_data_sync_info.menu_ck_approve_report')
        menu_ck_exit = self.env.ref('kindee_data_sync_info.menu_ck_exit')
        # print mygroup
        l = []
        for menu_access in mygroup.menu_access:
            if menu_access == menu_ck_personal_information:
                l.append('menu_ck_personal_information')
            if menu_access == menu_ck_change_password:
                l.append('menu_ck_change_password')
            if menu_access == menu_ck_my_report:
                l.append('menu_ck_my_report')
            if menu_access == menu_ck_approve_report:
                l.append('menu_ck_approve_report')
            if menu_access == menu_ck_exit:
                l.append('menu_ck_exit')

        # print l
        return l

    # 根据ID选择报工信息
    @api.multi
    def search_by_userid_orderid(self, order_id):
        # start_date = '2017-06-15'

        # end_date = '2017-06-21'
        thisinfos = self.env['ck.hours.worker.line'].search([('id', '=', order_id), ('state', '!=', 'del')])
        l = []
        for line in thisinfos:
            thisinfo = line
            # for line in thisinfo.lines:
            ml = {}
            ml['username'] = thisinfo.user_id.name
            ml['fworkcenterno'] = thisinfo.fworkcenterno  # 工作中心编码
            ml['production_name'] = thisinfo.production_id.name  # 生产任务单号
            ml['fnumber'] = thisinfo.production_id.fnumber  # 产品编码
            ml['fname'] = thisinfo.production_id.fname  # 产品描述
            ml['fmodel'] = thisinfo.production_id.fmodel  # 产品型号
            ml['froutingno'] = thisinfo.production_id.froutingno  # 工艺编码
            ml['fqty'] = thisinfo.pqty  # 数量
            ml['funit'] = thisinfo.production_id.funit  # 单位
            ml['seobillno'] = thisinfo.production_id.seobillno  # 销售订单号
            ml['fcustno'] = thisinfo.production_id.fcustno  # 客户编号
            ml['fnote'] = thisinfo.production_id.fnote  # 客户备注
            ml['fdate'] = thisinfo.production_id.fdate  # 产品交期

            routing = self.env['ck.routing.sync'].search([('fworkcenterno', '=', thisinfo.fworkcenterno), ('foperno', '=', thisinfo.foperno)], limit=1)

            ml['froutingname'] = routing.froutingname  # 工艺名称
            ml['fopername'] = routing.fopername  # 工序名称
            ml['fworkcentername'] = routing.fworkcentername  # 工作中心名称

            ml['gqty'] = line.gqty  # 良品数量
            ml['sqty'] = line.sqty  # 报废数量
            ml['price'] = line.price  # 工价
            ml['amount'] = line.amount  # 金额
            ml['date_worker'] = datetime.datetime.strptime(line.date_worker, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).strftime(
                '%Y-%m-%d %H:%M:%S')  # 报工时间
            ml['state'] = line.state  # 报工时间
            ml['id'] = line.id  # 报工时间
            ml['user_id'] = line.user_id.id  # 用户id

            ml['fshift'] = line.fshift  # 班次
            ml['fmachine'] = line.fmachine  # 单双机
            ml['fpass'] = line.fpass  # 合格率

            ml['name'] = thisinfo.order_id.name  # 编号
            ml['id'] = thisinfo.id  # ID
            ml['production_fqty'] = thisinfo.production_id.fqty  # 工单数量
            ml['rqty'] = thisinfo.rqty  # 插排数量
            ml['reportpeople'] = thisinfo.reportpeople  # 多人报工人员备注
            l.append(ml)

        #     print l
        # print l
        return l

    # 根据生产任务单查询报工信息
    @api.multi
    def searchWorkBy_name_froutingno_foperno(self, name, froutingno, foperno, fworkcenterno):
        thisinfos = self.env['ck.hours.worker'].search([('production_id.name', '=', name),
                                                        ('foperno', '=', foperno),
                                                        ('fworkcenterno', '=', fworkcenterno),
                                                        ('state', '!=', 'del')])
        l = []
        data = []
        while len(thisinfos) > 0:
            thisinfo = thisinfos[:100]
            thisinfos = thisinfos - thisinfo
            if len(thisinfo) > 0:
                idstr_cond = str(thisinfo.mapped('id')).replace('[', '').replace(']', '')
                query_sql = '''
                                 select ck_hours_worker.user_id as user_id ,
                                   (select name from res_partner where id = (select partner_id from res_users where id =     ck_hours_worker.user_id limit 1) limit 1) as name ,
                                   ck_hours_worker.fworkcenterno,
                                   ck_icmo_sync.name as production_id_name,
                                   ck_icmo_sync.fnumber as production_id_fnumber,
                                   ck_icmo_sync.fname as production_id_fname,
                                   ck_icmo_sync.fmodel as production_id_fmodel,
                                   ck_icmo_sync.froutingno as production_id_froutingno,
                                   pqty,
                                   ck_icmo_sync.funit as production_id_funit,
                                   ck_icmo_sync.seobillno as production_id_seobillno,
                                   ck_icmo_sync.fcustno as production_id_fcustno,
                                   ck_icmo_sync.fnote as production_id_fnote,
                                   ck_icmo_sync.fdate as production_id_fdate,
                                   ck_routing_sync.froutingname as routing_froutingname,
                                   ck_routing_sync.fopername as routing_fopername,
                                   ck_routing_sync.fworkcentername as routing_fworkcentername,
                                   ck_routing_sync.if_needrqty as routing_if_needrqty,
                                   ck_routing_sync.if_need_manypeoplereport as routing_if_need_manypeoplereport,
                                   ck_hours_worker_line.gqty,
                                   ck_hours_worker_line.sqty,
                                   ck_hours_worker_line.price,
                                   ck_hours_worker_line.amount,
                                   ck_hours_worker_line.date_worker,
                                   ck_hours_worker_line.state,
                                   ck_hours_worker_line.fshift,
                                   ck_hours_worker_line.fmachine,
                                   ck_hours_worker_line.fpass,
                                   ck_hours_worker.name as order_id_name,
                                   ck_hours_worker_line.id,
                                   ck_hours_worker_line.rqty,
                                   ck_icmo_sync.fqty as production_id_fqty,
                                   ck_hours_worker_line.reportpeople
                                   from ck_hours_worker_line inner join ck_hours_worker on ck_hours_worker_line.order_id = ck_hours_worker.id
                                  inner join ck_icmo_sync on ck_hours_worker.production_id = ck_icmo_sync.id
                          left join ck_routing_sync on ck_routing_sync.fworkcenterno = ck_hours_worker.fworkcenterno and ck_routing_sync.foperno = ck_hours_worker.foperno
                          where ck_hours_worker_line.id in (%s)
                       ''' % (idstr_cond)
                self._cr.execute(query_sql)
                data = data + self._cr.fetchall()
                # for item in data:
                #     print item

            for line in data:
                thisinfo = line
                # for line in thisinfo.lines:
                ml = {}
                i = 0
                ml['userid'] = line[i] or ''
                i = i + 1
                ml['username'] = line[i] or ''
                i = i + 1
                ml['fworkcenterno'] = line[i] or ''  # 工作中心编码
                i = i + 1
                ml['production_name'] = line[i] or ''  # 生产任务单号
                i = i + 1
                ml['fnumber'] = line[i] or ''  # 产品编码
                i = i + 1
                ml['fname'] = line[i] or ''  # 产品描述
                i = i + 1
                ml['fmodel'] = line[i] or ''  # 产品型号
                i = i + 1
                ml['froutingno'] = line[i] or ''  # 工艺编码
                i = i + 1
                ml['fqty'] = line[i] or 0.0  # 数量
                i = i + 1
                ml['funit'] = line[i] or ''  # 单位
                i = i + 1
                ml['seobillno'] = line[i] or '' or ''  # 销售订单号
                i = i + 1
                ml['fcustno'] = line[i] or ''  # 客户编号
                i = i + 1
                ml['fnote'] = line[i] or ''  # 客户备注
                i = i + 1
                ml['fdate'] = line[i] or ''  # 产品交期
                i = i + 1

                # routing = self.env['ck.routing.sync'].search([('fworkcenterno', '=', thisinfo.fworkcenterno), ('foperno', '=', thisinfo.foperno)], limit=1)

                ml['froutingname'] = line[i] or ''  # 工艺名称
                i = i + 1
                ml['fopername'] = line[i] or ''  # 工序名称
                i = i + 1
                ml['fworkcentername'] = line[i] or ''  # 工作中心名称
                i = i + 1
                ml['if_needrqty'] = line[i] or False  # 是否需要插排数
                i = i + 1
                ml['if_need_manypeoplereport'] = line[i] or False  # 是否需报多人
                i = i + 1

                ml['gqty'] = line[i] or 0.0  # 良品数量
                i = i + 1
                ml['sqty'] = line[i] or 0.0  # 报废数量
                i = i + 1
                ml['price'] = line[i] or 0.0  # 工价
                i = i + 1
                ml['amount'] = line[i] or 0.0  # 金额
                i = i + 1
                date = line[i] or ''
                ml['date_worker'] = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).strftime(
                    '%Y-%m-%d')
                i = i + 1
                # ml['date_worker'] = datetime.datetime.strptime(line.date_worker, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.env.user.tz)).date() #报工时间
                # ml['date_worker']  = line.date_worker
                ml['date_worker'] = ml['date_worker'][0:10]  # 报工时间
                ml['state'] = line[i] or ''  # 报工时间
                i = i + 1

                ml['fshift'] = line[i] or ''  # 班次
                i = i + 1
                ml['fmachine'] = line[i] or ''  # 单双机
                i = i + 1
                ml['fpass'] = line[i] or ''  # 合格率
                i = i + 1

                ml['name'] = line[i] or ''  # 编号
                i = i + 1
                ml['id'] = line[i] or ''  # ID
                i = i + 1
                ml['rqty'] = line[i] or 0.0  # 插排数量
                i = i + 1
                ml['production_fqty'] = line[i] or 0.0  # 工单数量
                i = i + 1
                ml['reportpeople'] = line[i] or ''  # 多人报工人员备注
                l.append(ml)

            #     print l
            # print l
        return l

    # 选择当前任务单里面报了多少工作中心，工序，工艺
    @api.multi
    def searchWorkBy_GroupBy(self, name, froutingno, foperno, fworkcenterno):
        domain = [];
        if name:
            domain.append(('production_id.name', '=', name))
        if froutingno:
            domain.append(('production_id.froutingno', '=', froutingno))
        if foperno:
            domain.append(('foperno', '=', foperno))
        if fworkcenterno:
            domain.append(('fworkcenterno', '=', fworkcenterno))
        domain.append(('state', '!=', 'del'))
        thisinfos = self.env['ck.hours.worker'].search(domain)
        l = []
        for line in thisinfos:
            # for line in thisinfo.lines:
            ml = {}
            ml['foperno'] = line.foperno  # 工序编码
            routing = self.env['ck.routing.sync'].search([
                ('fworkcenterno', '=', line.fworkcenterno), ('foperno', '=', line.foperno)], limit=1)
            ml['froutingno'] = routing.froutingno  # 工艺
            ml['fworkcenterno'] = routing.fworkcenterno  # 工作中心
            ml['name'] = name  # 生产任务单
            l.append(ml)
        work_list = []
        for ll in l:
            flag = True
            froutingno_t = ll['froutingno']
            foperno_t = ll['foperno']
            fworkcenterno_t = ll['fworkcenterno']
            for work_t in work_list:
                froutingno_u = work_t['froutingno']
                foperno_u = work_t['foperno']
                fworkcenterno_u = work_t['fworkcenterno']
                if froutingno_t == froutingno_u and foperno_t == foperno_u and fworkcenterno_t == fworkcenterno_u:
                    flag = False
                    break

            if flag:
                work_list.append(ll)

        return work_list

    @api.multi
    def search_msg(self):
        # msginfos = self.env['mail.message'].search([])
        notifications = self.env['mail.notification'].search([
            ('partner_id', 'in', [self.env.user.partner_id.id]),
            ('is_read', '=', False)], order='id desc')
        # print notifications
        l = []
        for notification in notifications:
            msg = notification.message_id

            attachment_infos = []
            for attachment_id in msg.attachment_ids:
                attachment_info = {}
                attachment_info['id'] = attachment_id.id
                attachment_info['url'] = attachment_id.url
                attachment_info['res_name'] = attachment_id.res_name
                attachment_info['datas_fname'] = attachment_id.datas_fname
                attachment_info['type'] = attachment_id.type
                attachment_info['name'] = attachment_id.name
                attachment_info['user_id'] = attachment_id.user_id.id
                attachment_info['res_model'] = attachment_id.res_model
                attachment_info['mimetype'] = attachment_id.mimetype
                attachment_info['datas'] = attachment_id.datas
                attachment_infos.append(attachment_info)
            ml = {}
            ml['attachment_infos'] = attachment_infos
            ml['id'] = msg.id  # 消息编号
            ml['record_name'] = msg.record_name  # 消息编号
            ml['body'] = msg.body  # 消息体
            ml['date'] = msg.date  # 消息体
            ml['email_from'] = msg.email_from  # 消息体
            l.append(ml)
        return l

    @api.multi
    def search_msg_test(self):
        print(self)

        sql = "update ck_hours_worker_line set foperno = (select foperno from ck_hours_worker where ck_hours_worker.id = ck_hours_worker_line.order_id), " \
              "fopername = (select fopername from ck_hours_worker where ck_hours_worker.id = ck_hours_worker_line.order_id)," \
              "fmodel = (select fmodel from ck_icmo_sync where id = (select production_id from ck_hours_worker where id = ck_hours_worker_line.order_id))," \
              "fnumber = (select fnumber from ck_hours_worker where ck_hours_worker.id = ck_hours_worker_line.order_id)," \
              "fname = (select fname from ck_hours_worker where ck_hours_worker.id = ck_hours_worker_line.order_id)," \
              "pqty = (select pqty from ck_hours_worker where ck_hours_worker.id = ck_hours_worker_line.order_id)," \
              "production_id = (select production_id from ck_hours_worker where ck_hours_worker.id = ck_hours_worker_line.order_id)"

        self._cr.execute(sql)

    @api.multi
    def get_user_department_info(self):
        if self.env.user.employee_ids:
            return self.env.user.employee_ids[0].department_id.complete_name
        else:
            return ''


class CK_Hours_Worker_line(models.Model):
    _name = 'ck.hours.worker.line'
    _description = _("Hours of Worker line")
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env['res.users'].browse(self._uid).company_id.id
                                 )  # 公司
    order_id = fields.Many2one(comodel_name='ck.hours.worker', string='Order Reference',
                               ondelete='cascade', select=True, readonly=True, index=True, auto_join=True)  # 报工单
    fnumber = fields.Char(string=_('ProductNo'), related='order_id.fnumber')  # 产品编码（长）
    fname = fields.Char(string=_('ProductDesc'), related='order_id.fname')  # 产品描述
    date_worker = fields.Datetime(string=_('Report Time'), default=lambda self: fields.datetime.now(), index=True)  # 报工时间

    date_approve = fields.Datetime(string=_('Approve Time'))  # 审批时间

    user_id = fields.Many2one(comodel_name='res.users', string=_('Owner'), readonly=False, index=True)  # 用户ID
    state = fields.Selection(
        [('new', _('New')), ('done', _('Done')), ('del', _('Delete'))], _('State'), readonly=False, default='new',
        index=True)  # 状态
    sqty = fields.Float(string=_('Scrap Quantity'))  # 报废数量
    gqty = fields.Float(string=_('Good Quantity'))  # 良品数量
    price = fields.Float(compute='_compute_price', string='Price', digits=dp.get_precision('ck_workprice_digit'),
                         store=True, default=0.0)  # 单价
    amount = fields.Float(compute='_compute_price', string='Amount', digits=dp.get_precision('ck_workprice_digit'),
                          store=True, default=0.0)  # 工费

    fshift = fields.Selection([('day', _('白班')), ('night', _('晚班'))],
                              string=_('Shift'), default='day')  # 班次
    fmachine = fields.Selection([('one', _('单机')), ('multi', _('双机'))],
                                string=_('Number of machines'), default='one')  # 机台数量
    fpass = fields.Float(string=_('良品率(%)'), default=100.00)  # 合格率

    sqty_pre = fields.Float(string=_('审核报废数量'))  # 报废数量审核前
    gqty_pre = fields.Float(string=_('审核前良品'))  # 良品数量审核前
    fshift_pre = fields.Selection([('day', _('白班')), ('night', _('晚班'))],
                                  string=_('审核前班次'), default='day')  # 班次审核前
    fmachine_pre = fields.Selection([('one', _('单机')), ('multi', _('双机'))],
                                    string=_('审核前单双机'), default='one')  # 机台数量审核前
    rqty_pre = fields.Float(string=_('审核前返工数量'))  # 良品数量审核前

    fworkcentername = fields.Char(string=_('WorkCenterName'), related='order_id.fworkcentername')  # 工作中心名称

    fopername = fields.Char(string=_('OperationName'), related='order_id.fopername')  # 工序名称

    fworkcenterno = fields.Char(string=_('WorkCenterNo'), related='order_id.fworkcenterno', index=True)  # 工作中心编码

    foperno = fields.Char(string=_('OperationNo'), related='order_id.foperno', index=True)  # 工序编码

    pqty = fields.Float(string=_('Picking Quantity'), related='order_id.pqty')  # 投料数量

    production_id = fields.Many2one(comodel_name='ck.icmo.sync', string=_('ProductionOrder'),
                                    readonly=False, related='order_id.production_id', auto_join=True)

    fmodel = fields.Char(string=_('型号'), related='production_id.fmodel')  # 产品型号

    worktime = fields.Float(string=_('Work Time'))  # 工时
    remark1 = fields.Char(string=_('Remark1'))  # 备注1
    remark2 = fields.Char(string=_('Remark2'))  # 备注2
    remark3 = fields.Char(string=_('Remark3'))  # 备注3
    remark4 = fields.Char(string=_('Remark4'))  # 备注4

    department = fields.Char(compute='_compute_department', search='_search_department', string=_('部门'))

    rqty = fields.Float(string=_('Remade Quantity'), default=0)  # 插排数量

    name = fields.Char('Order Reference', required=True, copy=False, readonly=False,
                       select=True, default=lambda obj: '/', )

    scrap_lines = fields.One2many('ck.route.scrap.reasons.line', 'order_id', string='Scrap Quality Lines',
                                  readonly=False, copy=True)  # 报废明细

    material_scrap_lines = fields.One2many('ck.material.scrap.reasons.line', 'order_id', string='Material Scrap Quality Lines',
                                           readonly=False, copy=True)  # 报废明细

    reportpeople = fields.Char(string=_('Report people'))  # 多人报工人员备注

    _order = 'company_id, order_id ,  id'

    def _search_department(self, opeartor, value):
        routings = self.env['ck.routing.sync'].search([('fworkcentername', opeartor, value)])
        ids = [routing.fworkcenterno for routing in routings]
        return [('fworkcenterno', 'in', ids)]

    def send_unapproved_msg(self, cr, uid, context=None):
        print("===================================test quartz============================")
        # groups = self.pool['res.groups'].search(cr, uid,[('name', 'like', 'Team leader')])
        groups = self.pool['res.groups'].search(cr, uid, [('name', '=', 'Manager')])
        # groups = self.pool['res.groups'].search(cr, uid,[('name', '=', 'NULL')])

        for group in groups:
            mygroups = self.pool['res.groups'].browse(cr, uid, group, context=context)
            print(mygroups.users)

            for user in mygroups.users:
                print(user)

    @api.one
    @api.onchange('production_id')
    def change_production_id(self):
        self.foperno = False
        self.fopername = False
        self.fworkcenterno = False
        self.fworkcentername = False
        self.fnumber = False
        self.fname = False
        self.pqty = 0
        if self.production_id:
            if not self.fnumber or not self.fname:
                self.fnumber = self.production_id.fnumber or False
                self.fname = self.production_id.fname or False
        if not self.user_id:
            self.usr_id = self.env.user

    @api.one
    @api.onchange('foperno')
    def change_foperno(self):
        self.fopername = False
        self.fworkcenterno = False
        self.fworkcentername = False
        self.pqty = 0
        if self.foperno:
            foper_ids = self.env['ck.routing.sync'].search([('foperno', '=', self.foperno)], limit=1)
            if any(foper_ids):
                self.fopername = foper_ids[0].fopername

    @api.one
    @api.onchange('fworkcenterno')
    def change_fworkcenterno(self):
        self.pqty = 0
        self.fworkcentername = False
        if self.fworkcenterno:
            foper_ids = self.env['ck.routing.sync'].search([('fworkcenterno', '=', self.fworkcenterno)], limit=1)
            if any(foper_ids):
                self.fworkcentername = foper_ids[0].fworkcentername
            if self.company_id and self.production_id and self.foperno:

                production_opra = self.env['ck.icno.opra'].search([('company_id', '=', self.company_id.id),
                                                                   ('production_id', '=', self.production_id.id),
                                                                   ('foperno', '=', self.foperno)], limit=1)

                attrition_rate = self.env['ck.attrition.rate'].search([
                    ('fnumber', '=', self.production_id.fnumber)], limit=1)

                if not attrition_rate:
                    attrition_rate = self.env['ck.attrition.rate'].search([
                        ('fmodel', '=', self.production_id.fmodel)], limit=1)

                attrition_rate_no = 0
                if attrition_rate:
                    attrition_rate_no = attrition_rate.attrition_rate

                if production_opra:
                    production_opra._compute_qty()
                    self.pqty = self.production_id.fqty * (1 + attrition_rate_no) - production_opra.pqty
                else:
                    self.pqty = self.production_id.fqty * (1 + attrition_rate_no)

    @api.multi
    def button_confirm(self):
        # def button_confirm(self, state, sqty, gqty, rqty, fshift, fmachine):
        _logger.debug("zhoufeng:  call button_confirm start : %s" % (datetime.datetime.now()))
        if self.state != 'done':
            _logger.debug("zhoufeng:  call button_confirm write start: %s" % (datetime.datetime.now()))
            fpass = 0
            if self.gqty:
                totalnum = float(self._context['rqty'] + self._context['sqty'] + self._context['gqty'])
                passrate = round((float(self._context['gqty']) / totalnum), 4)
                fpass = passrate * 100

            self.write({'sqty': self._context['sqty'], 'gqty': self._context['gqty'], 'rqty': self._context['rqty'], 'fshift': self._context['fshift'],
                        'fmachine': self._context['fmachine'], 'date_approve': datetime.datetime.now(), 'state': 'done', 'fpass': fpass})
            _logger.debug("zhoufeng:  call button_confirm write end: %s" % (datetime.datetime.now()))
            # self.sqty = sqty
            # self.gqty = gqty
            # self.rqty = rqty
            # self.fshift = fshift
            # self.fmachine = fmachine
            # self.worktime = worktime

            # self.check_if_excess()
            # _logger.debug("zhoufeng:  call dogetprice start : %s" % (datetime.datetime.now()))
            # price, amount = self.dogetprice()
            # self.write({'price': price, 'amount': amount})
            # _logger.debug("zhoufeng:  call dogetprice end : %s" % (datetime.datetime.now()))

            # self._compute_amount()
            # self.date_approve = datetime.datetime.now()
            # self.state = 'done'
            # if self.reportpeople:
            #     self.split_by_reportpeople()
            if self.order_id:
                self.order_id.uflag = not self.order_id.uflag
                self.order_id.check_complete()

        _logger.debug("zhoufeng:  call button_confirm end : %s" % (datetime.datetime.now()))
        return True

    def check_if_excess(self):

        domain2 = []
        domain3 = []
        domain = []
        domain.append(('state', '!=', 'del'))
        if self.production_id:
            domain.append(('production_id', '=', self.production_id.id))
            domain.append(('foperno', '=', self.foperno))
            domain2.append(('fnumber', '=', self.production_id.fnumber))
            domain3.append(('fmodel', '=', self.production_id.fmodel))
        else:
            domain.append(('production_id', '=', self.order_id.production_id.id))
            domain.append(('foperno', '=', self.order_id.foperno))
            domain2.append(('fnumber', '=', self.order_id.production_id.fnumber))
            domain3.append(('fmodel', '=', self.order_id.production_id.fmodel))
        lines = self.env['ck.hours.worker.line'].search(domain)
        totaltotalnum = 0
        for line in lines:
            totalnum = line.gqty + line.sqty + line.rqty
            totaltotalnum = totaltotalnum + totalnum
        attrition_rate = self.env['ck.attrition.rate'].search(domain2, limit=1)
        if not attrition_rate:
            attrition_rate = self.env['ck.attrition.rate'].search(domain3, limit=1)
        attrition_rate_val = 0
        if attrition_rate:
            attrition_rate_val = attrition_rate.attrition_rate

        if self.production_id:
            if totaltotalnum > self.production_id.fqty * (attrition_rate_val * 100 + 100) / 100:
                raise exceptions.Warning(_('总数量超过工单数量，请检查数量是否正确。'))
        else:
            if self.order_id:
                if totaltotalnum > self.order_id.production_id.fqty * (attrition_rate_val * 100 + 100) / 100:
                    raise exceptions.Warning(_('总数量超过工单数量，请检查数量是否正确。'))
        '''
        # _logger.debug("zhoufeng:  call check_if_excess start : %s" % (datetime.datetime.now()))
        lines = self.env['ck.hours.worker.line'].search(
            [('production_id', '=', self.production_id.id), ('foperno', '=', self.foperno), ('state', '!=', 'del')])
        totaltotalnum = 0
        for line in lines:
            totalnum = line.gqty + line.sqty + line.rqty
            totaltotalnum = totaltotalnum + totalnum

        attrition_rate = self.env['ck.attrition.rate'].search([('fnumber', '=', self.production_id.fnumber)], limit=1)
        if not attrition_rate:
            attrition_rate = self.env['ck.attrition.rate'].search([('fmodel', '=', self.production_id.fmodel)], limit=1)
        attrition_rate_val = 0
        if attrition_rate:
            attrition_rate_val = attrition_rate.attrition_rate

        if totaltotalnum > self.production_id.fqty * (attrition_rate_val*100 + 100)/100:
            raise exceptions.Warning(_('总数量超过工单数量，请检查数量是否正确。'))

        # _logger.debug("zhoufeng:  call check_if_excess end : %s" % (datetime.datetime.now()))
        '''

    @api.one
    def _compute_department(self):
        fworkcenter = self.env['ck.routing.sync'].search([('fworkcenterno', '=', self.fworkcenterno)], limit=1)
        self.department = fworkcenter.fworkcentername

    @api.one
    @api.depends('sqty', 'gqty')
    def _compute_price(self):
        if self.gqty:
            self.dogetprice()

    def dogetprice(self):
        # _logger.debug("zhoufeng:  call dogetprice start : %s" % (datetime.datetime.now()))
        '''
        totalnum = self.sqty + self.gqty

        passrate = round((self.gqty / totalnum), 4)

        self.fpass = passrate * 100
        '''
        # 客户和长编码
        price = self.env['ck.price.ext'].search([('fnumber', '=', self.production_id.fnumber),
                                                 ('foperno', '=', self.foperno),
                                                 '|', ('fshift', '=', self.fshift), ('fshift', '=', 'all'),
                                                 ('fmodel', '=', False),
                                                 ('fcustno', '=', self.production_id.fcustno),
                                                 '|', ('fmachine', '=', self.fmachine), ('fmachine', '=', 'all'),
                                                 ('fpass', '<=', self.fpass),
                                                 ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                 ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                 ],
                                                limit=1)
        if not price and self.production_id.fcustno:
            # 客户和长编码
            price = self.env['ck.price.ext'].search([('fnumber', '=', self.production_id.fnumber),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', self.fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', False),
                                                     ('fcustno', '=', self.production_id.fcustno.encode("utf-8")[0:4]),
                                                     '|', ('fmachine', '=', self.fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', self.fpass),
                                                     ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)
        if not price:
            # 客户和型号
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', self.fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', self.production_id.fmodel),
                                                     ('fcustno', '=', self.production_id.fcustno),
                                                     '|', ('fmachine', '=', self.fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', self.fpass),
                                                     (
                                                         'date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)
        if not price and self.production_id.fcustno:
            # 客户和型号
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', self.fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', self.production_id.fmodel),
                                                     ('fcustno', '=', self.production_id.fcustno.encode("utf-8")[0:4]),
                                                     '|', ('fmachine', '=', self.fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', self.fpass),
                                                     (
                                                         'date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)

        if not price:
            # 长编码
            price = self.env['ck.price.ext'].search([('fnumber', '=', self.production_id.fnumber),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', self.fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', False),
                                                     # ('fcustno', '=', False),
                                                     '|', ('fmachine', '=', self.fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', self.fpass),
                                                     (
                                                         'date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ], order='fcustno desc',
                                                    limit=1)
        if not price:
            # 型号
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', self.fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', self.production_id.fmodel),
                                                     # ('fcustno', '=', False),
                                                     '|', ('fmachine', '=', self.fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', self.fpass),
                                                     (
                                                         'date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ], order='fcustno desc',
                                                    limit=1)
        if not price:
            # 客户
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', self.fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', False),
                                                     ('fcustno', '=', self.production_id.fcustno),
                                                     '|', ('fmachine', '=', self.fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', self.fpass),
                                                     (
                                                         'date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)
        if not price:
            # 客户
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', self.fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', False),
                                                     # ('fcustno', '=', False),
                                                     '|', ('fmachine', '=', self.fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', self.fpass),
                                                     (
                                                         'date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ], order='fcustno desc',
                                                    limit=1)

        # print price

        if not price:
            raise exceptions.Warning(_('Price not fount!'))

        self.price = price.fprice

        if not price.fqty:
            raise exceptions.Warning(_('单价的数量为0，不能报工，请找单价维护人员进行修改!'))
        amount = round((price.fprice / price.fqty * self.gqty), 3)
        self.amount = amount
        return (price.fprice, amount)
        # _logger.debug("zhoufeng:  call dogetprice end : %s" % (datetime.datetime.now()))

    @api.multi
    def button_confirm_line(self):
        _logger.debug("zhoufeng:  call button_confirm_line start : %s" % (datetime.datetime.now()))
        if self.reportpeople:
            self.split_by_reportpeople()

        if self.state != 'done':
            self.check_if_excess()
            price, amount = self.dogetprice()

            # self.date_approve = datetime.datetime.now()
            # self.state = 'done'
            self.write({'price': price, 'amount': amount, 'date_approve': datetime.datetime.now(), 'state': 'done'})
            if self.order_id:
                self.order_id.uflag = not self.order_id.uflag
                self.order_id.check_complete()
        _logger.debug("zhoufeng:  call button_confirm_line end : %s" % (datetime.datetime.now()))
        return True

    @api.multi
    def split_by_reportpeople(self):
        reportpeoples = self.reportpeople.replace('\n', '').split(';')
        count = len(reportpeoples)
        everygqty = self.gqty // count
        counts = []
        if everygqty * count != self.gqty:
            i = 0
            for reportpeople in reportpeoples:
                counts.append(everygqty)
                i = i + 1
                if i == count:
                    counts[i - 1] = self.gqty - (i - 1) * everygqty
        else:
            i = 0
            for reportpeople in reportpeoples:
                counts.append(everygqty)
                i = i + 1

        i = 0
        for reportpeople in reportpeoples:
            reportpeopleone = reportpeople.split(':')
            userinfo = self.env['res.users'].search([('login', '=', reportpeopleone[0])], limit=1)
            userid = userinfo.id
            currentamount = self.price * counts[i] / 1000
            if i == 0:
                self.user_id = userid
                self.gqty = counts[i]
                self.amount = currentamount
            else:
                createinfo = {}
                createinfo['user_id'] = userid
                createinfo['reportpeople'] = self.reportpeople
                createinfo['gqty'] = counts[i]
                createinfo['price'] = self.price
                createinfo['pqty'] = self.pqty
                createinfo['amount'] = currentamount
                createinfo['fmachine'] = self.fmachine
                createinfo['fmachine_pre'] = self.fmachine_pre
                createinfo['fmodel'] = self.fmodel
                createinfo['fname'] = self.fname
                createinfo['fnumber'] = self.fnumber
                createinfo['fopername'] = self.fopername
                createinfo['foperno'] = self.foperno
                createinfo['fpass'] = 100
                createinfo['fshift'] = self.fshift
                createinfo['fshift_pre'] = self.fshift_pre
                createinfo['fworkcentername'] = self.fworkcentername
                createinfo['fworkcenterno'] = self.fworkcenterno
                createinfo['order_id'] = self.order_id.id
                createinfo['production_id'] = self.production_id.id
                createinfo['remark1'] = self.remark1
                createinfo['remark2'] = self.remark2
                createinfo['remark3'] = self.remark3
                createinfo['remark4'] = self.remark4
                createinfo['rqty'] = 0
                createinfo['rqty_pre'] = self.rqty_pre
                createinfo['sqty'] = 0
                createinfo['sqty_pre'] = self.sqty_pre
                createinfo['date_approve'] = datetime.datetime.now()
                createinfo['state'] = 'done'
                line = self.env['ck.hours.worker.line'].create(createinfo)
                line.fshift = self.fshift
                line.fmachine = self.fmachine
            i = i + 1

    @api.one
    @api.depends('sqty', 'gqty')
    def _compute_amount(self):
        # if self.state != 'done':
        amount = 0
        price = 0
        if not self.fnumber:
            self.fnumber = self.production_id.fnumber or False
        if not self.fname:
            self.fname = self.production_id.fname or False
        if not self.user_id:
            self.user_id = self.env.user
        if self.gqty > 0:
            price_obj = self.env['ck.price']
            dom = [('date_start', '<=', fields.Date.today()), ('date_stop', '>=', fields.Date.today()),
                   ('company_id', '=', self.company_id.id), ('foperno', '=', self.foperno)]
            price_ids = price_obj.search(dom)
            if any(price_ids):
                price = price_ids[0].fprice
                amount = self.gqty * price / price_ids[0].fqty
        # self.amount = amount
        # self.price = price

    def unlink(self, cr, uid, ids, context=None):
        if ids:
            for rec in self.browse(cr, uid, ids, context=context):
                rec.state = 'del'
                # new_id = super(CK_Hours_Worker_line, self).unlink(cr, uid, ids, context)
                rec.order_id.check_number()
                if len(rec.order_id.lines) == 0:
                    rec.order_id.unlink()
                # else:
                # rec.order_id = ''
                # obj.write_uid = uid.id
                # obj.write_date = datetime.datetime.now()
        return True

    '''
    def unlink(self, cr, uid, ids, context=None):
        if ids:
            for rec in self.browse(cr, uid, ids, context=context):
                rec.state = 'del'
                rec.order_id.check_number()
                if len(rec.order_id.lines) == 0:
                    rec.order_id.state = 'del'
                # else:
                # rec.order_id = ''
                # obj.write_uid = uid.id
                # obj.write_date = datetime.datetime.now()
        return True
    '''

    @api.model
    def create(self, vals):
        if vals.get('user_id', False) == False:
            vals['user_id'] = self._uid

        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('ck.hours.worker.line') or '/'
        import_flag = self.env.context.get('batch_import', False)
        if vals.get('batch_import', False):
            if not import_flag:
                self = self.with_context(batch_import=True)
            import_flag = True
            vals.pop('batch_import')

        if import_flag == False:
            production_id = self.env['ck.icmo.sync'].browse([vals['production_id']])
            vals['fnumber'] = production_id.fnumber
            vals['fname'] = production_id.fname

            now_time = datetime.datetime.strptime(datetime.datetime.now().
                                                  replace(tzinfo=pytz.utc).
                                                  astimezone(pytz.timezone(self.env.user.tz)).
                                                  strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            shifts = self.env['ck.shift'].search([('fshift', '=', 'day')])

            for shift in shifts:
                if shift.fshift == 'day':
                    date_start = shift.date_start
                    date_stop = shift.date_stop

                    mystarttime = datetime.datetime.now().strftime('%Y-%m-%d')
                    if len(date_start) == 8:
                        mystarttime = mystarttime + ' ' + date_start
                    if len(date_start) < 8:
                        mystarttime = mystarttime + ' ' + date_start + ':00'

                    mystoptime = datetime.datetime.now().strftime('%Y-%m-%d')
                    if len(date_stop) == 8:
                        mystoptime = mystoptime + ' ' + date_stop
                    if len(date_stop) < 8:
                        mystoptime = mystoptime + ' ' + date_stop + ':00'

                    myrealstarttime = datetime.datetime.strptime(mystarttime, '%Y-%m-%d %H:%M:%S')
                    myrealstoptime = datetime.datetime.strptime(mystoptime, '%Y-%m-%d %H:%M:%S')

                    if now_time >= myrealstarttime and now_time <= myrealstoptime:
                        vals['fshift'] = 'day'
                    else:
                        vals['fshift'] = 'night'

            # print now_time

            if vals['gqty']:
                totalnum = float(vals['rqty'] + vals['sqty'] + vals['gqty'])
                passrate = round((float(vals['gqty']) / totalnum), 4)
                vals['fpass'] = passrate * 100

            lines = self.env['ck.hours.worker.line'].search([('production_id', '=', production_id.id), ('foperno', '=', vals['foperno']), ('state', '!=', 'del')])

            totaltotalnum = vals['sqty'] + vals['gqty'] + vals['rqty']
            for line in lines:
                totalnum = line.gqty + line.sqty + line.rqty
                totaltotalnum = totaltotalnum + totalnum

            attrition_rate = self.env['ck.attrition.rate'].search([('fnumber', '=', production_id.fnumber)], limit=1)
            if not attrition_rate:
                attrition_rate = self.env['ck.attrition.rate'].search([('fmodel', '=', production_id.fmodel)], limit=1)
            attrition_rate_val = 0
            if attrition_rate:
                attrition_rate_val = attrition_rate.attrition_rate

            if totaltotalnum > production_id.fqty * (attrition_rate_val * 100 + 100) / 100:
                raise exceptions.Warning(_('总数量超过工单数量，请检查数量是否正确。'))

            vals['sqty_pre'] = vals['sqty']
            vals['gqty_pre'] = vals['gqty']
            vals['rqty_pre'] = vals['rqty']
            vals['fshift_pre'] = vals['fshift']
            vals['fmachine_pre'] = vals['fmachine']

            if not vals['order_id']:
                valshead = {}
                valshead['production_id'] = vals['production_id']
                valshead['user_id'] = vals['user_id']
                valshead['fnumber'] = production_id.fnumber
                valshead['fname'] = production_id.fname
                valshead['foperno'] = vals['foperno']
                valshead['fopername'] = vals['fopername']
                valshead['fworkcenterno'] = vals['fworkcenterno']
                valshead['fworkcentername'] = vals['fworkcentername']
                totalqty = vals['sqty'] + vals['gqty'] + vals['rqty']
                valshead['pqty'] = totalqty
                valshead['gqty'] = vals['gqty']
                valshead['sqty'] = vals['gqty'] + vals['sqty']
                # valshead['price'] = vals['price']
                # valshead['amount'] = vals['amount']
                newhead_id = self.env['ck.hours.worker'].create(valshead)

                vals['order_id'] = newhead_id.id

        new_id = super(CK_Hours_Worker_line, self).create(vals)
        new_id.order_id.check_number()
        # newhead_id.price = new_id.price
        # newhead_id.amount_total = new_id.amount
        return new_id

    @api.multi
    def write(self, vals):
        _logger.debug("zhoufeng:  call line write start : %s" % (datetime.datetime.now()))
        import_flag = self.env.context.get('batch_import', False)
        if vals.get('batch_import', False):
            if not import_flag:
                self = self.with_context(batch_import=True)
            import_flag = True
            vals.pop('batch_import')
        res = super(CK_Hours_Worker_line, self).write(vals)

        # if vals.has_key('gqty') | vals.has_key('sqty') | vals.has_key('rqty'):
        if 'gqty' in vals.keys() or 'sqty' in vals.keys() or 'rqty' in vals.keys():
            updatefpass = False
            for key in vals.keys():
                if key == 'fpass':
                    updatefpass = True
                else:
                    updatefpass = False
            if updatefpass:
                _logger.debug("zhoufeng:  call line write end 1 : %s" % (datetime.datetime.now()))
                return res

            order_id = self.order_id
            t_gqty = 0
            t_sqty = 0
            t_rqty = 0
            amount_total = 0
            complete = True
            for line in order_id.lines:
                t_gqty += line.gqty
                t_sqty += line.sqty
                amount_total += line.amount or 0
                if line.state == 'new':
                    complete = False
            amount_qty = t_gqty + t_sqty + t_rqty
            if amount_qty > 0 and complete:
                price = amount_total / amount_qty if amount_qty > 0 else 0
                order_id.write({'pqty': amount_qty, 'gqty': t_gqty,
                                'sqty': t_sqty, 'rqty': t_rqty,
                                'price': price, 'amount_total': amount_total})
            else:
                order_id.write({'pqty': amount_qty, 'gqty': t_gqty,
                                'sqty': t_sqty, 'rqty': t_rqty})

            if import_flag == False:

                # order_id.pqty = totalqty
                # order_id.gqty = self.gqty
                # order_id.sqty = self.sqty
                domain2 = []
                domain3 = []
                domain = []
                domain.append(('state', '!=', 'del'))
                if self.production_id:
                    domain.append(('production_id', '=', self.production_id.id))
                    domain.append(('foperno', '=', self.foperno))
                    domain2.append(('fnumber', '=', self.production_id.fnumber))
                    domain3.append(('fmodel', '=', self.production_id.fmodel))
                else:
                    domain.append(('production_id', '=', self.order_id.production_id.id))
                    domain.append(('foperno', '=', self.order_id.foperno))
                    domain2.append(('fnumber', '=', self.order_id.production_id.fnumber))
                    domain3.append(('fmodel', '=', self.order_id.production_id.fmodel))
                lines = self.env['ck.hours.worker.line'].search(domain)
                totaltotalnum = 0
                for line in lines:
                    totalnum = line.gqty + line.sqty + line.rqty
                    totaltotalnum = totaltotalnum + totalnum
                attrition_rate = self.env['ck.attrition.rate'].search(domain2, limit=1)
                if not attrition_rate:
                    attrition_rate = self.env['ck.attrition.rate'].search(domain3, limit=1)
                attrition_rate_val = 0
                if attrition_rate:
                    attrition_rate_val = attrition_rate.attrition_rate

                if self.gqty:
                    totalnum = float(self.rqty + self.sqty + self.gqty)
                    passrate = round((float(self.gqty) / totalnum), 4)
                    if self.fpass != passrate * 100:
                        self.fpass = passrate * 100
                else:
                    if self.fpass != 0:
                        self.fpass = 0

                if self.production_id:
                    if totaltotalnum > self.production_id.fqty * (attrition_rate_val * 100 + 100) / 100:
                        raise exceptions.Warning(_('总数量超过工单数量，请检查数量是否正确。'))
                else:
                    if self.order_id:
                        if totaltotalnum > self.order_id.production_id.fqty * (attrition_rate_val * 100 + 100) / 100:
                            raise exceptions.Warning(_('总数量超过工单数量，请检查数量是否正确。'))

        _logger.debug("zhoufeng:  call line write end 2 : %s" % (datetime.datetime.now()))

        return res

    def dogetpriceforchange(self, gqty, sqty, fshift, fmachine):
        totalnum = sqty + gqty

        passrate = round((gqty / totalnum), 4)

        fpass = passrate * 100

        # 客户和长编码
        price = self.env['ck.price.ext'].search([('fnumber', '=', self.production_id.fnumber),
                                                 ('foperno', '=', self.foperno),
                                                 '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                 ('fmodel', '=', False),
                                                 ('fcustno', '=', self.production_id.fcustno),
                                                 '|', ('fmachine', '=', fmachine), ('fmachine', '=', 'all'),
                                                 ('fpass', '<=', fpass),
                                                 ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                 ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                 ],
                                                limit=1)

        if not price:
            # 客户和型号
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', self.production_id.fmodel),
                                                     ('fcustno', '=', self.production_id.fcustno),
                                                     '|', ('fmachine', '=', fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', fpass),
                                                     ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)

        if not price:
            # 长编码
            price = self.env['ck.price.ext'].search([('fnumber', '=', self.production_id.fnumber),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', False),
                                                     ('fcustno', '=', False),
                                                     '|', ('fmachine', '=', fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', fpass),
                                                     ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)
        if not price:
            # 型号
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', self.production_id.fmodel),
                                                     ('fcustno', '=', False),
                                                     '|', ('fmachine', '=', fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', fpass),
                                                     ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)
        if not price:
            # 客户
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', False),
                                                     ('fcustno', '=', self.production_id.fcustno),
                                                     '|', ('fmachine', '=', fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', fpass),
                                                     ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)
        if not price:
            # 客户
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', False),
                                                     ('fcustno', '=', False),
                                                     '|', ('fmachine', '=', fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', fpass),
                                                     ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)
        # 客户和长编码
        price = self.env['ck.price.ext'].search([('fnumber', '=', self.production_id.fnumber),
                                                 ('foperno', '=', self.foperno),
                                                 '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                 ('fmodel', '=', False),
                                                 ('fcustno', '=', self.production_id.fcustno),
                                                 '|', ('fmachine', '=', fmachine), ('fmachine', '=', 'all'),
                                                 ('fpass', '<=', fpass),
                                                 ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                 ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                 ],
                                                limit=1)

        if not price:
            # 客户和型号
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', self.production_id.fmodel),
                                                     ('fcustno', '=', self.production_id.fcustno),
                                                     '|', ('fmachine', '=', fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', fpass),
                                                     ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)

        if not price:
            # 长编码
            price = self.env['ck.price.ext'].search([('fnumber', '=', self.production_id.fnumber),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', False),
                                                     ('fcustno', '=', False),
                                                     '|', ('fmachine', '=', fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', fpass),
                                                     ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)
        if not price:
            # 型号
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', self.production_id.fmodel),
                                                     ('fcustno', '=', False),
                                                     '|', ('fmachine', '=', fmachine), ('fmachine', '=', 'all'),
                                                     ('fpass', '<=', fpass),
                                                     ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)
        if not price:
            # 客户
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', False),
                                                     ('fcustno', '=', self.production_id.fcustno),
                                                     '|', ('fmachine', '=', fmachine), ('fmachine', '=', False),
                                                     ('fpass', '<=', fpass),
                                                     ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)
        if not price:
            # 客户
            price = self.env['ck.price.ext'].search([('fnumber', '=', False),
                                                     ('foperno', '=', self.foperno),
                                                     '|', ('fshift', '=', fshift), ('fshift', '=', 'all'),
                                                     ('fmodel', '=', False),
                                                     ('fcustno', '=', False),
                                                     '|', ('fmachine', '=', fmachine), ('fmachine', '=', False),
                                                     ('fpass', '<=', fpass),
                                                     ('date_start', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
                                                     ('date_stop', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                                     ],
                                                    limit=1)

        # print price

        returninfo = {}

        if not price:
            returninfo['errormsg'] = _('Price not fount!')

        if price:
            amount = round((price.fprice * gqty / price.fqty), 3)
            returninfo['price'] = price.fprice
            returninfo['amount'] = amount
            returninfo['fqty'] = price.fqty

        return returninfo

    @api.multi
    def change_info_on_approve(self, gqty, sqty, fshift, fmachine):
        return self.dogetpriceforchange(gqty, sqty, fshift, fmachine)


class CK_User_Weixin(models.Model):
    _name = 'ck.user.weixin'
    _description = _("Weixin user Map")
    _order = "company_id, user_id, date_active"
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.users'].browse(self._uid).company_id.id
                                 )  # 公司
    open_id = fields.Char(string=_('Weixin ID'))  # 微信UUID
    user_id = fields.Many2one('res.users', _('Owner'), readonly=False)  # 用户ID
    password = fields.Char(string=_('Password'), size=32, required=False)  # 密码
    date_active = fields.Datetime(string=_('Valid Date'), readonly=True, default=lambda self: fields.datetime.now())  # 绑定日期

    _sql_constraints = [
        ("user_weixin_unique", "unique(company_id, user_id)",
         _("Duplicated User"))
    ]


class CK_Price_Ext(models.Model):
    _name = 'ck.price.ext'
    _description = _("Work Price extend")
    _order = "company_id,fpass desc, fmodel, fitemid, froutingno, foperno"

    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.users'].browse(self._uid).company_id.id
                                 )  # 公司
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency',
                                  related="company_id.currency_id")  # 币别
    fitemid = fields.Integer(string=_('ProductID'))  # 产品ID
    fnumber = fields.Char(string=_('ProductNo'))  # 产品编码（长）
    fname = fields.Char(string=_('ProductDesc'))  # 产品描述
    fmodel = fields.Char(string=_('ProductModel'), index=True)  # 产品规格
    fshift = fields.Selection([('all', _('All')), ('day', _('白班')), ('night', _('晚班'))],
                              string=_('Shift'), default='day')  # 班次
    fmachine = fields.Selection([('all', _('All')), ('one', _('单机')), ('multi', _('双机'))],
                                string=_('Number of machines'), default='one')  # 机台数量
    fpass = fields.Float(string=_('Pass rate'), default=100.00)  # 合格率
    fcustid = fields.Integer(string=_('CustmerID'))  # 客户ID
    fcustno = fields.Char(string=_('CustmerNo'))  # 客户编号
    froutingid = fields.Integer(string=_('RoutingID'))  # 工艺路线ID
    froutingno = fields.Char(string=_('RoutingNo'))  # 工艺编码
    froutingname = fields.Char(string=_('RoutingName'))  # 工艺名称
    foperid = fields.Integer(string=_('OperationID'))  # 工序ID
    foperno = fields.Char(string=_('OperationNo'), index=True)  # 工序编码
    fopername = fields.Char(string=_('OperationName'))  # 工序名称
    funit = fields.Char(string=_('Unit'), required=True, default='PCS')  # 产品单位
    fqty = fields.Float(string=_('Quantity'))  # 任务单数量
    fbase_price = fields.Float(digits=dp.get_precision('ck_workprice_digit'), string=_('Base Price'))  # 基准价格
    fprice = fields.Float(digits=dp.get_precision('ck_workprice_digit'), string=_('WorkPrice'))  # 价格
    date_start = fields.Date('Valid From', default=fields.Date.today())  # 生效开始日期
    date_stop = fields.Date('Valid Until', default=fields.Date.from_string('9999-12-31'))  # 生效结束日期

    @api.one
    @api.onchange('fcustid')
    def change_fcustid(self):
        if self.fcustid:
            icmo_ids = self.env['ck.icmo.sync'].search([('fcustid', '=', self.fcustid)], limit=1)
            if any(icmo_ids):
                self.fcustno = icmo_ids[0].fcustno

    @api.one
    @api.onchange('fcustno')
    def change_fcustno(self):
        if self.fcustno:
            icmo_ids = self.env['ck.icmo.sync'].search([('fcustno', '=', self.fcustno)], limit=1)
            if any(icmo_ids):
                self.fcustid = icmo_ids[0].fcustid

    @api.one
    @api.onchange('fitemid')
    def change_fitemid(self):
        if self.fitemid:
            foper_ids = self.env['ck.icmo.sync'].search([('fitemid', '=', self.fitemid)], limit=1)
            if any(foper_ids):
                self.fnumber = foper_ids[0].fnumber
                self.fname = foper_ids[0].fname

    @api.one
    @api.onchange('fnumber')
    def change_fnumber(self):
        if self.fnumber:
            foper_ids = self.env['ck.icmo.sync'].search([('fnumber', '=', self.fnumber)], limit=1)
            if any(foper_ids):
                self.fitemid = foper_ids[0].fitemid
                self.fname = foper_ids[0].fname

    @api.one
    @api.onchange('foperno')
    def change_foperno(self):
        if self.foperno:
            foper_ids = self.env['ck.routing.sync'].search([('foperno', '=', self.foperno)], limit=1)
            if any(foper_ids):
                self.fopername = foper_ids[0].fopername
                self.foperid = foper_ids[0].foperid

    @api.one
    @api.onchange('foperid')
    def change_foperid(self):
        if self.foperid:
            foper_ids = self.env['ck.routing.sync'].search([('foperid', '=', self.foperid)], limit=1)
            if any(foper_ids):
                self.fopername = foper_ids[0].fopername
                self.foperno = foper_ids[0].foperno

    @api.one
    @api.onchange('froutingno')
    def change_froutingno(self):
        if self.froutingno:
            foper_ids = self.env['ck.routing.sync'].search([('froutingno', '=', self.froutingno)], limit=1)
            if any(foper_ids):
                self.froutingname = foper_ids[0].froutingname
                self.froutingid = foper_ids[0].froutingid

    @api.one
    @api.onchange('froutingid')
    def change_froutingid(self):
        if self.froutingid:
            foper_ids = self.env['ck.routing.sync'].search([('froutingid', '=', self.froutingid)], limit=1)
            if any(foper_ids):
                self.froutingname = foper_ids[0].froutingname
                self.froutingno = foper_ids[0].froutingno

    @api.one
    @api.onchange('fbase_price')
    def change_fbase_price(self):
        self.change_work_price()

    @api.one
    @api.onchange('fshift')
    def change_fshift(self):
        self.change_work_price()

    @api.one
    @api.onchange('fmachine')
    def change_fmachine(self):
        self.change_work_price()

    def change_work_price(self):
        if self.fbase_price:
            fshiftinfo = self.env['ck.shift'].search([('fshift', '=', self.fshift)], limit=1)
            fmachineinfo = self.env['ck.machine'].search([('fmachine', '=', self.fmachine)], limit=1)

            if fshiftinfo and fmachineinfo:
                self.fprice = self.fbase_price * fshiftinfo.rate * fmachineinfo.rate


class ck_shift(models.Model):
    _name = 'ck.shift'
    _description = _("Classes Info")

    fshift = fields.Selection([('all', _('All')), ('day', _('白班')), ('night', _('晚班'))],
                              string=_('Shift'), default='day')  # 班次
    date_start = fields.Char(string=_('From'))  # 开始时间
    date_stop = fields.Char(string=_('To'))  # 结束时间

    rate = fields.Float(string=_('Rate'), default=1)  # rate比率

    _sql_constraints = [
        ('fshift_uniq', 'unique(fshift)', 'Shift Must unique!'),
    ]


class ck_machine(models.Model):
    _name = 'ck.machine'
    _description = _("Machine Info")

    fmachine = fields.Selection([('all', _('All')), ('one', _('单机')), ('multi', _('双机'))],
                                string=_('Number of machines'), default='one')  # 机台数量

    rate = fields.Float(string=_('Rate'), default=1)  # rate比率

    _sql_constraints = [
        ('fmachine_uniq', 'unique(fmachine)', 'Machine Must unique!'),
    ]


class ck_pass_rate(models.Model):
    _name = 'ck.pass.rate'
    _description = _("Pass Rate Info")

    _order = "fpass desc"

    fpass = fields.Float(string=_('Pass rate'))  # 合格率

    rate = fields.Float(string=_('Rate'), default=1)  # rate比率

    _sql_constraints = [
        ('fpass_uniq', 'unique(fpass)', 'Machine Must unique!'),
    ]


class ck_attrition_rate(models.Model):
    _name = 'ck.attrition.rate'
    _description = _("Attrition Rate Info")

    fitemid = fields.Integer(string=_('ProductID'))  # 产品ID
    fnumber = fields.Char(string=_('ProductNo'))  # 产品编码（长）
    fname = fields.Char(string=_('ProductDesc'))  # 产品描述

    fmodel = fields.Char(string=_('ProductModel'))  # 产品规格

    attrition_rate = fields.Float(string=_('Attrition rate'))  # 损耗率
    attrition_key = fields.Char(string="Key")

    @api.one
    @api.onchange('fitemid')
    def change_fitemid(self):
        if self.fitemid:
            foper_ids = self.env['ck.icmo.sync'].search([('fitemid', '=', self.fitemid)], limit=1)
            if any(foper_ids):
                self.fnumber = foper_ids[0].fnumber
                self.fname = foper_ids[0].fname

    @api.one
    @api.onchange('fnumber')
    def change_fnumber(self):
        if self.fnumber:
            foper_ids = self.env['ck.icmo.sync'].search([('fnumber', '=', self.fnumber)], limit=1)
            if any(foper_ids):
                self.fitemid = foper_ids[0].fitemid
                self.fname = foper_ids[0].fname


class ck_route_scrap_reasons(models.Model):
    _name = 'ck.route.scrap.reasons'
    _description = _("Scrap Reason")

    foperno = fields.Char(string=_('OperationNo'))  # 工序编码
    fopername = fields.Char(string=_('OperationName'))  # 工序名称
    reason = fields.Char(string=_('Reason'))  # 原因

    _sql_constraints = [
        ("ck_route_scrap_reasons_unique", "unique(foperno,reason)", _("工序原因不能重复。"))
    ]

    @api.one
    @api.onchange('foperno')
    def change_foperno(self):
        if self.foperno:
            foper_ids = self.env['ck.routing.sync'].search([('foperno', '=', self.foperno)], limit=1)
            if any(foper_ids):
                self.fopername = foper_ids[0].fopername


class ck_route_scrap_reasons_line(models.Model):
    _name = 'ck.route.scrap.reasons.line'
    _description = _("Scrap Reason")

    order_id = fields.Many2one(comodel_name='ck.hours.worker.line', ondelete='cascade', string='Order Reference', select=True)  # 报工单
    reason = fields.Char(string=_('Reason'))  # 原因
    qty = fields.Float(string=_('Quantity'), store=True)  # 报废数量

    rate = fields.Float(compute='_compute_rate', string=_('Rate'), default=0, store=True)

    def _compute_rate(self):
        print(self)
        return 1


class ck_user_worktime(models.Model):
    _name = 'ck.user.work.time'
    _description = _("Work Time")

    user_id = fields.Many2one('res.users', _('Owner'), readonly=False)  # 用户ID
    worktime = fields.Float(string=_('Work Time'))  # 工时
    remark = fields.Char(string=_('Remark'))  # 备注1
    date_worker = fields.Datetime(string=_('Report Time'), default=lambda self: fields.datetime.now())  # 报工时间
    state = fields.Selection(
        [('new', _('New')), ('done', _('Done')), ('del', _('Delete'))], _('State'),
        readonly=False, default='new')  # 状态

    department = fields.Char(compute='_compute_department', store=True, string=_('部门'))

    @api.one
    @api.depends('user_id', 'state')
    def _compute_department(self):
        if self.user_id.employee_ids:
            self.department = self.user_id.employee_ids[0].department_id.complete_name

    def _search_department(self, opeartor, value):
        employees = self.env['hr.employee'].search(['|', ('department_id', opeartor, value), ('department_id.parent_id', opeartor, value)])
        ids = [employee.user_id.id for employee in employees]
        return [('user_id', 'in', ids)]

    @api.multi
    def search_by_useridanddatetime(self, start_date, end_date):
        # start_date = '2017-06-15'
        # end_date = '2017-06-21'
        startdate = (datetime.datetime.strptime(start_date, '%Y-%m-%d')).replace(
            tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
        enddate = (datetime.datetime.strptime(end_date, '%Y-%m-%d')).replace(
            tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
        start_date = startdate.strftime('%Y-%m-%d %H:%M:%S')
        end_date = enddate.strftime('%Y-%m-%d %H:%M:%S')
        thisinfos = self.env['ck.user.work.time'].search(
            [('user_id', '=', self._uid), ('date_worker', '>=', start_date), ('date_worker', '<', end_date)])
        l = {}
        totaltime = 0
        for line in thisinfos:
            totaltime += line.worktime

        l['totaltime'] = totaltime
        return l

    @api.multi
    def search_by_useridanddatetimeline(self, start_date, end_date):
        # start_date = '2017-06-15'
        # end_date = '2017-06-21'
        startdate = (datetime.datetime.strptime(start_date, '%Y-%m-%d')).replace(
            tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
        enddate = (datetime.datetime.strptime(end_date, '%Y-%m-%d')).replace(
            tzinfo=pytz.timezone(self.env.user.tz)).astimezone(pytz.timezone(pytz.utc.zone))
        start_date = startdate.strftime('%Y-%m-%d %H:%M:%S')
        end_date = enddate.strftime('%Y-%m-%d %H:%M:%S')
        thisinfos = self.env['ck.user.work.time'].search(
            [('user_id', '=', self._uid), ('date_worker', '>=', start_date), ('date_worker', '<', end_date)])
        l = []
        totaltime = 0
        for line in thisinfos:
            ml = {}
            ml['user_id'] = line.user_id.id  # 用户
            ml['login'] = line.user_id.login  # 用户登录名
            ml['name'] = line.user_id.name  # 用户名
            ml['worktime'] = line.worktime  # 时长
            ml['remark'] = line.remark  # 备注
            ml['date_worker'] = line.date_worker  # 时间
            ml['state'] = line.state  # 状态
            l.append(ml)
        return l

    @api.multi
    def unlink(self):
        for line in self:
            line.state = 'del'
        return True

    @api.model
    def create(self, vals):
        domain = [('user_id', '=', vals['user_id']), ('worktime', '=', vals['worktime']), ('remark', '=', vals['remark']), ('date_worker', '=', vals['date_worker'])]
        search = self.search(domain, limit=1)
        if search:
            return search
        else:
            res = super(ck_user_worktime, self).create(vals)
            return res


class ck_material_scrap_reasons(models.Model):
    _name = 'ck.material.scrap.reasons'
    _description = _("Scrap Reason")

    foperno = fields.Char(string=_('OperationNo'))  # 工序编码
    fopername = fields.Char(string=_('OperationName'))  # 工序名称
    reason = fields.Char(string=_('Reason'))  # 原因

    _sql_constraints = [
        ("ck_route_scrap_reasons_unique", "unique(foperno,reason)", _("工序原因不能重复。"))
    ]

    @api.one
    @api.onchange('foperno')
    def change_foperno(self):
        if self.foperno:
            foper_ids = self.env['ck.routing.sync'].search([('foperno', '=', self.foperno)], limit=1)
            if any(foper_ids):
                self.fopername = foper_ids[0].fopername


class ck_material_scrap_reasons_line(models.Model):
    _name = 'ck.material.scrap.reasons.line'
    _description = _("Scrap Reason")

    order_id = fields.Many2one(comodel_name='ck.hours.worker.line', ondelete='cascade', string='Order Reference',
                               select=True)  # 报工单
    reason = fields.Char(string=_('Reason'))  # 原因
    qty = fields.Float(string=_('Quantity'), store=True)

    rate = fields.Float(compute='_compute_rate', string=_('Rate'), default=0, store=True)

    def _compute_rate(self):
        print(self)
        return 1
