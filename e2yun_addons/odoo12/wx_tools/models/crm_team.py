# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models
from odoo.fields import Datetime
from geopy.distance import vincenty

_logger = logging.getLogger(__name__)


class WXCrmTeam(models.Model):
    _inherit = 'crm.team'
    # _order = 'distance'

    qrcode_ticket = fields.Char(u'二维码ticket')
    qrcode_url = fields.Char(u'二维码url')
    qrcodeimg = fields.Html(compute='_get_qrcodeimg', string=u'二维码')

    latitude = fields.Float('纬度', digits=(10, 7))
    longitude = fields.Float('经度', digits=(10, 7))
    distance = fields.Float('距离', digits=(10, 7))
    location_write_date = fields.Datetime("更新时间", readonly=True)
    address_location = fields.Char(u'地址', compute='_get_address_location')

    @api.one
    def _get_address_location(self):
        from ..controllers import amapapi
        if (self.longitude == 0.0 or self.longitude == 0.0) and self.street:
            street_location = amapapi.geocodegeo(self, address=self.street)
            if street_location:
                location = street_location.split(',')
                self.longitude = location[0]
                self.latitude = location[1]
                self.write({'longitude': location[0], 'latitude': location[1], 'location_write_date': Datetime.now(),
                            'address_location': self.street
                            })
                self.address_location = self.street
        else:
            self.address_location = self.street

    @api.one
    def _get_qrcodeimg(self):
        # 生成团队二维码
        if not self.qrcode_ticket:
            _logger.info("生成二维码")
            from ..controllers import client
            entry = client.wxenv(self.env)
            qrcodedatastr = 'TEAM|%s|%s' % (self.id, self.name)
            qrcodedata = {"expire_seconds": 2592000, "action_name": "QR_STR_SCENE",
                          "action_info": {"scene": {"scene_str": qrcodedatastr}}}
            qrcodeinfo = entry.wxclient.create_qrcode(qrcodedata)
            self.write({'qrcode_ticket': qrcodeinfo['ticket'],
                        'qrcode_url': qrcodeinfo['url']})
            self.qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                             'height="100px" />' % (qrcodeinfo['ticket'] or '/wx_tools/static/description/icon.png')
        else:
            self.qrcodeimg = '<img src=https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s width="100px" ' \
                             'height="100px" />' % (self.qrcode_ticket or '/wx_tools/static/description/icon.png')

    @api.model
    def tearm_high_goal(self):
        # 获取销售团队下面评分最高用户
        gamification_goal = self.env['gamification.goal'].sudo().search([('user_id', 'in', self.member_ids.ids)])
        # for gamificatio in gamification_goal:
        #     _logger.info(gamificatio.user_id.id)
        #     _logger.info(gamificatio.current)
        if gamification_goal:
            max_goal_user = (max(gamification_goal, key=lambda x: x["current"]))
        else:
            return None
        _logger.info(max_goal_user)
        return max_goal_user

    @api.multi
    def convertteamaddres(self):
        crm_team_pool = self.env['crm.team'].search([])
        for crm_team in crm_team_pool:
            crm_team._get_address_location()
        return ""

    @api.multi
    def getrecenttearm(self, latitude, longitude):
        newport_ri = (latitude, longitude)
        crm_team_pool = self.env['crm.team'].search([])
        search_read_new = []
        for crm_team in crm_team_pool:
            if crm_team.longitude != 0.0 or crm_team.longitude != 0.0:
                cleveland_oh = (crm_team.latitude, crm_team.longitude)
                pos_kilometers = vincenty(newport_ri, cleveland_oh).kilometers
                crm_team.distance = pos_kilometers
                search_read_new.append(crm_team)
                _logger.info("门店与用户距离%s" % pos_kilometers)
        if search_read_new:
            min_distance = (min(search_read_new, key=lambda dict: dict['distance']))
            self.near_team = '%s:距离%s公里' % (min_distance.street, min_distance.distance)
            return min_distance
        return None

