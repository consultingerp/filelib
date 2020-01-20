# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class e2yun_hhjc_crm_lead_extends(models.Model):
#     _name = 'e2yun_hhjc_crm_lead_extends.e2yun_hhjc_crm_lead_extends'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100