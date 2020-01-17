# -*- coding: utf-8 -*-
{
    'name': "E2yun HHJC CRM Lead Extends",

    'summary': """
    线索模型增加字段，更改前台显示页面
        """,

    'description': """
    """,

    'author': "Kangyu.Wang",
    'website': "http://www.e2yun.com",

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
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}