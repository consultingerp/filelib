# -*- coding: utf-8 -*-
{
    'name': "yc_website_home",

    'summary': """
        悦辰主页修改""",

    'description': """
        悦辰主页修改
    """,

    'author': "Zhiyong.Cao",
    'website': "www.e2yun.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/website_home.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    # 'installable': True,
}