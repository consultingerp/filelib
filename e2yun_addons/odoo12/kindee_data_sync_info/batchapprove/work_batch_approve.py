# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class ck_hours_worker_line_batch_approve(models.TransientModel):
    _name = 'ck.hours.worker.line.batch.approve'

    fshift = fields.Selection([('day', '白班'), ('night', '晚班')], string='班次', default='day')

    @api.multi
    def batch_approve_worker_line(self):
        active_ids = self.env.context.get('active_ids', [])
        lines = self.env['ck.hours.worker.line'].search([('id', 'in', active_ids), ('state', '=', 'new')])
        for line in lines:
            # state = 'done'
            # sqty = line.sqty
            # gqty = line.gqty
            # rqty = line.rqty
            # fshift = line.fshift
            # fmachine = line.fmachine
            if line.fshift != self.fshift:
                if self.fshift:
                    line.fshift = self.fshift
                    line.dogetprice()
            line.state = "done"
            line.order_id.state = "done"
            line.remark4 = "批量审批标识"
            line.date_approve = fields.datetime.now()
            # line._context['state'] = 'done'
            # line._context['sqty'] = line.sqty
            # line._context['gqty'] = line.gqty
            # line._context['rqty'] = line.rqty
            # line._context['fshift'] = line.fshift
            # line._context['fmachine'] = line.fmachine
            # line.button_confirm()

            # line.state = 'done'
            # line.order_id.state = 'done'
            # if line.order_id:
            #     line.order_id.uflag = not self.order_id.uflag
            #     line.order_id.check_complete()
