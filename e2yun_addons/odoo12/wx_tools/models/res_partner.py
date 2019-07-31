# coding=utf-8
import logging

from odoo import models, fields, api
from geopy.distance import vincenty

_logger = logging.getLogger(__name__)


class WXResPartner(models.Model):
    _inherit = 'res.partner'

    wxcorp_user_id = fields.Many2one('wx.corpuser', '关联企业号用户')
    wx_user_id = fields.Many2one('wx.user', '微信公众用户')
    wxlatitude = fields.Float('纬度', digits=(10, 7))
    wxlongitude = fields.Float('经度', digits=(10, 7))
    wxprecision = fields.Float('位置精度', digits=(10, 7))
    location_write_date = fields.Datetime("更新时间", readonly=True)
    wx_address = fields.Char(u'地址', compute='_get_address')
    near_team = fields.Char(u'附近门店', compute='_get_near_team')

    @api.one
    def _get_near_team(self):
        _logger.info(self)

    @api.one
    def _get_address(self):
        # 获取用户位置
        from ..controllers import amapapi
        if self.wxlatitude and self.wxlongitude:
            wx_location = '%s,%s' % (self.wxlongitude, self.wxlatitude)
            convert_location = amapapi.coordinateconvert(self, wx_location)
            location = convert_location.split(';')[0]  # 用户真实位置
            formatted_address = amapapi.geocoderegeo(self, location)
            if formatted_address:
                self.wx_address = formatted_address
            newport_ri = (location.split(',')[1], location.split(',')[0])
            crm_team_pool = self.env['crm.team'].search([])
            search_read_new = []
            for crm_team in crm_team_pool:
                if crm_team.longitude != 0.0 or crm_team.longitude != 0.0:
                    cleveland_oh = (crm_team.latitude, crm_team.longitude)
                    pos_kilometers = vincenty(newport_ri, cleveland_oh).kilometers
                    crm_team.distance = pos_kilometers
                    search_read_new.append(crm_team)
                    # _logger.info("门店与用户距离%s" % pos_kilometers)
            if search_read_new:
                min_distance = (min(search_read_new, key=lambda dict: dict['distance']))
                self.near_team = '%s:距离%s公里' % (min_distance.street, min_distance.distance)
            _logger.info("获取门店信息")

    # def _compute_im_status(self):
    #     super(WXResPartner, self)._compute_im_status()

    def send_corp_msg(self, msg):
        from ..rpc import corp_client
        entry = corp_client.corpenv(self.env)
        mtype = msg["mtype"]
        if mtype == "text":
            entry.client.message.send_text(entry.current_agent, self.wxcorp_user_id.userid, msg["content"])
        if mtype == "card":
            entry.client.message.send_text_card(entry.current_agent, self.wxcorp_user_id.userid, msg['title'],
                                                msg['description'], msg['url'], btntxt=msg.get("btntxt", "详情"))
        elif mtype == 'image':
            ret = entry.client.media.upload(mtype, msg['media_data'])
            entry.client.message.send_image(entry.current_agent, self.wxcorp_user_id.userid, ret['media_id'])
        elif mtype == 'voice':
            ret = entry.client.media.upload(mtype, msg['media_data'])
            entry.client.message.send_voice(entry.current_agent, self.wxcorp_user_id.userid, ret['media_id'])

    def get_corp_key(self):
        if self.wxcorp_user_id:
            return self.wxcorp_user_id.userid

    def get_wx_key(self):
        if self.wx_user_id:
            return self.wx_user_id.openid

    @api.multi
    def write(self, vals):
        resusers = super(WXResPartner, self).write(vals)
        if vals.get('wx_user_id') and self.user_ids.wx_user_id.id != vals.get('wx_user_id'):
            self.user_ids.wx_user_id = vals.get('wx_user_id')
            self.user_ids.wx_id = self.user_ids.wx_user_id.openid
        return resusers
