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
        'security/ir.model.access2.csv',
        'views/target_completion_report.xml',
        'views/data_sources.xml',
    ],
    'qweb': [
        'static/src/xml/outbound_button_template.xml',
        # 'static/src/xml/completion_button_template.xml',
             ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'web': True,
}