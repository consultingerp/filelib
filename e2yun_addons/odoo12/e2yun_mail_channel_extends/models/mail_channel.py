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
from odoo import models, api


class MailChannelExtends(models.Model):
    _inherit = 'mail.channel'

    @api.multi
    def channel_info(self, extra_info=False):
        channel_infos = super(MailChannelExtends, self).channel_info(extra_info=extra_info)
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++%s%s' % (self._context['isMobile'] + self._context))
        if 'isMobile' in self._context and self._context['isMobile']:
            for channel in channel_infos:
                channel['is_minimized'] = False
        return channel_infos
