# -*- coding: utf-8 -*-
{
    'name': "e2yun_coupon",

    'summary': """
    显示所有用户优惠券的模块
        """,

    'description': """
    显示用户所有的优惠券的模块
    """,

    'author': "czy",
    'website': "www.e2yun.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_coupon', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': False
}