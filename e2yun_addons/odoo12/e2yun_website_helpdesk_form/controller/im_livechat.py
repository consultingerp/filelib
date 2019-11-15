# -*-coding:utf-8-*-

import base64
import odoo
import datetime

from odoo import http, _
from odoo.http import request
from odoo import models, fields, api
from odoo.addons.im_livechat.controllers.main import LivechatController


class LivechatController(LivechatController):

    @http.route('/im_livechat/loader/<int:channel_id>', type='http', auth='public')
    def loader(self, channel_id, **kwargs):
        # channel_id = 9
        reponse_website = super(LivechatController, self).loader(channel_id, **kwargs)
        return reponse_website


