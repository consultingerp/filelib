# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import werkzeug
import logging

import requests

from odoo import api, fields, models, tools, _
from odoo.addons.base_geoengine import fields as geo_fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

def geo_find_baidu(addr,city, apikey=False):
    if not addr:
        return None

    if not apikey:
        raise UserError(_('''API key for GeoCoding (Places) required.\n
                          Save this key in System Parameters with key: baidu.api_key_geocode, value: <your api key>
                          Visit http://lbsyun.baidu.com/apiconsole/key/create for more information.
                          '''))

    url = "http://api.map.baidu.com/geocoder/v2/?"
    try:
        result = requests.get(url, params={'address': addr, 'city': city,'output': 'json', 'ak': apikey}).json()
    except Exception as e:
        raise UserError(_('Cannot contact geolocation servers. Please make sure that your Internet connection is up and running (%s).') % e)
    status_message = 'OK'
    if result['status'] != 0:
        if result['status'] == 1:
            status_message = _('服务器内部错误')
        elif result['status'] == 2:
            status_message = _('请求参数非法')
        elif result['status'] == 3:
            status_message = _('权限校验失败')
        elif result['status'] == 4:
            status_message = _('配额校验失败')
        elif result['status'] == 5:
            status_message = _('ak不存在或者非法')
        elif result['status'] == 101:
            status_message = _('服务禁用')
        elif result['status'] == 102:
            status_message = _('不通过白名单或者安全码不对')
        elif result['status'] >= 200 and result['status'] < 300:
            status_message = _('无权限')
        elif result['status'] >= 300:
            status_message = _('配额错误')
        if status_message != 'OK':
            _logger.error(status_message)
            error_msg = _('Unable to geolocate, received the error:\n[%s]%s'
                          '\n\nBaidu made this a paid feature.\n'
                          'You should first enable billing on your Baidu account.\n'
                          'Then, go to Developer Console, and enable the APIs:\n'
                          'Geocoding, Maps Static, Maps Javascript.\n'
                          % (result['status'], status_message))
            raise UserError(error_msg)

    try:
        geo = result['result']['location']
        return float(geo['lat']), float(geo['lng'])
    except (KeyError, ValueError):
        return None

def geo_find_bing(addr, apikey=False):
    if not addr:
        return None

    if not apikey:
        raise UserError(_('''API key for GeoCoding (Places) required.\n
                          Save this key in System Parameters with key: bing.api_key_geocode, value: <your api key>
                          Visit https://docs.microsoft.com/en-us/bingmaps/getting-started/bing-maps-dev-center-help/getting-a-bing-maps-key
                          for more information.
                          '''))

    url = "https://dev.virtualearth.net/REST/v1/Locations/?"
    try:
        result = requests.get(url, params={'q':addr, 'o':'json', 'key':apikey}).json()
    except Exception as e:
        raise UserError(_('Cannot contact geolocation servers. Please make sure that your Internet connection is up and running (%s).') % e)

    if result['statusCode'] != 200:
        if result.get('statusDescription'):
            _logger.error(result['statusDescription'])
            error_msg = _('Unable to geolocate, received the error:\n%s'
                          '\n\nBing made this a paid feature.\n'
                          'You should first enable billing on your Bing account.\n'
                          'Then, go to Developer Console, and enable the APIs:\n'
                          'Geocoding, Maps Static, Maps Javascript.\n'
                          % result['statusDescription'])
            raise UserError(error_msg)

    try:
        if len(result['resourceSets']) > 0 and len(result['resourceSets'][0]) > 0:
            geo = result['resourceSets'][0]['resources'][0]['point']['coordinates']
            return float(geo[0]), float(geo[1])
        else:
            return None
    except (KeyError, ValueError):
        return None


