# -*- coding: utf-8 -*-
{
    'name': 'E2yun Partner Add Approval',
    'version': '12.0.0.1',
    'sequence': '10',
    'category': 'base',
    'depends': ['base','auth_signup'],
    'author': 'liqiang',
    'website': 'http://e2yun.cn',
    'summary': 'Res Partner Extends',
    'description': """E2yun Partner Add Approval""",
    'data': [
        'views/res_partner_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
