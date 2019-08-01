# -*-coding:utf-8-*-

import json
import logging

from geopy.distance import vincenty

from odoo import http
from odoo.fields import Datetime
from odoo.http import request
from ..controllers import amapapi

_logger = logging.getLogger(__name__)


class AmapAip(http.Controller):
    @http.route(['/amap/convert'], type='http', auth="public", csrf=False, website=True, cors="*")
    def convert(self, *args, **kwargs):
        try:
            convert_location = amapapi.coordinateconvert(request, request.params['location'])
            formatted_address = amapapi.geocoderegeo(request, convert_location)
            location = convert_location.split(',')  # 用户真实位置
            user = request.env['res.users'].sudo().search([('id', '=', request.uid)], limit=1)
            collect_user_location = request.env['ir.config_parameter'].sudo().get_param(
                'base_setup.collect_user_location')
            if collect_user_location:
                if user.exists():
                    user.partner_id.write({
                        'wxlatitude': location[1],
                        'wxlongitude': location[0],
                        'wxprecision': '-1',
                        'location_write_date': Datetime.now()
                    })
                    user.setpartnerteamanduser(request, location[1], location[0])
        except Exception as e:
            print(e)
            return ''
        data = {"locations": convert_location, 'formatted_address': formatted_address}
        return json.dumps(data)

    @http.route(['/amap/nearby_stores'], type='json', auth='user')
    def nearby_stores(self, location, storename):
        datalistsize = 50
        domain = []
        if storename == 'BJ':
            domain = [
                ('name', 'ilike', "北京%")
            ]
        elif storename == 'SZ':
            domain = [
                ('name', 'ilike', "深圳%")
            ]
        elif storename == 'OTH':
            domain = [
                ('name', 'not ilike', '北京%'),
                ('name', 'not ilike', '深圳%')
            ]
        elif not storename and not location:
            domain = []
            datalistsize = 80
        elif not storename:
            domain = []
            datalistsize = 10

        if location:  # 如果是带了地址
            try:
                convert_location = amapapi.coordinateconvert(request, location)
                formatted_address = amapapi.geocoderegeo(request, convert_location)
                location = convert_location.split(',')  # 用户真实位置
                user = request.env['res.users'].sudo().search([('id', '=', request.uid)], limit=1)
                collect_user_location = request.env['ir.config_parameter'].sudo().get_param(
                    'base_setup.collect_user_location')
                if collect_user_location:
                    if user.exists():
                        user.partner_id.write({
                            'wxlatitude': location[1],
                            'wxlongitude': location[0],
                            'wxprecision': '-1',
                            'location_write_date': Datetime.now()
                        })
                        user.setpartnerteamanduser(request, location[1], location[0])
            except Exception as e:
                print(e)
                return ''
            data = {"locations": convert_location, 'formatted_address': formatted_address}
            newport_ri = (location[1], location[0])
            crm_team_pool = request.env['crm.team'].search_read(domain)
            search_read_new = []
            for crm_team in crm_team_pool:
                if crm_team['longitude'] != 0.0 or crm_team['longitude'] != 0.0:
                    cleveland_oh = (crm_team['latitude'], crm_team['longitude'])
                    pos_kilometers = vincenty(newport_ri, cleveland_oh).kilometers
                    crm_team['distance'] = round(pos_kilometers, 2)
                    search_read_new.append(crm_team)
                    # _logger.info("门店与用户距离%s" % pos_kilometers)
            search_read_new = sorted(search_read_new, key=lambda dict: dict['distance'], reverse=False)

        else:  # 没有地址信息
            search_read_new = request.env['crm.team'].search_read(domain, limit=datalistsize)

        crm_team_list = []
        listsize = len(search_read_new) if len(search_read_new) <= datalistsize else datalistsize
        for i in range(listsize):
            crm_team_list.append(search_read_new[i])
        return {
            'crm_team_list': crm_team_list
        }

    @http.route(['/amap/stores_list'], type='json', auth='user')
    def stores_list(self, name):
        if name == 'BJ':
            domain = [
                ('name', 'ilike', "北京%")
            ]
        elif name == 'SZ':
            domain = [
                ('name', 'ilike', "深圳%")
            ]
        else:
            domain = [
                ('name', 'not ilike', '北京%'),
                ('name', 'not ilike', '深圳%')
            ]
        crm_team_list = request.env['crm.team'].search_read(domain, limit=50)
        return {
            'crm_team_list': crm_team_list
        }
