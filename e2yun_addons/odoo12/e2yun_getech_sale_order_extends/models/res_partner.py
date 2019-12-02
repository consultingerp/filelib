# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api, exceptions
import datetime
import suds.client
import json


class Partner(models.Model):
    _inherit = 'res.partner'

    partner_code = fields.Char('编号', copy=False)
    vat = fields.Char(copy=False)

    is_company = fields.Boolean(default=True)

    _sql_constraints = [
        ('partner_code_unique', 'unique (partner_code)', "客户编号不能重复"),
        ('vat_unique', 'unique (vat,parent_id)', "统一社会信用代码不能重复"),
    ]

    @api.model
    def create(self, vals):
        if ('parent_id' in vals or not vals['parent_id']) and ('vat' in vals and vals['vat']):
            if self.search([('vat', '=', vals['vat'])]):
                raise exceptions.Warning("统一社会信用代码已经存在，不能重复，请检查数据！")
        res = super(Partner, self).create(vals)
        if 'partner_code' not in vals and not res.partner_code:
            if res.customer or res.supplier:
                if res.customer:
                    prefix = 'CUS'
                elif res.supplier:
                    prefix = 'VEN'
                name = self.env['ir.sequence'].get_next_code_info_if_no_create('res_partner', prefix, '', 7)
                res.partner_code = name
        elif 'partner_code' in vals and not vals['partner_code']:
            res.partner_code = vals['partner_code']
        return res

    @api.multi
    def write(self, vals):
        if (not self.parent_id) and ('vat' in vals and vals['vat']):
            if self.search([('vat', '=', vals['vat'])]):
                raise exceptions.Warning("统一社会信用代码已经存在，不能重复，请检查数据！")
        res = super(Partner, self).write(vals)
        for item in self:
            if not item.partner_code:
                if item.customer or item.supplier:
                    if item.customer:
                        prefix = 'CUS'
                    elif item.supplier:
                        prefix = 'VEN'
                    name = self.env['ir.sequence'].get_next_code_info_if_no_create('res_partner', prefix, '', 7)
                    item.partner_code = name
        return res
