# -*- coding: utf-8 -*-
{
    'name': "E2yun Customer Extends",

    'summary': """
        客户主数据扩充""",

    'description': """
        客户主数据扩充
    """,

    'author': "Kangyu.Wang",
    'website': "http://www.e2yun.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'sales_team', 'sale', 'base_setup', 'e2yun_partner_address'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_config_settings_views.xml',
        'data/ir_sequence_data.xml',
        'data/cron.xml',
        'pre_install.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}