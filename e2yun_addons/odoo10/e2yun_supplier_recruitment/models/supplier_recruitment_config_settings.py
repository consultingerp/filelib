# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class RecruitmentSettings(models.TransientModel):
    _name = 'supplier.recruitment.config.settings'
    _inherit = ['res.config.settings']

    module_supplier_recruitment_survey = fields.Selection(selection=[
        (0, "Do not use interview forms"),
        (1, "Use interview forms during the recruitment process")
        ], string='Interview Form')
