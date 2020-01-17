# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from odoo import api, fields, models, tools, _
import xlrd
import time

class AgreementFileUpload(models.Model):
    _name = "agreement.file.upload"
    _description = "agreement file upload"

    name = fields.Selection((('pdfswy','PDF首尾页'), ('pdfqw','PDF全文版'), ('fktj','付款条件')), default="", string="The import type", required=True)
    data = fields.Binary('File', required=True)
    filename = fields.Char('File Name', required=True)

    @api.multi
    def import_file(self):
        this = self[0]
        attachment = self.env['ir.attachment']  # 附件
        name=self.filename
        res_name=""
        if self.name=='pdfswy':
            res_name='pdfswy'
        elif self.name=='pdfqw':
            res_name = 'pdfqw'
        elif self.name == 'fktj':
            res_name = 'fktj'

        agreement_id = self._context['active_id']

        # attachment.search([('res_model', '=', 'agreement.file.upload'),
        #                    ('res_id', '=', agreement_id),
        #                    ('res_name', '=', res_name)]).unlink()  # 删除无效附件

        sql = "select id  from ir_attachment where  res_id = %s  and res_name = %s and res_model = %s "
        self._cr.execute(sql, (agreement_id, res_name, 'agreement.file.upload'))
        attachmentSqlData = self._cr.fetchall()
        if attachmentSqlData:
            for d in attachmentSqlData:
                attachment.browse(d[0]).unlink()


        attachmentObj = attachment.create({
            'name': name,
            'datas': this.data,
            'datas_fname':name,
            'res_model': 'agreement.file.upload',
            'res_id': agreement_id,
            'res_name': res_name,
        })

        sql="update agreement set "+res_name+"=%s where id=%s"
        self._cr.execute(sql, (attachmentObj.id,agreement_id))
        return {'type': 'ir.actions.act_window_close'}



