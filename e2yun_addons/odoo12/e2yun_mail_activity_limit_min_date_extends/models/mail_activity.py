# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Niyas Raphy(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, api, fields, _, exceptions
from datetime import date


class MailActivityExtends(models.Model):
    _inherit = 'mail.activity'

    # @api.onchange('date_deadline')
    # def _onchange_date_deadline(self):
    #     if not self.date_deadline:
    #         self.date_deadline = date.today()
    #     elif self.date_deadline < date.today():
    #         # self.date_deadline = date.today()
    #         raise exceptions.except_orm(_('不能小于当前日期'))

    @api.model
    def create(self, vals):
        res = super(MailActivityExtends, self).create(vals)
        for item in res:
            if item.date_deadline < date.today():
                raise exceptions.except_orm(_('不能小于当前日期'))
        return res
