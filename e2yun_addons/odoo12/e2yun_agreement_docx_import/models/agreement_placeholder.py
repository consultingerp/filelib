# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AgreementPlaceholder(models.Model):
    _name = "agreement.placeholder"
    _description = "Agreement Placeholder"
    _table = 'agreement_placeholder'

    name = fields.Char(string="Name", required=True)
    type = fields.Selection([ ('text', 'Text'), ('picture', 'Picture')],
                                     string='类型',
                                     default='text',required=True)
    text = fields.Char(string="text" )
    picture = fields.Binary("picture")