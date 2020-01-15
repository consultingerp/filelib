# -*- coding: utf-8 -*-
{
    'name': "SRM Mat Demand Line Lifnr",

    'summary': """
         Supplier batch confirmation
        """,

    'description': """
       Supplier batch confirmation
    """,
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "author": "chuqiu.xu",
    'depends': ['srm_demand_publish'],
    'data': [
        'demand_publish_view_lifnr.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True

}