# -*- coding: utf-8 -*-
{
    'name': "e2yun_hhjc_target_completion",
    'description': '目标完成占比报表',
    'author': "lth",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'outbound_sync_from_pos'],

    # always loaded
    'data': [
        'security/ir.model.access2.csv',
        'views/target_completion_report.xml',
        'views/data_sources.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        'static/src/xml/outbound_button_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'web': True,
}