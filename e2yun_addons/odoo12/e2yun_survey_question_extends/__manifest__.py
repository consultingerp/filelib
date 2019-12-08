# -*- coding: utf-8 -*-
{
    'name': "e2yun_survey_question_extends",

    'summary': """
        Survey Question Extends """,

    'description': """
        Survey Question Extends 
    """,

    'author': "Feng Zhou",
    'website': "http://www.e2yun.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Marketing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['survey'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}