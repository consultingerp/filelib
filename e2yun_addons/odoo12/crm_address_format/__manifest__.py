# -*- coding: utf-8 -*-
{
    'name': "crm_address_format",

    'summary': """
        增加线索地址格式与客户地址格式保持一致""",

    'description': """
        增加线索地址格式与客户地址格式保持一致
    """,

    'author': "czy",
    'website': "www.e2yun.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm'],

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
}