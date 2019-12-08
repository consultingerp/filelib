# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, api, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    odoobot_state = fields.Selection(string="Bot Status")

    notification_type = fields.Selection([
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in System')],
        'Notification Management', required=True, default='email',
        help="Policy on how to handle Chatter notifications:\n"
             "- Handle by Emails: notifications are sent to your email address\n"
             "- Handle in System: notifications appear in your System Inbox")

    @api.multi
    def is_admin(self):
        # By default Python functions starting with _ are considered private methods.
        # Private methods (such as _is_admin) cannot be called remotely
        return self._is_admin()
