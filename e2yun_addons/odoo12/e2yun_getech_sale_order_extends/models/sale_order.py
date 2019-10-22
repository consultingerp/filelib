# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models, fields, api
import datetime
import suds.client
import json


class SaleOrder_BU(models.Model):
    _name = 'sale.order.bu'

    code = fields.Char('Code')
    name = fields.Char('Name')


class SaleOrder_Project_type(models.Model):
    _name = 'sale.order.project.type'

    code = fields.Char('Code')
    name = fields.Char('Name')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bu = fields.Many2one('sale.order.bu', '产业/BU')
    project_type = fields.Many2one('sale.order.project.type', '项目大类')
