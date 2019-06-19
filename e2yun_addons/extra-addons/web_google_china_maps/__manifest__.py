# -*- coding: utf-8 -*-
{
    'name': 'Web Google China Maps',
    'version': '12.0.8.07',
    'author': "Supop.cn",
    'summary': """Web Google Map and google places autocomplete address form(Available in China)""",
    'description': """
Web Google Map and google places autocomplete address form
==========================================================
可在中国使用的google地图视图。
This module brings three features:
1. Allows user to view all partners addresses on google maps.
2. Enabled google places autocomplete address form into partner
form view, it provide autocomplete feature when you typed an address of partner
3. Routes information
""",
    'images': ['static/description/map1.jpg'],
    'author': 'Sunpop.cn',
    'website': 'http://www.sunpop.cn',
    'license': 'LGPL-3',
    'category': 'web',
    'sequence': 0,
    'price': 0.00,
    'currency': 'EUR',
    'depends': [
        'website_google_map',
        'base_geolocalize',
    ],
    'data': [
        'views/google_places_template.xml',
        'views/res_partner.xml',
        # data
        'data/ir_config_parameter.xml',
    ],
    'demo': [],
    'qweb': ['static/src/xml/widget_places.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
