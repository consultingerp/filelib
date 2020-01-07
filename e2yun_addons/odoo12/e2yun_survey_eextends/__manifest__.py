# -*- coding: utf-8 -*-
{
    'name': "e2yun_survey_eextends",

    'summary': """
        问卷修改""",

    'description': """
        问卷修改
    """,

    'author': "Zhiyong.Cao",
    'website': "http://www.e2yun.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Survey',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'survey', 'e2yun_survey_pagee_extends'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}