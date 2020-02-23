# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TestForInput(models.Model):
    _name = 'input.test.value'
    _description = '输入界面测试'

    value_id = fields.Many2one('input.test')
    select_value = fields.Selection([('val1', '值1'), ('val2', '值2')],)
    y_value = fields.Char('y')
    input_value = fields.Integer('num')
    x_value = fields.Char('x')


class InputTest(models.Model):
    _name = 'input.test'
    _description = '输入测试'

    name = fields.Char()
    test_ids = fields.One2many('input.test.value', 'value_id',
                               default=lambda self: self._default_test_ids())

    def _default_test_ids(self):
        recs = self.env['input.test'].search([])
        values = [{'x_value': '1', 'y_value': "a"}, {'x_value': '2', 'y_value': "a"}, {'x_value': '3', 'y_value': "a"},
                  {'x_value': '1', 'y_value': "b"}, {'x_value': '2', 'y_value': "b"}, {'x_value': '3', 'y_value': "b"},
                  {'x_value': '1', 'y_value': "c"}, {'x_value': '2', 'y_value': "c"}, {'x_value': '3', 'y_value': "c"}]
        return [
            (0, 0, {
                'name': "简单测试",
                'test_id': rec.id,
                'x_value': val['x_value'],
                'y_value': val['y_value'],
                'input_value': 0,
                'select_value': 'val1',
            })
            for rec in recs
            for val in values
        ]

