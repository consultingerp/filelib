#!/usr/bin/python
# -*- coding: UTF-8 -*-
from odoo import api, fields, models, exceptions, _

class Srm_purchase_component(models.Model):
    _name = "purchase.component"
    _table = 'purchase_component'

    po_number = fields.Char('po_number', )
    po_item = fields.Char('po_item')
    name= fields.Char('name')
    purchase_component_line = fields.One2many('purchase.component.line', 'purchase_component_id', 'component Line', copy=True)


class Srm_purchase_component_line(models.Model):
    _name = "purchase.component.line"
    _table = 'purchase_component_line'

    purchase_component_id = fields.Many2one('purchase.component', 'purchase component', required=True, readonly=True, ondelete='cascade')
    po_number = fields.Char('po_number', )
    po_item = fields.Char('po_item')
    material = fields.Char('material')
    entry_quantity = fields.Float('entry_quantity')
    entry_uom = fields.Char('entry_uom')
    plant = fields.Char('plant')





