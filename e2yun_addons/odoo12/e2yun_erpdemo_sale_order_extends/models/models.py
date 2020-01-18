# -*- coding: utf-8 -*-

from odoo import models, fields, api

class E2yunERPDemoResCurrencyExtends(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        currency_rates = (from_currency + to_currency)._get_rates(company, date)
        if not currency_rates.get(to_currency.id) or not currency_rates.get(from_currency.id):
            res = 1.0
        else:
            res = currency_rates.get(to_currency.id) / currency_rates.get(from_currency.id)
        return res