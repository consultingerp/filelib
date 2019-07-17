# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions


class ResStateCity(models.Model):
    _name = 'res.state.city'
    _description = 'City'

    state_id = fields.Many2one('res.country.state',string='State')
    name = fields.Char('City')
    code = fields.Char('City Code')
    area_ids = fields.One2many('res.city.area','city_id',string='Area')

class ResCityArea(models.Model):
    _name = 'res.city.area'
    _description = 'Area'

    city_id = fields.Many2one('res.state.city',string='City')
    name = fields.Char('Area')
    code = fields.Char('Area Code')

class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    city_ids = fields.One2many('res.state.city','state_id',string='City')
