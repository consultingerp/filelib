# -*- coding: utf-8 -*-
{
    'name': "e2yun_demo_crm_extends",

    'summary': """
    
        """,

    'description': """
        
    """,

    'author': "Li Haonan",
    'website': "http://www.e2yun.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'e2yun_customer_info', 'e2yun_crm_lead_extends', 'crm_lead_product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/customer_lost_reason.xml',
        #'views/templates.xml',
    ],
}