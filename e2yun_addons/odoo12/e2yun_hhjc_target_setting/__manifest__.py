# -*- coding: utf-8 -*-
{
    'name': "target_setting",
    'description': "门店目标设定",
    'author': "lth",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail', 'im_livechat', 'sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access2.csv',
        'views/sales_team_goal.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'web': True,
}