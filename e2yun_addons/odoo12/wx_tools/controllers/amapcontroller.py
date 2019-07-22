# -*-coding:utf-8-*-

import logging
from ..rpc import corp_client

from odoo import http
from odoo.http import request
from ..controllers import amapapi
from odoo.fields import Datetime
import json

_logger = logging.getLogger(__name__)


class AmapAip(http.Controller):
    @http.route(['/amap/convert'], type='http', auth="public", csrf=False, website=True, cors="*")
    def convert(self, *args, **kwargs):
        try:
            convert_location = amapapi.coordinateconvert(request, request.params['location'])
            formatted_address = amapapi.geocoderegeo(request, convert_location)
            location = convert_location.split(',')  # 用户真实位置
            user = request.env['res.users'].sudo().search([('id', '=', request.uid)], limit=1)
            collect_user_location = request.env['ir.config_parameter'].sudo().get_param('base_setup.collect_user_location')
            if collect_user_location:
                if user.exists():
                    user.partner_id.write({
                        'wxlatitude': location[1],
                        'wxlongitude': location[0],
                        'wxprecision': '-1',
                        'location_write_date': Datetime.now()
                    })
        except Exception as e:
            return ''
        data = {"locations": convert_location, 'formatted_address': formatted_address}
        return json.dumps(data)
