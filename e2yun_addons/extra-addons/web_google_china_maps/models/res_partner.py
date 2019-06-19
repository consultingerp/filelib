# -*- coding: utf-8 -*-
import json
#import urllib2
import urllib.request
import urllib.error

from odoo import api, fields, models, tools, exceptions, _
from odoo.exceptions import UserError


def geo_find2(addr):
    if not addr:
        return None
    url = 'https://maps.google.cn/maps/api/geocode/json?sensor=false&address='
    #url += urllib2.quote(addr.encode('utf8'))
    url += urllib.request.quote(addr.encode('utf8'))

    try:
        #result = json.load(urllib2.urlopen(url))
        result = json.load(urllib.request.urlopen(url))
    except Exception as e:
        raise UserError(_('Cannot contact geolocation servers. Please make sure that your Internet connection is up and running (%s).') % e)

    if result['status'] != 'OK':
        return None

    try:
        geo = result['results'][0]['geometry']['location']
        return float(geo['lat']), float(geo['lng'])
    except (KeyError, ValueError):
        return None

def geo_query_address(street=None, zip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        # put country qualifier in front, otherwise GMap gives wrong results,
        # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
        country = '{1} {0}'.format(*country.split(',', 1))
    return tools.ustr(', '.join(filter(None, [street,
                                              ("%s %s" % (zip or '', city or '')).strip(),
                                              state,
                                              country])))
class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def action_map_route(self):
        self.ensure_one()
        context = self.env.context.copy()
        user_id = self.env.user.partner_id
        if not all([user_id.partner_longitude, user_id.partner_latitude]):
            raise exceptions.Warning(_(
                'You have not defined your geolocation'))
        context.update({
            'origin_latitude': user_id.partner_latitude,
            'origin_longitude': user_id.partner_longitude,
            'destination_latitude': self.partner_latitude,
            'destination_longitude': self.partner_longitude
        })
        partners = [user_id.id, self.id]
        view_map_id = self.env.ref('web_google_china_maps.view_partner_map')
        return {
            'name': _('Map'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'map',
            'view_type': 'map',
            'views': [(view_map_id.id, 'map')],
            'context': context,
            'domain': [('id', 'in', partners)]
        }

    @api.multi
    def geo_localize(self):
        # We need country names in English below
        for partner in self.with_context(lang='en_US'):
            result = geo_find2(geo_query_address(street=partner.street,
                                                zip=partner.zip,
                                                city=partner.city,
                                                state=partner.state_id.name,
                                                country=partner.country_id.name))
            if result is None:
                result = geo_find2(geo_query_address(
                    city=partner.city,
                    state=partner.state_id.name,
                    country=partner.country_id.name
                ))

            if result:
                partner.write({
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.Date.context_today(partner)
                })
        return True