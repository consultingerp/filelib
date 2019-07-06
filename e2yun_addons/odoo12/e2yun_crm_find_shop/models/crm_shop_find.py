# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CrmTeamADDinformation(models.Model):
    _inherit = ['crm.team']

    color = fields.Integer('Color Index')

    shop_adr_photo = fields.Binary('门店照片')