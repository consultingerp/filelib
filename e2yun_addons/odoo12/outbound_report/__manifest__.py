# -*- coding: utf-8 -*-
{
    'name': "outbound_report",
    'description': "出库报表",
    'author': "lth",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail', 'im_livechat', 'sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/outbound_report_dashboard.xml',
        'views/sales_team_goal.xml',
        'views/target_completion_report.xml',
    ],
    'qweb': [
        'static/src/xml/outbound_button_template.xml',
             ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'web': True,
}