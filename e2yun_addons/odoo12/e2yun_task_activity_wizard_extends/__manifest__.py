# -*- coding: utf-8 -*-
{
    'name': "e2yun_task_activity_wizard_extends",

    'summary': """
        任务活动向导修改""",

    'description': """
        任务活动向导修改
    """,

    'author': "Zhiyong.Cao",
    'website': "http://e2yun.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','e2yun_project_extends','project',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizard/task_activity_wizard_extends.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}