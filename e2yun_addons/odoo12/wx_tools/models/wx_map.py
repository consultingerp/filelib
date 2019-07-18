from odoo import models, api, fields, http
import random
import string
import time



class wx_map_model(models.TransientModel):
    _inherit = ['wx.config.settings']

    wx_nonceStr = fields.Char('nonceStr')
    wx_timestamp = fields.Integer('timestamp')
    wx_jsapi_ticket = fields.Char('jsapi_ticket')


    @api.multi
    def get_nonceStr(self):
        res = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
        return res

    @api.multi
    def get_timestamp(self):
        res = int(time.time())
        return res

    @api.multi
    def get_jsapi_ticket(self):
        from .wx_config_model import wx_config_settings
        ticket_url = 'http://api.weixin.qq.com/cgi-bin/ticket/getticket?type=jsapi&access_token=%s' % wx_config_settings.wx_AccessToken
        res = http.request(ticket_url)
        return res

    @api.multi
    def sign(self, wx_nonceStr):


