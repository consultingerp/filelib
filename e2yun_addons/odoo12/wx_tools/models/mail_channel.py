# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools import html2plaintext


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    @api.model
    def create_user(self, partners_to):
        channel = self.create({
            'channel_partner_ids': [(4, partner_id) for partner_id in partners_to],
            'public': 'private',
            'channel_type': 'chat',
            'email_send': False,
            'name': ', '.join(self.env['res.partner'].sudo().browse(partners_to).mapped('name')),
        })
        return channel

    @api.model
    def channel_get(self, partners_to, pin=True):
        return super(MailChannel, self).channel_get(partners_to, pin)

    @api.model
    def create(self, vals):
        return super(MailChannel, self).create(vals)