def geo_query_address(street=None, zip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        # put country qualifier in front, otherwise GMap gives wrong results,
        # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
        country = '{1} {0}'.format(*country.split(',', 1))
    return tools.ustr(', '.join(
        field for field in [street, ("%s %s" % (zip or '', city or '')).strip(), state, country]
        if field
    ))

def urlplus(url, params):
    return werkzeug.Href(url)(params or None)

class ResPartner(models.Model):
    _inherit = "res.partner"
    # Geometry Field
    shape = fields.GeoPoint('Coordinate')

    # partner_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    # partner_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    # date_localization = fields.Date(string='Geolocation Date')
    def create_geometry(self):
        for partner in self:
            lat = partner.partner_latitude
            lng = partner.partner_longitude
            point = geo_fields.GeoPoint.from_latlon(cr=partner.env.cr,
                                                    latitude=lat,
                                                    longitude=lng)
            partner.shape = point

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        lat = self.partner_latitude
        lng = self.partner_longitude
        if lat == 0.0 and lng == 0.0:
            res.geo_localize()
        else:
            self.create_geometry()
        return res

    @classmethod
    def _geo_localize_cn(cls, apikey, street='', zip='', city='', state='', country=''):
        search = geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_find_baidu(search, city, apikey)
        if result is None:
            search = geo_query_address(city=city, state=state, country=country)
            result = geo_find_baidu(search, city, apikey)
        return result

    @classmethod
    def _geo_localize_en(cls, apikey, street='', zip='', city='', state='', country=''):
        search = geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_find_bing(search, apikey)
        if result is None:
            search = geo_query_address(city=city, state=state, country=country)
            result = geo_find_bing(search, apikey)
        return result

    @api.multi
    def geo_localize(self):
        # We need country names in English below
        lang = self.env.lang if self.env.lang else self.env.user.lang
        for partner in self.with_context(lang=lang):
            street = partner.street
            if partner.street2:
                street += partner.street2
            if partner.country_id.code == 'CN':
                apikey = self.env['ir.config_parameter'].sudo().get_param('baidu.api_key_geocode',
                                                                          default='LSh6ALesEBqAus4GCDurc0sRSkbrqfjH')

                result = partner._geo_localize_cn(apikey,
                                               street,
                                               partner.zip,
                                               partner.city,
                                               partner.state_id.name,
                                               partner.country_id.name)
            else:
                apikey = self.env['ir.config_parameter'].sudo().get_param('bing.api_key_geocode',
                                                                          default='AqY4IFeQhJPHi5FjGBNc7hfgUNcaVf7S_qyyP_dlVCesSJUqI7dBA-gsyoAIUvGu')
                result = partner._geo_localize_en(apikey,
                                               street,
                                               partner.zip,
                                               partner.city,
                                               partner.state_id.name,
                                               partner.country_id.name)
            if result:
                lat = result[0]
                lng = result[1]
                point = geo_fields.GeoPoint.from_latlon(cr=partner.env.cr,
                                                        latitude=lat,
                                                        longitude=lng)
                partner.write({
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.Date.context_today(partner),
                    'shape': point
                })
        return True


    @api.multi
    def write(self, vals):

        res = super(ResPartner, self).write(vals)

        if ('partner_latitude' in vals) or ('partner_longitude' in vals):
            self.create_geometry()
        elif (('street' in vals) or ('street2' in vals) or ('city' in vals) or
                  ('country_id' in vals) or ('zip' in vals) or ('state_id' in vals) or
                  ('zip_id' in vals)):
            self.geo_localize()
        if 'shape' in vals:
            self.env.cr.execute(
                """
                    UPDATE res_partner SET 
                        partner_latitude = ST_Y(ST_Transform(shape,4326)),
                        partner_longitude = ST_X(ST_Transform(shape,4326))
                    WHERE id = %(id)s 
                """, {'id': self.id})

        return res

    @api.multi
    def baidu_map_img(self, zoom=8, width=298, height=298):
        baidu_maps_api_key = self.env['ir.config_parameter'].sudo().get_param('baidu.api_key_geocode',
                                                                              default='LSh6ALesEBqAus4GCDurc0sRSkbrqfjH')
        country_name = self.country_id and self.country_id.name or ''
        state_name = self.state_id and self.state_id.name or ''
        city_name = self.city or ''
        street_name = self.street or ''
        street2_name = self.street2 or ''
        params = {
            'markers': '%s' % street2_name,
            'center': '%s%s%s%s' % (country_name, state_name, city_name, street_name),
            'height': "%s" % height,
            'width': "%s" % width,
            'zoom': zoom,
            'ak': baidu_maps_api_key,
        }
        # http://api.map.baidu.com/staticimage/v2
        return urlplus('//api.map.baidu.com/staticimage', params)

    @api.multi
    def baidu_map_link(self, zoom=10):
        baidu_maps_api_key = self.env['ir.config_parameter'].sudo().get_param('baidu.api_key_geocode',
                                                                              default='LSh6ALesEBqAus4GCDurc0sRSkbrqfjH')

        partner_name = self.name
        city_name = self.city or ''
        street2_name = self.street2 or ''
        params = {
            'address': '%s,%s,%s' % (city_name, street2_name, partner_name),
            'output': 'html',
            'src': 'e2yun',
            'ak': baidu_maps_api_key
        }
        # http://lbsyun.baidu.com/index.php?title=uri
        return urlplus('//api.map.baidu.com/geocoder', params)
