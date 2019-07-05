# -*- coding: utf-8 -*-
# Part of e2yun. See LICENSE file for full copyright and licensing details.

from odoo import fields

class Binary(fields.Binary):

    def create(self, record_values):
        assert self.attachment
        if not record_values:
            return
        # create the attachments that store the values
        env = record_values[0][0].env
        with env.norecompute():
            for record, value in record_values:
                if value and 'datas_fname' in record:
                    env['ir.attachment'].sudo().with_context(
                        binary_field_real_user=env.user,
                    ).create([{
                            'name': self.name,
                            'res_model': self.model_name,
                            'res_field': self.name,
                            'res_id': record.id,
                            'type': 'binary',
                            'datas': value,
                            'datas_fname': record.datas_fname,
                        }

            ])

    def write(self, records, value):
        assert self.attachment

        with records.env.norecompute():
            if value:
                res_ids=[]
                # update the existing attachments
                for record in records:
                    atts = records.env['ir.attachment'].sudo().search([
                        ('res_model', '=', self.model_name),
                        ('res_field', '=', self.name),
                        ('res_id', '=', records.id),
                    ])
                    if atts:
                        atts.write({'datas': value,'datas_fname': record.datas_fname})
                        res_ids.append(atts.res_id)
                atts_records = records.browse(res_ids)
                # create the missing attachments
                if len(atts_records) < len(records):
                    for record in (records - atts_records):
                        if 'datas_fname' in record:
                            atts.create([{
                                    'name': self.name,
                                    'res_model': record._name,
                                    'res_field': self.name,
                                    'res_id': record.id,
                                    'type': 'binary',
                                    'datas': value,
                                    'datas_fname': record.datas_fname,
                                }

                            ])
            else:
                atts = records.env['ir.attachment'].sudo().search([
                    ('res_model', '=', self.model_name),
                    ('res_field', '=', self.name),
                    ('res_id', 'in', records.ids),
                ])
                atts.unlink()


    # def write(self, records, value):
    #     domain = [
    #         ('res_model', '=', records._name),
    #         ('res_field', '=', self.name),
    #         ('res_id', 'in', records.ids),
    #     ]
    #     atts = records.env['ir.attachment'].sudo().search(domain)
    #     if value and atts.url and atts.type == 'url' and not image.is_url(value):
    #         atts.write({
    #             'url': None,
    #             'type': 'binary',
    #         })
    #     if value and image.is_url(value):
    #         with records.env.norecompute():
    #             if value:
    #                 mimetype, content = get_mimetype_and_optional_content_by_url(value)
    #                 index_content = records.env['ir.attachment']._index(content, None, mimetype)
    #
    #                 # update the existing attachments
    #                 atts.write({
    #                     'url': value,
    #                     'mimetype': mimetype,
    #                     'datas': None,
    #                     'type': 'url',
    #                     'index_content': index_content,
    #                 })
    #
    #                 # create the missing attachments
    #                 for record in (records - records.browse(atts.mapped('res_id'))):
    #                     atts.create({
    #                         'name': self.name,
    #                         'res_model': record._name,
    #                         'res_field': self.name,
    #                         'res_id': record.id,
    #                         'type': 'url',
    #                         'url': value,
    #                         'mimetype': mimetype,
    #                         'index_content': index_content,
    #                     })
    #             else:
    #                 atts.unlink()
    #     else:
    #         super(Binary, self).write(records, value)
    #

fields.Binary = Binary
