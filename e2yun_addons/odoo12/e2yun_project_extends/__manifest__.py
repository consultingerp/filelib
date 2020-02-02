{
    'name': "e2yun_project_extends",

    'summary': """
        Project Extends Info
        """,

    'description': """
      项目管理
    """,

    'author': "Feng Zhou",
    'website': "http://www.e2yun.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project', 'survey'],

    # always loaded
    'data': [
       'security/ir.model.access2.csv',
       'views/e2yun_project_view.xml',
       'views/survey_page_tempalte.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    # 'installable': False,
}
# -*- coding: utf-8 -*-
