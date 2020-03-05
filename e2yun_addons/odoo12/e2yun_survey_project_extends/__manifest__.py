# -*- coding: utf-8 -*-
{
    'name': "e2yun_survey_project_extends",

    'summary': """
        供应商评估  涉及项目模块的更改""",

    'description': """
        与问卷相关的内容""",

    'author': "Kangyu.Wang",
    'website': "http://www.e2yun.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'e2yun_project_extends', 'e2yun_survey_eextends', 'e2yun_suppliers_register'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}