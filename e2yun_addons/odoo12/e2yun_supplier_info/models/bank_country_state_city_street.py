from odoo import models, fields, api

class Country(models.Model):
    _name = 'bank.country'
    _description = 'Bank Country'
    _order = 'name'

    name = fields.Char(
        string='Country Name', required=True, translate=True, help='The full name of the country.')
    code = fields.Char(
        string='Country Code', size=2,
        help='The ISO country code in two chars. \nYou can use this field for quick search.')
    currency_id = fields.Many2one('res.currency', string='Currency')
    state_ids = fields.One2many('bank.state', 'country_id', string='States')

class State(models.Model):
    _name = 'bank.state'
    _description = 'Bank State'
    _order = 'name'
    country_id = fields.Many2one('bank.country', string='Country', required=True)
    name = fields.Char(string='State Name', required=True,
                       help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton')
    code = fields.Char(string='State Code', help='The state code.', required=True)

    city_ids = fields.One2many('bank.city', 'state_id', string='States')

class City(models.Model):
    _name = 'bank.city'
    _description = 'Bank City'
    _order = 'name'
    state_id = fields.Many2one('bank.state', string='State', required=True)
    name = fields.Char(string='City Name', required=True,)
    code = fields.Char(string='City Code', help='The City code.', required=True)
    region_ids = fields.One2many('bank.region', 'city_id', string='City')

class Region(models.Model):
    _name = 'bank.region'
    _description = 'Bank Region'
    _order = 'name'
    city_id = fields.Many2one('bank.city', string='City', required=True)
    name = fields.Char(string='Region Name', required=True,)
    code = fields.Char(string='Region Code', help='The Region code.', required=True)
