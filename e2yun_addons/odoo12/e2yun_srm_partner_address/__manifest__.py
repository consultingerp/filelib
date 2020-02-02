# -*- coding: utf-8 -*-
{
    'name': "E2yun SRM Partner Address",
    'summary': """
        供应商地址维护""",
    'description': """
        供应商地址维护
    """,
    'author': "liqiang",
    'website': "http://www.e2yun.cn",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','contacts','base_address_city'],
    'data': [
        #'security/ir.model.access2.csv',
        'views/views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}