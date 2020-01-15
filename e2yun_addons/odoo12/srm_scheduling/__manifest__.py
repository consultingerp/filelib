# -*- coding: utf-8 -*-
{
    'name': "SRM scheduling",
    'summary': """
        srm scheduling""",

    'description': """
       srm scheduling
    """,
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "author": "chuqiu.xu",
    'depends': ['web','srm_demand_publish'],
    'data': [
        'views/qweb_templates.xml',
        'views/manager_view.xml',
    ],
    'qweb': [
        'qweb/templates.xml',
    ],
    'js': [],
    # only loaded in demonstration mode
    'demo': [ ],
    'installable': True,
    'auto_install': False,
    'application': True
}