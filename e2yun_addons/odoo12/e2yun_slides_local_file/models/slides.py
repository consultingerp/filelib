# -*- coding: utf-8 -*-
# Part of e2yun. See LICENSE file for full copyright and licensing details.


import mimetypes
from odoo import api, fields, models, SUPERUSER_ID, _


class Slide(models.Model):
    _inherit = 'slide.slide'

    datas = fields.Binary(filename="datas_fname")
    datas_fname = fields.Char("File Name")

    def _get_embed_code(self):
        super(Slide, self)._get_embed_code()
        for record in self:
            if record.slide_type == 'video':
                if record.datas and record.mime_type == "local":
                    object = self.env['ir.attachment'].search(
                        [('res_model', '=', record._name),
                         ('res_field', '=', 'datas'),
                         ('res_id', '=', record.id)], limit=1)
                    if object:
                        record.embed_code = """
                            <iframe frameborder="0" width="640" height="498"
                                src="%s"
                                allowfullscreen></iframe>
                        """ % (object.local_url)
            elif record.slide_type == 'document':
                if record.datas and record.mime_type == "local":
                    object = self.env['ir.attachment'].search(
                        [('res_model', '=', record._name),
                         ('res_field', '=', 'datas'),
                         ('res_id', '=', record.id)], limit=1)
                    if object:
                        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url','http://e2yun.com')
                        record.embed_code = """
                            <iframe frameborder="0" width="640" height="498"
                                src="https://view.officeapps.live.com/op/embed.aspx?src=%s%s"
                                allowfullscreen></iframe>
                        """ % (base_url, object.local_url)

    @api.onchange('datas')
    def on_change_datas(self):
        self.ensure_one()
        if self.datas:
            self['mime_type'] = "local"

    @api.onchange('datas_fname')
    def on_change_datas_fname(self):
        self.ensure_one()
        if self.datas_fname:
            mimetype = mimetypes.guess_type(self.datas_fname)[0]
            if 'image' in mimetype:
                self.slide_type = 'infographic'
            elif 'pdf' in mimetype:
                self.slide_type = 'presentation'
            elif 'text' in mimetype or 'javascript' in mimetype:
                self.slide_type = 'document'
            elif 'video' in mimetype or 'audio' in mimetype:
                self.slide_type = 'video'


    @api.model
    def create(self, values):
        slide = super(Slide, self).create(values)
        atts = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', self._name),
            ('res_field', '=', 'datas'),
            ('res_id', '=', slide.id),
        ], limit=1)
        if atts and atts.datas and not atts.datas_fname:
            mimetype = mimetypes.guess_type(slide.datas_fname)[0]
            atts.write({'datas_fname': slide.datas_fname, 'mimetype': mimetype})
        return slide

    @api.multi
    def write(self, values):
        res = super(Slide, self).write(values)
        for record in self:
            atts = record.env['ir.attachment'].sudo().search([
                ('res_model', '=', record._name),
                ('res_field', '=', 'datas'),
                ('res_id', '=', record.id),
                ], limit=1)
            if atts:
                if 'datas' in values or 'datas_fname' in values:
                    atts.write({'datas_fname': record.datas_fname, 'datas': record.datas})
                if (record.document_id != str(atts.id) and
                        record.datas and record.mime_type == "local"):
                    record.write({'document_id': atts.id})
        return res
