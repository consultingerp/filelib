# -*-coding:utf-8-*-

from odoo import fields, models


class HelpdeskTicketBrandType(models.Model):
    _name = 'helpdesk.ticket.brandtype'
    _description = '售后品牌'
    _order = 'sequence'

    name = fields.Char(string='名称', required=True, translate=True)
    sequence = fields.Integer(default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "类型已存在 !"),
    ]
