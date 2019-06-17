# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'E2yun Base Geolocation',
    'version': '2.0',
    'category': 'Sales',
    'description': """
======================
E2yun Base Geolocation
======================
This module extends Partners Geolocation


if partner.country_id.code == 'CN' use Baidu Geolocation
others use Bing Geolocation


replace website google map with baidu map


add Geolocation map for partner view 
    """,
    'depends': ['base','base_geolocalize','e2yun_geoengine_maps'],
    'data': ['views/res_partner_views.xml',
             'views/website_templates.xml'
    ],
    'installable': True,
}
