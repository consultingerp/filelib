# -*- coding: utf-8 -*-
{
    'name': "E2yun Partner Address",
    'summary': """
        客户地址维护""",
    'description': """
        客户地址维护
    """,
    'author': "liqiang",
    'website': "http://www.e2yun.cn",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','contacts'],
    'data': [
        'security/ir.model.access2.csv',
        'views/views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}