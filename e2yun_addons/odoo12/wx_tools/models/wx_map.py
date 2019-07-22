from odoo import models, api, fields, http
import random
import string
import time
import urllib
import hashlib


class wx_map_model(models.TransientModel):
    _inherit = ['wx.config.settings']

    wx_nonceStr = fields.Char('nonceStr')
    wx_timestamp = fields.Integer('timestamp')
    wx_jsapi_ticket = fields.Char('jsapi_ticket')
    current_url = fields.Char('current_url')
    signature = fields.Char('signature')


    @api.multi
    def get_nonceStr(self):
        wx_nonceStr = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
        return wx_nonceStr

    @api.multi
    def get_timestamp(self):
        wx_timestamps = int(time.time())
        return wx_timestamps

    @api.multi
    def get_jsapi_ticket(self):
        from .wx_config_model import wx_config_settings
        wx_AccessToken = wx_config_settings.get_default_wx_AccessToken()
        ticket_url = 'http://api.weixin.qq.com/cgi-bin/ticket/getticket?type=jsapi&access_token=%s' % wx_AccessToken
        try:
            ret_dict = urllib.request.urlopen(ticket_url).read().decode('utf-8')
            wx_jsapi_ticket = ret_dict['ticket']
            return wx_jsapi_ticket
        except Exception as e:
            return e

    @api.multi
    def get_current_url(self):
        current_url = http.request.httprequest
        return current_url

    @api.multi
    def sign(self):
        signstr = "js_api=" + self.get_jsapi_ticket() + '&nonceStr=' + self.get_nonceStr() + '&timestamp=' + self.get_timestamp + '&url=' + self.get_current_url
        signature = hashlib.sha1(signstr).hexdigest()
        return signature

