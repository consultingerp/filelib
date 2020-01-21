# -*- coding: utf-8 -*-

from odoo import models, fields, api,exceptions
from odoo import tools, _
from datetime import datetime

class delivery_order_rep_view(models.Model):
    _name = 'delivery.order.rep.view'
    _description = 'Delivery Order'

    versi = fields.Char('Version')
    datoo = fields.Date('Demand Date')
    menge = fields.Integer('Scheduling Qty')
    dnmeg = fields.Integer('Delivery Qty')
    prinu = fields.Integer('Print Qty')
    inmeg = fields.Integer('In Goods Qty')
    usmeg = fields.Integer('Used Qty')
    werks = fields.Many2one('stock.warehouse', 'Factory', required=True)
    comco = fields.Many2one('res.company', 'Company', required=True, readonly=True)
    lifnr = fields.Many2one('res.partner', 'Supplier', required=False, readonly=True, domain=[('supplier', '=', True)])
    allow_create_days = fields.Integer('Allow create days')
    isAllowCreate = fields.Boolean('isAllowCreate', compute='_get_isAllowCreate')
    isscheduledate = fields.Boolean('isscheduledate')
    isallownoschedulecreate = fields.Boolean('isallownoschedulecreate')

    _defaults = {
        'comco': lambda self: self.env['res.company']._company_default_get('delivery.order.rep'),
        'lifnr': lambda self: self.env['res.users']._get_default_supplier(),
        'menge':0,
        'dnmeg':0,
        'prinu':0,
        'inmeg':0,
        'usmeg':0,
        'isAllowCreate':True,
        'isscheduledate':True,
        'isallownoschedulecreate':True
    }


    def _get_isAllowCreate(self):
        for s in self:
            datoo = datetime.strptime(str(s.datoo), '%Y-%m-%d')
            nowstr = datetime.strftime(datetime.now(), '%Y-%m-%d')
            nowdate = datetime.strptime(nowstr, '%Y-%m-%d')
            if s.allow_create_days > 0 and (datoo - nowdate).days > s.allow_create_days:
                s.isAllowCreate = False
            else:
                s.isAllowCreate = True

    def get_last_day_data(self,comco,lifnr,datoo):
        self._cr.execute("select id from delivery_order_rep_view where (menge - coalesce(dnmeg,0)) > 0 and comco=%s and lifnr=%s and datoo < %s ", (comco, lifnr,datoo))
        data = self._cr.dictfetchall()
        if data and len(data) > 0:
            return True
        else:
            return False


    def search(self, args, offset=0, limit=None, order=None, count=False):
        ctx = self._context.copy()
        if args and len(args) > 0:

            if 'datoo' in self._context:
                args_id = 0
                for a in args:
                    if 'id' in a:
                        args_id = a[2]
                dev_obj = self.env['delivery.order.rep.view'].browse(int(args_id))
                if dev_obj:
                    datoo = dev_obj.datoo
                    werks = dev_obj.werks
                    isscheduledate= dev_obj.isscheduledate,
                    isallownoschedulecreate= dev_obj.isallownoschedulecreate,
                    versi= dev_obj.versi

                    ctx['datoo'] = datoo
                    ctx['isscheduledate'] = isscheduledate
                    ctx['isallownoschedulecreate'] = isallownoschedulecreate
                    ctx['versi'] = versi
                    ctx['werks'] = werks.id


            comco = self.env['res.company']._company_default_get('delivery.order.rep.view')
            lifnr = self.env['res.users']._get_default_supplier()
            args += [('comco', '=', comco.id), ('lifnr', '=', lifnr), ('usmeg', '>', 0)]

        else:
            comco = self.env['res.company']._company_default_get('delivery.order.rep.view')
            lifnr = self.env['res.users']._get_default_supplier()
            args += [('comco', '=', comco.id), ('lifnr', '=', lifnr), ('usmeg', '>', 0)]

            self._cr.execute("select id from delivery_order_rep_view where usmeg>0 and comco=%s and lifnr=%s",(comco.id,lifnr))
            unlinkids = self._cr.dictfetchall()
            if len(unlinkids)>0:
                for unlinkid in unlinkids:
                    self.browse(unlinkid['id']).unlink()

            # reps = self.env['delivery.order.rep'].search(args);
            # dict =[]
            # tablefield = ['versi', 'werks','datoo','menge','comco','lifnr','allow_create_days','dnmeg','prinu','inmeg','usmeg']
            #repValue = self.env['delivery.order.rep'].read(reps, tablefield)
            partner = self.env['res.partner'].browse(lifnr);
            replist = []
            isallownoschedulecreate = partner.allow_no_schedule_create;
            nowstr = datetime.strftime(datetime.now(), '%Y-%m-%d')
            nowdate = datetime.strptime(nowstr, '%Y-%m-%d')
            readonlyValue = True;
            todayHaveschedule = False
            if isallownoschedulecreate:
                readonlyValue=False;
            # for rep in repValue:
            #     if nowstr == str(rep['datoo']):
            #         todayHaveschedule = True;
            #     repMap = {
            #         'versi':str(rep['versi']),
            #         'werks':rep['werks'][0],
            #         'datoo': rep['datoo'],
            #         'menge': rep['menge'],
            #         'comco': rep['comco'][0],
            #         'lifnr': rep['lifnr'][0],
            #         'allow_create_days': rep['allow_create_days'],
            #         'dnmeg': rep['dnmeg'],
            #         'prinu': rep['prinu'],
            #         'inmeg': rep['inmeg'],
            #         'usmeg': rep['usmeg'],
            #         'isscheduledate':True,
            #         'isallownoschedulecreate':readonlyValue
            #     }
            #     replist.append(repMap)

            if partner.allow_no_schedule_create:
                werks =0
                allow_create_days = 0
                if len(replist)>0:
                    werks = replist[0]['werks'];
                    allow_create_days = replist[0]['allow_create_days'];
                else:

                    self._cr.execute("select allow_create_days from res_partner where id= %(lifnr)s ",{'lifnr':lifnr})
                    allow_create_daysOne = self._cr.fetchone()
                    allow_create_days = allow_create_daysOne[0]
                    self._cr.execute("select id from stock_warehouse where company_id= %(comco)s ", {'comco':comco.id})
                    werksOne = self._cr.fetchone()
                    werks = werksOne[0]
                map = {
                    'versi':'',
                    'werks':werks,
                    'datoo': nowdate,
                    'menge': 0,
                    'comco': comco.id,
                    'lifnr': lifnr,
                    'allow_create_days': allow_create_days,
                    'dnmeg': 0,
                    'prinu': 0,
                    'inmeg': 0,
                    'usmeg': 1,
                    'isscheduledate': False,
                    'isallownoschedulecreate': False
                }
                replist.append(map)
            for rep in replist:
                self.create(rep)

        return super(delivery_order_rep_view, self).search(args, offset=offset, limit=limit, order=order,count=count);

    @api.multi
    def create_delivery(self):
        id2 = self.env.ref('srm_delivery_order.srm_delivery_order_form')
        ctx=self._context.copy()
        ctx['werks'] = self.werks.id
        ctx['datoo'] = self.datoo
        ctx['isscheduledate'] = self.isscheduledate
        ctx['isallownoschedulecreate'] = self.isallownoschedulecreate
        ctx['versi'] = self.versi
        return {
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'delivery.order',
            'views': [(id2.id, 'form')],
            'view_id': id2.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context':ctx
        }

    @api.multi
    def check_create_delivery(self):
        # self.ensure_one()
        # days = self.lifnr.allow_create_days;
        # datoo = datetime.strptime(self.datoo, '%Y-%m-%d')
        # nowstr = datetime.strftime(datetime.now(), '%Y-%m-%d')
        # nowdate = datetime.strptime(nowstr, '%Y-%m-%d')
        # if days > 0 and (datoo - nowdate).days > days:
        #     raise exceptions.ValidationError("当前时间已经超出了允许创建的天数,允许创建交货单天数为：" + str(days) + "天。")


        if self.get_last_day_data(self.comco.id,self.lifnr.id,self.datoo) and self.versi:

            msg_obj = self.env['confirm.msg'].create(
                {'confirm_title': "提示",
                 'confirm_msg': "历史日期有未完成的排程交货，是否继续创建交货单?",
                 'previous_id': self[0].id,
                 'previous_type': self._name,
                 'previous_method': 'create_delivery'})
            if msg_obj:
                return msg_obj.do_confirm_action()
        else:
            return self.create_delivery()

