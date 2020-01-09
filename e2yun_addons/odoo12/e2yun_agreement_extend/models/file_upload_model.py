# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from odoo import api, fields, models, tools, _
import xlrd
import time

class AgreementFileUpload(models.TransientModel):
    _name = "agreement.file.upload"
    _description = "agreement file upload"

    name = fields.Selection((('pdfswy','PDF首尾页'), ('pdfqw','PDF全文版'), ('fktj','付款条件')), default="", string="The import type", required=True)
    data = fields.Binary('File', required=True)
    filename = fields.Char('File Name', required=True)

    @api.multi
    def import_file(self):
        this = self[0]
        attachment = self.env['ir.attachment']  # 附件
        name="self.filename"

        if self.name=='pdfswy':
            name='PDF首尾页'
        elif self.name=='pdfqw':
            name = 'PDF全文版'
        elif self.name == 'fktj':
            name = '付款条件'

        attachmentObj = attachment.create({
            'name': name,
            'datas': base64.encodestring(this.data),
            'datas_fname':self.filename,
            'res_model': self._context['active_model'],
            'res_id': self._context['active_id'],
            'res_name': self.name
        })

        return {'type': 'ir.actions.act_window_close'}



