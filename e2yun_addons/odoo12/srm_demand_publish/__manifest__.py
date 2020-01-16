# -*- coding: utf-8 -*-
{
    'name': "SRM Mat Demand",
    'summary': """
        Material scheduling requirements""",

    'description': """
       Material scheduling requirements
    """,
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "author": "chuqiu.xu",
    'depends': ['purchase','web'],
    'data': [
        'demand_publish_view.xml',
        'mat_email_template.xml',
    ],
    'css': ['coustom_css/my.css'],
    'installable': True,
    'auto_install': False,
    'application': True

}