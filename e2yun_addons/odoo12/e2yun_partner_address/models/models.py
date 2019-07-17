# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions
from datetime import timedelta

from odoo.exceptions import ValidationError, Warning

class E2yunCsutomerExtends(models.Model):
    _inherit = 'res.partner'

    city_id = fields.Many2one('res.state.city',string='City',domain="[('state_id','=?',state_id)]")
    area_id = fields.Many2one('res.city.area',string='Area',domain="[('city_id','=?',city_id)]")
