from odoo import models, fields, api

class City(models.Model):
    _name = 'res.state.city'
    _description = 'City'
    _order = 'name'
    name = fields.Char('城市名称', required=True)
    state_id = fields.Many2one('res.country.state', string='State', required=True)