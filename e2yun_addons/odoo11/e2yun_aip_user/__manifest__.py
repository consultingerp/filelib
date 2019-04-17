# -*- coding: utf-8 -*-
{
    'name': "E2yun aip user",

    'summary': """
        用户增强""",

    'description': """
        用户增强添加操作用户
    """,

    'author': "joytao.zhu",
    'website': "http://www.e2yun.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'auth_crypt'],

    # always loaded
    'data': ["views/res_users_view.xml"
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}