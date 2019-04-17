# -*- coding: utf-8 -*-

import logging

import odoo
from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from odoo.http import request

from odoo.addons.base.res import res_users
res_users.USER_PRIVATE_FIELDS.append('password_crypt')

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = "res.users"
    aip_active = fields.Boolean(default=True)
    aip_user_id = fields.Many2one(
        comodel_name='res.users',
        string="AIP User",
    )

    @classmethod
    def _login(cls, db, login, password):
        if not password:
            return False
        user_id = False
        aip_user_name = False
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                user = self.search([('login', '=', login),'|',('active', '=', True),
                                    '&',('aip_user_id', '!=', False),('aip_active', '=', True)])
                if user:
                    user_id = user.id
                    user.sudo(user_id).check_credentials(password)
                    if user.aip_user_id:
                        user.sudo(user.aip_user_id.id)._update_last_login()
                        aip_user_name = user.aip_user_id.login
                    else:
                        user.sudo(user_id)._update_last_login()
        except AccessDenied:
            user_id = False

        status = "successful" if user_id else "failed"
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        if aip_user_name:

            _logger.info("Login %s for db:%s login:%s from %s", status, db, aip_user_name, ip)
        else:
            _logger.info("Login %s for db:%s login:%s from %s", status, db, login, ip)

        return user_id

    @api.model
    def check_credentials(self, password):
        # convert to base_crypt if needed
        self.env.cr.execute('SELECT password, password_crypt FROM res_users WHERE id=%s AND ( active OR aip_active )', (self.env.uid,))
        encrypted = None
        user = self.env.user
        if self.env.cr.rowcount:
            stored, encrypted = self.env.cr.fetchone()
            if stored and not encrypted:
                user._set_password(stored)
                self.invalidate_cache()
        try:
            return super(ResUsers, self).check_credentials(password)
        except odoo.exceptions.AccessDenied:
            if encrypted:
                valid_pass, replacement = user._crypt_context() \
                    .verify_and_update(password, encrypted)
                if replacement is not None:
                    user._set_encrypted_password(replacement)
                if valid_pass:
                    return
            raise