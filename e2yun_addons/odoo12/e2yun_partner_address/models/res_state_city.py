# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions

# 继承城市模型res.city
# class ResStateCity(models.Model):
#     _inherit = 'res.city'
#
#     area_ids = fields.One2many('res.city.area','city_id',string='Area')

# 设置地区模型：因为城市res.city自带区县，所以注释
# class ResCityArea(models.Model):
#     _name = 'res.city.area'
#     _description = 'Area'
#
#     city_id = fields.Many2one('res.city',string='City')
#     name = fields.Char('Area')
#     code = fields.Char('Area Code')

class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    city_ids = fields.One2many('res.city','state_id',string='City')
