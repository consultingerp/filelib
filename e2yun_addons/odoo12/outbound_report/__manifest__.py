# -*- coding: utf-8 -*-
{
    'name': "outbound_report",
    'description': "出库报表",
    'author': "lth",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail', 'im_livechat', 'sale_management', 'wx_tools'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/outbound_report.xml',
        # 'views/outbound_template.xml',
        'views/outbound_report_dashboard.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'active': False,
    'web': True,
}