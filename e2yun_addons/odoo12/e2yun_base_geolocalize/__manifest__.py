# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'E2yun Partners Geolocation',
    'version': '2.0',
    'category': 'Sales',
    'description': """
E2yun Partners Geolocation 
==========================
partner.country_id.code == 'CN' use Baidu Geolocation
others use Bing Geolocation
    """,
    'depends': ['base','base_geolocalize','e2yun_geoengine_maps'],
    'data': ['views/res_partner_views.xml',
             'views/website_templates.xml'
    ],
    'installable': True,
}
