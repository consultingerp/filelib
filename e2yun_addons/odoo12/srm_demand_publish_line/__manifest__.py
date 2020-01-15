# -*- coding: utf-8 -*-
{
    'name': "SRM Mat Demand Line",

    'summary': """
       Purchase batch confirmation""",

    'description': """
        Purchase batch confirmation
    """,
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "author": "chuqiu.xu",
    # any module necessary for this one to work correctly
    'depends': ['srm_demand_publish'],
    # always loaded
    'data': [
        'demand_publish_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True

}