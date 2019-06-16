# -*- coding: utf-8 -*-
{
    'name': 'E2yun CRM Team security',
    'version': '12.0.0.1',
    'sequence': '10',
    'category': 'CRM',
    'depends': ['base','sales_team'],
    'author': 'liqiang',
    'website': 'http://e2yun.cn',
    'summary': 'E2yun CRM Team security',
    'description': """Privilege Control of Sales Team""",
    'data': [
        'security/crm_team_security.xml'
    ],
    'installable': True,
    'auto_install': False,
}
