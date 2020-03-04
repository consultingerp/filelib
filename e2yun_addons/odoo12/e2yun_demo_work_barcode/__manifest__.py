# -*- coding: utf-8 -*-
{
    'name': "e2yun_demo_work_barcode",

    'summary': """
        Demo Word系统增加报工二维码
        """,

    'description': """
        Demo Word系统增加报工二维码
    """,

    'author': "Li Haonan",
    'website': "http://www.e2yun.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'kindee_data_sync_info'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/barcode_print.xml',
    ],
}